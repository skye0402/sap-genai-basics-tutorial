"""Exercise 06 — Speech Assistant (CLI).

Talk to gpt-realtime on SAP Generative AI Hub from your terminal. The
assistant replies in whatever language you just spoke. Speak English,
get English back. Speak Japanese, get Japanese back.

Run from this folder:
    uv sync
    uv run main.py

Stop with Ctrl+C.

The auth + WebSocket setup follows the same pattern as the other
exercises in this repo: read AICORE_* from the shared .env at repo
root. On top of that we capture the microphone and play back the
model's voice using sounddevice (PortAudio).

Headphones are strongly recommended — without them the mic will pick
up the assistant's own voice and barge in on itself.
"""

from __future__ import annotations

import asyncio
import base64
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import requests
import sounddevice as sd
import tzlocal
import websockets
from dotenv import load_dotenv


# Load the shared repo-root .env, same convention as 01-..05-.
load_dotenv(Path(__file__).resolve().parents[1] / ".env")


# --------------------------------------------------------------------------- #
#  Constants
# --------------------------------------------------------------------------- #

# Public default for the SAP-hosted gpt-realtime deployment. Override via
# AICORE_REALTIME_DEPLOYMENT_URL in .env if you have your own deployment.
DEFAULT_DEPLOYMENT_URL = (
    "wss://realtime.ai.prod.ap-northeast-1.aws.ml.hana.ondemand.com"
    "/v2/inference/deployments/d38437dd056459a0"
)
DEFAULT_MODEL_NAME = "gpt-realtime"

SAMPLE_RATE_HZ = 24_000  # OpenAI realtime pcm16 default
MIC_BLOCK_MS = 40        # how often we hand a chunk to the WebSocket
MIC_BLOCK_FRAMES = SAMPLE_RATE_HZ * MIC_BLOCK_MS // 1000


# --------------------------------------------------------------------------- #
#  Auth
# --------------------------------------------------------------------------- #


def get_token() -> str:
    """Exchange client_id/secret for a short-lived bearer token."""
    auth_url = os.environ["AICORE_AUTH_URL"]
    if not auth_url.endswith("/oauth/token"):
        auth_url = auth_url.rstrip("/") + "/oauth/token"
    resp = requests.post(
        auth_url,
        data={"grant_type": "client_credentials"},
        auth=(os.environ["AICORE_CLIENT_ID"], os.environ["AICORE_CLIENT_SECRET"]),
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


# --------------------------------------------------------------------------- #
#  Conversation
# --------------------------------------------------------------------------- #


def _local_time_zone() -> ZoneInfo:
    """Return the OS-configured local time zone as a ZoneInfo.

    `tzlocal` is the right way to do this on Windows. The standard
    library's `time.tzname` returns display names like "Tokyo Standard
    Time" which aren't valid IANA identifiers; tzlocal does the
    Windows-name -> IANA-name mapping for us.
    """
    try:
        return tzlocal.get_localzone()
    except Exception:  # noqa: BLE001
        # Last-resort fallback: UTC. The model will still work, it just
        # won't know to greet "good evening" at the user's actual hour.
        return ZoneInfo("UTC")


def build_system_instructions() -> str:
    """Build the system prompt fresh at session start.

    We bake the current date/time and the OS-detected time zone into the
    prompt so the model can:
      - answer date/time questions truthfully (we know the model has no
        clock of its own that we can rely on),
      - greet the user with the right time-of-day phrase ("good morning"
        vs "good evening" vs the equivalent in any other language).
    """
    tz = _local_time_zone()
    now = datetime.now(tz)
    # Example: "Saturday, June 14, 2026 at 20:34 (Asia/Tokyo, UTC+09:00)"
    pretty = now.strftime("%A, %B %d, %Y at %H:%M")
    iso = now.isoformat(timespec="seconds")
    tz_name = str(tz)
    utc_offset = now.strftime("%z")
    utc_offset_fmt = f"{utc_offset[:3]}:{utc_offset[3:]}" if utc_offset else ""

    return (
        f"The current local date and time is: {pretty} "
        f"({tz_name}, UTC{utc_offset_fmt}). "
        f"ISO-8601: {iso}. "
        "Use this when the user asks about the date, time, day of the "
        "week, or anything time-relative. Do not claim you don't know "
        "the time — you do, it's right here.\n\n"
        "GREETING RULE: At the very start of the conversation (your first "
        "spoken turn only), greet the user with a time-of-day-appropriate "
        "phrase based on the local hour above:\n"
        "  - 05:00–11:59 -> 'good morning'\n"
        "  - 12:00–17:59 -> 'good afternoon'\n"
        "  - 18:00–21:59 -> 'good evening'\n"
        "  - 22:00–04:59 -> 'hello' (don't wish them goodnight; they're "
        "obviously still awake)\n"
        "Use the equivalent phrase in whatever language the user speaks "
        "first. For Japanese: おはようございます / こんにちは / こんばんは. "
        "For German: Guten Morgen / Guten Tag / Guten Abend. "
        "For French: Bonjour / Bon après-midi / Bonsoir. And so on for "
        "any other language. Then briefly invite them to talk.\n\n"
        "You are a friendly, concise voice assistant. "
        "ALWAYS reply in the same language the user just spoke. "
        "If the user speaks English, reply in English. "
        "If the user speaks Japanese, reply in Japanese. "
        "If the user switches languages mid-conversation, follow them on the "
        "next turn. Keep replies short — one or two sentences unless the user "
        "asks for more.\n\n"
        "If the user clearly indicates they want to end the conversation "
        "(for example: 'I'm done', 'goodbye', 'bye', 'exit', 'quit', 'stop', "
        "'I want to finish', 'that's all', or the equivalent in any other "
        "language), do BOTH of the following: "
        "(1) say a short farewell out loud in the same language the user used, "
        "(2) call the `exit_app` tool. "
        "Do not call `exit_app` for casual phrases like 'thanks' or 'cool' — "
        "only when the user actually wants to leave."
    )


# Tool schema we declare to the model. The model invokes it via a normal
# function-call event; we intercept it on the WebSocket reader side and
# treat it as a signal to shut down.
EXIT_TOOL_SCHEMA = {
    "type": "function",
    "name": "exit_app",
    "description": (
        "Call this when the user wants to end the conversation. Always "
        "say a short spoken farewell in the same turn before calling it."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "reason": {
                "type": "string",
                "description": (
                    "A short note on why you are exiting (e.g. 'user said bye')."
                ),
            },
        },
        "required": [],
        "additionalProperties": False,
    },
}


async def run_assistant() -> int:
    token = get_token()
    print("[auth] got token")
    resource_group = os.environ["AICORE_RESOURCE_GROUP"]
    deployment_url = os.environ.get(
        "AICORE_REALTIME_DEPLOYMENT_URL", DEFAULT_DEPLOYMENT_URL,
    )
    model_name = os.environ.get("AICORE_REALTIME_MODEL", DEFAULT_MODEL_NAME)

    url = f"{deployment_url}/v1/realtime?model={model_name}"
    headers = {
        "Authorization": f"Bearer {token}",
        "AI-Resource-Group": resource_group,
    }

    # Queue of pcm16 byte-chunks the model has streamed back. Filled by the
    # WebSocket reader, drained by the speaker playback task.
    playback_q: asyncio.Queue = asyncio.Queue(maxsize=128)
    loop = asyncio.get_running_loop()

    # Half-duplex gate: while the assistant is speaking (or for a short
    # tail after), drop mic frames before sending them upstream. Without
    # this and without headphones, the speaker output bleeds back into
    # the mic and the server-side VAD treats it as the user talking,
    # causing the assistant to reply to itself in a loop.
    # Wrapped in a one-element list so the inner functions can reassign.
    mic_muted_until = [0.0]  # monotonic seconds; mic muted while now < this
    MIC_TAIL_S = 0.4         # keep mic muted this long after audio stops

    # Set when the model calls the `exit_app` tool. The WS reader stops the
    # loop on the next `response.done` so the farewell audio finishes first.
    exit_requested = [False]

    async with websockets.connect(
        url,
        additional_headers=headers,
        max_size=8 * 1024 * 1024,
        open_timeout=30,
        ping_interval=20,
        ping_timeout=60,
    ) as ws:
        print("[ws] connected")

        # Configure session: audio in + audio out at 24 kHz PCM16, server-VAD
        # so the model decides when our turn has ended, plus the system prompt
        # that pins the reply language to the user's input language.
        await ws.send(json.dumps({
            "type": "session.update",
            "session": {
                "type": "realtime",
                "model": model_name,
                "output_modalities": ["audio"],
                "instructions": build_system_instructions(),
                "tools": [EXIT_TOOL_SCHEMA],
                "tool_choice": "auto",
                "audio": {
                    "input": {
                        "format": {"type": "audio/pcm", "rate": SAMPLE_RATE_HZ},
                        "turn_detection": {
                            "type": "server_vad",
                            # Higher threshold + longer silence: forces the
                            # VAD to wait for a clear, sustained voice before
                            # opening a turn. This is what stops the assistant
                            # from re-triggering on its own faint speaker
                            # bleed-through when you don't have headphones.
                            "threshold": 0.8,
                            "prefix_padding_ms": 300,
                            "silence_duration_ms": 800,
                        },
                    },
                    "output": {
                        "format": {"type": "audio/pcm", "rate": SAMPLE_RATE_HZ},
                        "voice": "alloy",
                    },
                },
            },
        }))

        print("[mic] listening — just start talking. Ctrl+C to quit.")

        # ----- MIC CAPTURE ---------------------------------------------------
        # sounddevice's InputStream callback runs on a PortAudio thread, so we
        # bounce blocks back to the asyncio loop via call_soon_threadsafe and
        # an asyncio.Queue.
        mic_q: asyncio.Queue = asyncio.Queue(maxsize=64)

        def on_mic(indata: np.ndarray, frames: int, time_info, status) -> None:
            if status:
                # Underruns/overflows aren't fatal; just note them.
                print(f"[mic] {status}", file=sys.stderr)
            # indata is float32 in [-1, 1]; convert to int16 little-endian.
            pcm16 = (np.clip(indata[:, 0], -1.0, 1.0) * 32767).astype("<i2").tobytes()
            try:
                loop.call_soon_threadsafe(mic_q.put_nowait, pcm16)
            except asyncio.QueueFull:
                # We're behind on uploading; drop this block rather than
                # block PortAudio.
                pass

        async def pump_mic_to_ws() -> None:
            while True:
                chunk = await mic_q.get()
                # Drop mic frames while the assistant is speaking. This is
                # the half-duplex "echo cancel for the lazy" — it keeps
                # speaker bleed-through out of the input buffer.
                if time.monotonic() < mic_muted_until[0]:
                    continue
                await ws.send(json.dumps({
                    "type": "input_audio_buffer.append",
                    "audio": base64.b64encode(chunk).decode("ascii"),
                }))

        # ----- WS READER -----------------------------------------------------
        async def read_ws() -> None:
            current_transcript: list[str] = []
            async for raw in ws:
                if isinstance(raw, bytes):
                    continue
                try:
                    evt = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                t = evt.get("type", "")

                if t in ("response.output_audio.delta", "response.audio.delta"):
                    b64 = evt.get("delta") or evt.get("audio") or ""
                    if b64:
                        chunk_bytes = base64.b64decode(b64)
                        # Mute the mic for the duration of this chunk plus a
                        # short tail, so we don't pick up our own voice.
                        chunk_seconds = len(chunk_bytes) / 2 / SAMPLE_RATE_HZ
                        mic_muted_until[0] = max(
                            mic_muted_until[0],
                            time.monotonic() + chunk_seconds + MIC_TAIL_S,
                        )
                        await playback_q.put(chunk_bytes)

                elif t in (
                    "response.output_audio_transcript.delta",
                    "response.audio_transcript.delta",
                ):
                    current_transcript.append(evt.get("delta") or "")

                elif t in (
                    "response.output_audio_transcript.done",
                    "response.audio_transcript.done",
                ):
                    text = "".join(current_transcript).strip()
                    current_transcript.clear()
                    if text:
                        print(f"[assistant] {text}")

                elif t == "conversation.item.input_audio_transcription.completed":
                    user_text = (evt.get("transcript") or "").strip()
                    if user_text:
                        print(f"[you] {user_text}")

                elif t == "input_audio_buffer.speech_started":
                    # User started talking — flush any half-played reply so we
                    # don't talk over each other on barge-in.
                    while not playback_q.empty():
                        try:
                            playback_q.get_nowait()
                            playback_q.task_done()
                        except asyncio.QueueEmpty:
                            break

                elif t == "response.output_item.done":
                    # The model emits one of these for each output item it
                    # produced this turn. We watch for our exit tool.
                    item = evt.get("item") or {}
                    if (
                        item.get("type") == "function_call"
                        and item.get("name") == "exit_app"
                    ):
                        reason = ""
                        try:
                            args = json.loads(item.get("arguments") or "{}")
                            reason = args.get("reason") or ""
                        except json.JSONDecodeError:
                            pass
                        print(f"[exit] model called exit_app{f': {reason}' if reason else ''}")
                        exit_requested[0] = True

                elif t == "response.done":
                    # If the model asked to exit and the farewell-generating
                    # turn just finished, wait for the speaker to finish
                    # playing what's already queued, then stop the WS loop.
                    if exit_requested[0]:
                        await playback_q.join()
                        # Small tail so the audio device actually flushes
                        # the last buffer before the stream is torn down.
                        await asyncio.sleep(0.3)
                        return

                elif t == "error":
                    print(f"[ERROR] {json.dumps(evt, indent=2)}", file=sys.stderr)

        # ----- SPEAKER PLAYBACK ----------------------------------------------
        # OutputStream.write is blocking; run it in a thread so it doesn't
        # stall the event loop while a long sentence plays.
        async def play_speaker() -> None:
            with sd.OutputStream(
                samplerate=SAMPLE_RATE_HZ,
                channels=1,
                dtype="int16",
                blocksize=0,
            ) as out:
                while True:
                    chunk = await playback_q.get()
                    try:
                        if chunk is None:
                            return
                        arr = np.frombuffer(chunk, dtype="<i2")
                        await asyncio.to_thread(out.write, arr)
                    finally:
                        # Pair with task_done so playback_q.join() works
                        # when we wait for the farewell to finish.
                        playback_q.task_done()

        # ----- ARM EVERYTHING ------------------------------------------------
        with sd.InputStream(
            samplerate=SAMPLE_RATE_HZ,
            channels=1,
            dtype="float32",
            blocksize=MIC_BLOCK_FRAMES,
            callback=on_mic,
        ):
            tasks = [
                asyncio.create_task(pump_mic_to_ws(), name="mic->ws"),
                asyncio.create_task(read_ws(),       name="ws-reader"),
                asyncio.create_task(play_speaker(),  name="speaker"),
            ]
            try:
                # FIRST_COMPLETED so a clean return from read_ws() (which
                # happens on the exit_app tool flow) ends the wait and the
                # finally block cancels the other two tasks.
                done, _pending = await asyncio.wait(
                    tasks, return_when=asyncio.FIRST_COMPLETED,
                )
                for t in done:
                    exc = t.exception()
                    if exc:
                        raise exc
            finally:
                for t in tasks:
                    t.cancel()
                await asyncio.gather(*tasks, return_exceptions=True)

    return 0


def main() -> int:
    required = [
        "AICORE_CLIENT_ID",
        "AICORE_CLIENT_SECRET",
        "AICORE_AUTH_URL",
        "AICORE_RESOURCE_GROUP",
    ]
    missing = [k for k in required if not os.environ.get(k)]
    if missing:
        print(f"ERROR: missing env vars: {missing}", file=sys.stderr)
        print("       expected in the repo-root .env", file=sys.stderr)
        return 2
    try:
        return asyncio.run(run_assistant())
    except KeyboardInterrupt:
        print("\n[bye]")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
