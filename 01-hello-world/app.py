"""01-hello-world — same idea as main.py, but with a Gradio Blocks UI.

Read main.py first — it's the simplest possible call to SAP Generative AI Hub
(one prompt, one reply, ~25 lines). This file is the same idea wrapped in a
browser UI so the demo looks nicer (Unicode renders properly, the model + its
metadata are visible side by side, etc.). All the visual styling lives in
sap_ui.py so this file can stay focused on the SDK call.

Run from this folder:
    uv sync
    uv run python app.py

A browser tab opens at http://127.0.0.1:7860. Press Ctrl+C to stop.
"""

from __future__ import annotations

import os
from pathlib import Path

import gradio as gr
from dotenv import load_dotenv
from gen_ai_hub.proxy.langchain.init_models import init_llm
from langchain_core.messages import HumanMessage, SystemMessage

# All visual styling (theme, header, CSS overrides) is in sap_ui.py. Keeps
# this file focused on the LLM call, not on colors.
from sap_ui import sap_theme, CUSTOM_CSS, header_html, section_heading


# Same .env-from-repo-root convention main.py uses.
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

DEFAULT_MODEL = os.getenv("LLM_MODEL", "gpt-4.1")
DEFAULT_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "5000"))
DEFAULT_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))
DEFAULT_SYSTEM_PROMPT = os.getenv(
    "LLM_SYSTEM_PROMPT", "You are a helpful assistant.",
)


# --------------------------------------------------------------------------- #
#  THE TEACHING POINT — one call, structured response back
# --------------------------------------------------------------------------- #
#
# Same shape as main.py: build a list of messages, hand them to llm.invoke(),
# get back an AIMessage. The AIMessage carries:
#   - .content              the reply text
#   - .response_metadata    model id, finish reason, system fingerprint, ...
#   - .usage_metadata       input / output / total token counts
# We surface all three in the UI below so learners can see what an LLM call
# actually returns, not just the text.


def call_llm(
    user_prompt: str,
    system_prompt: str,
    temperature: float,
    max_tokens: int,
) -> tuple[str, dict]:
    """Make one call to SAP Generative AI Hub. Return (reply_text, raw_dict)."""
    if not user_prompt.strip():
        return "", {"info": "Type a prompt and press Send."}

    llm = init_llm(
        DEFAULT_MODEL,
        max_tokens=int(max_tokens),
        temperature=float(temperature),
    )
    messages = [
        SystemMessage(content=system_prompt or DEFAULT_SYSTEM_PROMPT),
        HumanMessage(content=user_prompt),
    ]

    response = llm.invoke(messages)

    raw = {
        "content": getattr(response, "content", str(response)),
        "id": getattr(response, "id", None),
        "response_metadata": getattr(response, "response_metadata", None) or {},
        "usage_metadata": getattr(response, "usage_metadata", None) or {},
        "type": getattr(response, "type", None),
    }
    return raw["content"], raw


# --------------------------------------------------------------------------- #
#  Gradio Blocks UI
# --------------------------------------------------------------------------- #


def build_ui() -> gr.Blocks:
    with gr.Blocks(title="01 · Hello World — SAP Gen AI Hub") as demo:
        gr.HTML(header_html(
            "SAP Generative AI Hub · Hello World",
            "Send a single prompt, see the structured reply.",
        ))

        with gr.Row():
            # ---- LEFT: config sidebar ----
            with gr.Column(scale=1, min_width=280):
                section_heading("Configuration")
                gr.Textbox(
                    label="Model",
                    value=DEFAULT_MODEL,
                    interactive=False,
                    info="Set via LLM_MODEL in the repo-root .env",
                )
                temperature = gr.Slider(
                    label="Temperature",
                    minimum=0.0, maximum=2.0, step=0.05,
                    value=DEFAULT_TEMPERATURE,
                    info="Higher = more creative",
                )
                max_tokens = gr.Slider(
                    label="Max output tokens",
                    minimum=50, maximum=20_000, step=50,
                    value=DEFAULT_MAX_TOKENS,
                )
                system_prompt = gr.Textbox(
                    label="System prompt",
                    value=DEFAULT_SYSTEM_PROMPT,
                    lines=4,
                )

            # ---- RIGHT: prompt + reply + raw response ----
            with gr.Column(scale=2):
                section_heading("Your prompt")
                user_prompt = gr.Textbox(
                    label="",
                    placeholder="e.g. Tell me a haiku about Tokyo.",
                    lines=4,
                    autofocus=True,
                )
                with gr.Row():
                    send = gr.Button("Send", variant="primary")
                    clear = gr.Button("Clear", variant="secondary")

                section_heading("Reply")
                reply = gr.Markdown(value="", line_breaks=True)

                # Teaching panel: an LLM call doesn't just return text — it
                # returns a structured payload with token counts and other
                # metadata. Talk through `usage_metadata` (input / output /
                # total tokens) and `response_metadata` (model id, finish
                # reason, system fingerprint) during the demo.
                section_heading("Raw response from the LLM")
                with gr.Accordion(
                    "Show full structured response (JSON)", open=True,
                ):
                    raw_response = gr.JSON(
                        label="AIMessage payload",
                        value={"info": "Send a prompt to see the full response here."},
                    )

        # Wire up: Send button, Enter in the prompt box, and Clear.
        send.click(
            fn=call_llm,
            inputs=[user_prompt, system_prompt, temperature, max_tokens],
            outputs=[reply, raw_response],
        )
        user_prompt.submit(
            fn=call_llm,
            inputs=[user_prompt, system_prompt, temperature, max_tokens],
            outputs=[reply, raw_response],
        )
        clear.click(
            fn=lambda: ("", "", {"info": "Send a prompt to see the full response here."}),
            inputs=None,
            outputs=[user_prompt, reply, raw_response],
        )

    return demo


def main() -> None:
    demo = build_ui()
    # `theme` and `css` go on launch() in Gradio 6+ (they used to live on Blocks).
    demo.launch(
        theme=sap_theme(),
        css=CUSTOM_CSS,
        inbrowser=True,
        share=False,
    )


if __name__ == "__main__":
    main()
