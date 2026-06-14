# 06 - Speech Assistant (CLI, multilingual)

A tiny command-line voice demo. You speak, the AI replies — in whatever language you spoke. Speak English, get English back. Speak Japanese, get Japanese back. Same for German, French, Spanish, Mandarin, etc.

This is the simplest possible end-to-end use of `gpt-realtime` on SAP Generative AI Hub: no web server, no browser, no LangChain. The CLI opens its own WebSocket directly to the deployment, captures your microphone through PortAudio, and plays the model's voice straight back through your speakers.

## What this example does

- Uses the **same `.env` at repo root** as `01`–`05` (`AICORE_*` keys).
- Authenticates with **OAuth client_credentials** to get a bearer token.
- Opens a **WebSocket** to a `gpt-realtime` deployment on SAP AI Core.
- Captures the microphone with **`sounddevice`** at 24 kHz mono PCM16.
- Streams audio up as `input_audio_buffer.append` events.
- Lets the model do **server-side voice-activity detection** so you don't need a push-to-talk key — just talk.
- Plays back `response.output_audio.delta` chunks through the speakers.
- Pins the **reply language to your input language** via the system prompt.
- **Knows the local date, time, and time zone** — the prompt is built fresh at session start with `datetime.now(tzlocal.get_localzone())`, so the model can answer time questions accurately and greet you with "good morning" / "おはようございます" / "Guten Abend" depending on the local hour.
- Prints `[you] ...` and `[assistant] ...` transcripts as they stream.

## Prerequisites

1. The same `.env` the other exercises use (one folder up). The realtime exercise reads:
   - `AICORE_AUTH_URL`
   - `AICORE_CLIENT_ID`
   - `AICORE_CLIENT_SECRET`
   - `AICORE_RESOURCE_GROUP`
   - `AICORE_REALTIME_DEPLOYMENT_URL` *(optional — defaults to a public SAP-hosted `gpt-realtime` deployment)*
   - `AICORE_REALTIME_MODEL` *(optional — defaults to `gpt-realtime`)*

2. **PortAudio** installed locally (sounddevice's backend):
   - **Windows:** ships in the wheel — nothing extra to do.
   - **macOS:** `brew install portaudio`
   - **Linux:** `sudo apt install libportaudio2`

3. **A microphone and headphones.** Headphones strongly recommended — without them the mic will pick up the assistant's own voice and barge in on itself.

## Run it

```bash
cd 06-speech-assistant
uv sync
uv run main.py
```

You'll see:

```
[auth] got token
[ws] connected
[mic] listening — just start talking. Ctrl+C to quit.
```

Now just talk. The server-side VAD decides when you've finished a sentence, the model replies, and you hear it through your speakers. Then keep going — it's a continuous conversation. Stop with `Ctrl+C`.

## Controls

- Just talk — server-side VAD detects when you're done.
- **To exit politely:** say something like "I'm done", "goodbye", "exit", "I want to finish", or the equivalent in any other language. The model will say a short farewell and then call the `exit_app` tool, which shuts the script down cleanly.
- **To force-quit:** `Ctrl+C`.

## How it works

```
   mic  ──►  sounddevice InputStream  ──►  pcm16 chunks
                                            │
                                            ▼
                                   input_audio_buffer.append
                                            │
                                            ▼
                       ┌──────────────────────────────────┐
                       │  gpt-realtime on SAP AI Core     │
                       │  (server-side VAD detects turns) │
                       └──────────────────────────────────┘
                                            │
                                            ▼
                              response.output_audio.delta
                                            │
                                            ▼
   speakers  ◄──  sounddevice OutputStream  ◄──  pcm16 chunks
```

Three things to notice in `main.py`:

1. **Auth** — OAuth client-credentials, identical pattern to what the other exercises do under the hood, just done explicitly here so you can see it.
2. **Session config** — asks for `audio` modality both ways at 24 kHz PCM16, turns on `server_vad`, and sets the system prompt that tells the model to mirror the user's language.
3. **Three concurrent asyncio tasks:**
   - one streams mic frames into `input_audio_buffer.append`,
   - one reads events from the WebSocket and queues audio deltas for playback,
   - one drains that queue into the speaker output stream.

## What's new compared to 01–05

- All previous exercises send **text** to a chat-completion model (LangChain, gen-ai-hub SDK). This one sends **audio in real time** over a long-lived **WebSocket**.
- Instead of `init_llm(...)`, you do the OAuth dance yourself and connect to a Realtime deployment directly. It's a different shape of API and worth seeing once.
- There's no `history = [...]` you have to manage in Python — the server keeps conversation state for the duration of the WebSocket.

## Things to try

- **Switch language mid-conversation.** Say something in English, then switch to Japanese on your next turn — the assistant should follow.
- **Change the voice** in `main.py` (`alloy`, `echo`, `shimmer`, …).
- **Tune the VAD** by lowering `silence_duration_ms` to make the model interrupt you faster, or raising it to give you more thinking time.
- **Give it a persona.** Edit `SYSTEM_INSTRUCTIONS` to make the assistant a grumpy pirate, a helpful librarian, a tour guide for Tokyo, etc.
- **Add input transcription.** Add `"transcription": {"model": "whisper-1"}` under `audio.input` in the session config to see your own words printed via `conversation.item.input_audio_transcription.completed` (the code already handles that event).
- **Add another tool.** The exit-by-voice feature (`exit_app`) shows the basic shape of a function-call tool over the Realtime API: schema in `session.update`, intercept `response.output_item.done` with `item.type == "function_call"` in the WS reader. Try adding e.g. a `change_voice` tool that swaps the assistant voice mid-session, or a `set_persona` tool.

## Troubleshooting

- **No audio plays.** Check your default output device. `python -c "import sounddevice as sd; print(sd.query_devices())"` lists devices; set `sd.default.device = (in_idx, out_idx)` in `main.py` before opening streams if you need to pick specific ones.
- **The model talks over itself / hears itself.** Use headphones. The script also includes a half-duplex gate that mutes the mic while the assistant is speaking (plus a 400ms tail) so this works without headphones too — but if you still see the assistant looping replies, your mic is louder than the gate's tail can cover. Either lower speaker volume, raise `MIC_TAIL_S` in `main.py`, or raise the `threshold` in the VAD config (currently `0.8`) toward `0.95`.
- **`OSError: PortAudio library not found`** on Linux — install `libportaudio2` (see Prerequisites).
- **`401`/`403` on connect.** Your `.env` is missing or the credentials don't have access to the realtime deployment. Confirm `AICORE_*` is what `01-hello-world` uses; if it works there but not here, your tenant doesn't have a `gpt-realtime` deployment and you'll need to set `AICORE_REALTIME_DEPLOYMENT_URL` to one that does.
