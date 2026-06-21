"""SAP Joule / AI Design styling for Gradio Blocks demos.

This module is the *visual* layer for the workshop UIs. Each exercise's
`app.py` imports from here and stays focused on its own teaching content
(the SDK call, the data flow) without the theme noise.

Reused by:
  - 01-hello-world/app.py
  - (in future) 02-cli-chat/app.py, ...

Public surface:
    sap_theme()              -> a gr.themes.Soft instance with SAP/Joule colors
    CUSTOM_CSS               -> CSS string with the targeted overrides we need
                                 on top of the theme
    header_html(title, sub)  -> the gradient header band with the Joule diamond
    section_heading(text)    -> a gr.HTML column-heading legible on the gradient

Inspired by the SAP Joule / "Composing the moment" brand visuals: a deep
navy-to-violet gradient body, white floating cards, primary actions in
classic SAP blue, AI accents in Joule violet, with a magenta-pink spark
highlight.
"""

from __future__ import annotations

import gradio as gr


# --------------------------------------------------------------------------- #
#  Color palette (eyeballed from SAP AI / Joule reference visuals)
# --------------------------------------------------------------------------- #

JOULE_NAVY        = "#0A0B3D"  # deepest gradient stop (top-left)
JOULE_INDIGO      = "#1F1B5C"  # mid gradient stop
JOULE_VIOLET      = "#5D3FD3"  # AI accent / brighter gradient stop
JOULE_LILAC       = "#9B7CFF"  # soft accent (icons, hover, links)
JOULE_PINK        = "#D770FF"  # spark / highlight accent
SAP_BLUE          = "#0064D9"  # primary button
SAP_BLUE_DARK     = "#0040A8"  # primary hover
SAP_BLUE_LIGHT    = "#A6C8FF"
TEXT_ON_DARK      = "#F5F5FA"
TEXT_ON_LIGHT     = "#1B1D1F"
SURFACE           = "#FFFFFF"
SURFACE_ALT       = "#F4F0FF"  # subtle AI-tinted surface (lavender)


# --------------------------------------------------------------------------- #
#  Theme builder
# --------------------------------------------------------------------------- #


def sap_theme() -> gr.themes.Base:
    """SAP-blue primary, Joule-violet secondary, dark gradient body."""
    sap_blue = gr.themes.Color(
        name="sap_blue",
        c50="#E6F0FF",  c100=SAP_BLUE_LIGHT, c200="#7FAEFF",
        c300="#5494FF", c400="#2A7AFF",      c500=SAP_BLUE,
        c600="#0050B8", c700=SAP_BLUE_DARK,  c800="#002F7C",
        c900="#001E54", c950="#001230",
    )
    joule_violet = gr.themes.Color(
        name="joule_violet",
        c50="#F1ECFF",  c100="#DCD0FF",  c200="#BFA8FF",
        c300=JOULE_LILAC, c400="#7E5FFF", c500=JOULE_VIOLET,
        c600="#4A2DBF", c700="#3A22A0",  c800="#2A1880",
        c900=JOULE_INDIGO, c950=JOULE_NAVY,
    )

    gradient = (
        f"linear-gradient(135deg, {JOULE_NAVY} 0%, "
        f"{JOULE_INDIGO} 45%, {JOULE_VIOLET} 100%)"
    )

    return gr.themes.Soft(
        primary_hue=sap_blue,
        secondary_hue=joule_violet,
        neutral_hue=gr.themes.colors.slate,
        font=[gr.themes.GoogleFont("Inter"), "system-ui", "sans-serif"],
    ).set(
        body_background_fill=gradient,
        body_background_fill_dark=gradient,
        # IMPORTANT: keep body_text_color at the default. Inputs inherit from
        # it — forcing it to white-for-the-dark-bg makes input text white-on-
        # white inside our cards. We render text-on-the-gradient via inline
        # `gr.HTML` blocks instead.
        block_background_fill=SURFACE,
        block_background_fill_dark=SURFACE,
        block_label_background_fill=SURFACE,
        block_label_text_color=TEXT_ON_LIGHT,
        block_title_text_color=TEXT_ON_LIGHT,
        block_info_text_color="#5A5F6B",
        block_border_width="0px",
        block_radius="12px",
        block_shadow="0 6px 24px rgba(10, 11, 61, 0.25)",
        input_background_fill=SURFACE_ALT,
        input_background_fill_dark=SURFACE_ALT,
        input_border_color="#E1D7FF",
        input_border_color_focus=JOULE_VIOLET,
        button_primary_background_fill=SAP_BLUE,
        button_primary_background_fill_hover=SAP_BLUE_DARK,
        button_primary_text_color="#FFFFFF",
        button_secondary_background_fill="#FFFFFF",
        button_secondary_background_fill_hover=SURFACE_ALT,
        button_secondary_text_color=JOULE_VIOLET,
        button_secondary_border_color=JOULE_VIOLET,
    )


# --------------------------------------------------------------------------- #
#  Targeted CSS overrides
# --------------------------------------------------------------------------- #
#
# Things the theme system can't reach reliably:
#   - input/textarea text color (selection styling collides with white text)
#   - <details>/<summary> color (accordion title)
#   - small icon controls that default to neutral-light and disappear on
#     white surfaces (number-input spinner buttons, accordion chevron,
#     copy buttons on JSON / Code / Textbox)

CUSTOM_CSS = f"""
/* Inputs & textareas inside cards — keep text dark on the lavender fill. */
.gradio-container input[type="text"],
.gradio-container input[type="number"],
.gradio-container textarea {{
    color: {TEXT_ON_LIGHT} !important;
    caret-color: {TEXT_ON_LIGHT};
}}
.gradio-container input::placeholder,
.gradio-container textarea::placeholder {{
    color: #8A8FA0 !important;
}}

/* Selected text: light lilac background with dark text, so highlights
   never disappear against the browser's default blue selection. */
.gradio-container ::selection {{
    background: #DCD0FF;
    color: {TEXT_ON_LIGHT};
}}

/* Accordion title / summary: pin to dark so it's legible on the white card. */
.gradio-container .label-wrap,
.gradio-container .label-wrap span,
.gradio-container details > summary,
.gradio-container details > summary span {{
    color: {TEXT_ON_LIGHT} !important;
}}

/* Small icon controls (number-input arrows, accordion chevron, copy buttons,
   etc). Gradio paints these in --color-text-secondary which is neutral-400
   on white -- effectively invisible. We pin them to the Joule violet so
   they're discoverable without having to hover. */
.gradio-container svg[class*="chevron"],
.gradio-container button[aria-label*="opy" i] svg,
.gradio-container button[aria-label*="lear" i] svg,
.gradio-container details > summary svg,
.gradio-container .number-input button,
.gradio-container input[type="number"]::-webkit-inner-spin-button,
.gradio-container input[type="number"]::-webkit-outer-spin-button {{
    color: {JOULE_VIOLET} !important;
    fill: {JOULE_VIOLET} !important;
    opacity: 1 !important;
}}
/* Up/down arrow stacks Gradio renders next to number inputs */
.gradio-container .icon-button,
.gradio-container .icon-button svg {{
    color: {JOULE_VIOLET} !important;
    fill: {JOULE_VIOLET} !important;
    opacity: 1 !important;
}}

/* JSON viewer base color (keys/strings keep their syntax highlight). */
.gradio-container .json-holder {{
    color: {TEXT_ON_LIGHT};
}}
"""


# --------------------------------------------------------------------------- #
#  Reusable HTML helpers
# --------------------------------------------------------------------------- #


def header_html(title: str, subtitle: str = "") -> str:
    """Gradient header band with the Joule diamond logo + magenta dotted accent.

    Pass to `gr.HTML(header_html("My demo", "subtitle goes here"))`.
    """
    sub = (
        f'<div style="opacity: 0.85; font-size: 13px; margin-top: 2px;">'
        f'{subtitle}</div>' if subtitle else ''
    )
    return f"""
    <div style="
        background: linear-gradient(135deg, {JOULE_NAVY} 0%, {JOULE_INDIGO} 45%, {JOULE_VIOLET} 100%);
        color: {TEXT_ON_DARK};
        padding: 18px 24px;
        border-radius: 14px;
        margin-bottom: 18px;
        display: flex;
        align-items: center;
        gap: 16px;
        box-shadow: 0 8px 28px rgba(10, 11, 61, 0.35);
    ">
      <div style="
          width: 44px; height: 44px;
          background: #FFFFFF;
          border-radius: 10px;
          display: flex; align-items: center; justify-content: center;
          box-shadow: 0 2px 8px rgba(0,0,0,0.18);
      ">
        <div style="
            width: 22px; height: 22px;
            background: linear-gradient(135deg, {JOULE_VIOLET} 0%, {JOULE_LILAC} 100%);
            transform: rotate(45deg);
            border-radius: 4px;
            box-shadow: inset -2px -2px 4px rgba(0,0,0,0.12);
        "></div>
      </div>
      <div style="flex: 1;">
        <div style="font-size: 19px; font-weight: 600; letter-spacing: 0.2px;">
          {title}
        </div>
        {sub}
        <div style="
            margin-top: 10px;
            height: 2px;
            background-image: radial-gradient(circle, {JOULE_PINK} 1px, transparent 1.4px);
            background-size: 8px 2px;
            background-repeat: repeat-x;
            opacity: 0.85;
        "></div>
      </div>
    </div>
    """


def section_heading(text: str) -> None:
    """A column-heading rendered as inline-styled HTML, legible on the dark body.

    Call inside a `with gr.Blocks(...)` / `with gr.Column(...)` context — it
    inserts a `gr.HTML` block.
    """
    gr.HTML(f"""
    <div style="
        color: {TEXT_ON_DARK};
        font-size: 16px;
        font-weight: 600;
        letter-spacing: 0.2px;
        margin: 8px 0 4px 2px;
    ">{text}</div>
    """)
