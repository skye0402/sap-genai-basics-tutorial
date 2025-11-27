"""05 – Complete Agentic AI example: Software License Procurement Agent.

This script shows a fully working LangGraph agent that:
- Uses tools to check software license availability (IT view)
- Uses tools to check team budget (Finance view)
- Decides whether a license request can be approved
- Prints an "audit log" of its reasoning steps

You will later derive a skeleton version of this for the hands-on exercise.
"""

import os
import operator
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from typing_extensions import Annotated, TypedDict

from gen_ai_hub.proxy.langchain.init_models import init_llm
from langchain.tools import tool
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage
from langgraph.graph import StateGraph, START, END


# ---------------------------------------------------------------------------
# Configuration & model
# ---------------------------------------------------------------------------

# Load shared configuration from repo root .env
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

MODEL = os.getenv("LLM_MODEL", "gpt-4.1")
MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "2000"))
TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0"))

# Initialize LLM via SAP Generative AI Hub helper
model = init_llm(MODEL, max_tokens=MAX_TOKENS, temperature=TEMPERATURE)


# ---------------------------------------------------------------------------
# Tools (IT + Finance)
# ---------------------------------------------------------------------------

@tool
def check_software_license(software_name: str) -> str:
    """Check if a license is available for the given software.

    This is a mocked implementation for the workshop. In a real scenario,
    this would query an internal IT inventory system.
    """

    name = software_name.strip().lower()
    if name in {"sap", "sap hana", "sap s/4hana"}:
        return "Available: we have spare SAP licenses."
    if name in {"adobe", "adobe cc", "adobe creative cloud"}:
        return "Out of stock: no Adobe licenses available."
    return f"Unknown availability for '{software_name}'. Assume not available."


@tool
def check_team_budget(team_name: str) -> str:
    """Check the remaining budget for a specific team.

    Mocked logic for the workshop. In reality this would query a Finance/ERP
    system for the cost center or team budget.
    """

    name = team_name.strip().lower()
    if name in {"it", "it team"}:
        return "Budget: 10000 USD remaining."
    if name in {"marketing", "marketing team"}:
        return "Budget: 100 USD remaining."
    if name in {"finance", "finance team"}:
        return "Budget: 5000 USD remaining."
    return f"Budget for team '{team_name}' is unknown. Treat as very low."


tools = [check_software_license, check_team_budget]
tools_by_name = {t.name: t for t in tools}
model_with_tools = model.bind_tools(tools)


# ---------------------------------------------------------------------------
# State definition
# ---------------------------------------------------------------------------


class MessagesState(TypedDict):
    """State passed between LangGraph nodes.

    - messages: conversation history + tool calls/results
    - llm_calls: how many times the LLM node has been called
    """

    messages: Annotated[list[AnyMessage], operator.add]
    llm_calls: int


# ---------------------------------------------------------------------------
# Nodes
# ---------------------------------------------------------------------------


def llm_call(state: MessagesState) -> MessagesState:
    """LLM decides whether to call a tool or answer the user.

    We prepend a system message that explains the agent's role:
    a software license procurement assistant that must consult both
    IT (license availability) and Finance (team budget) before deciding.
    """

    system = SystemMessage(
        content=(
            "You are a software license procurement assistant. "
            "For each request, you must:\n"
            "1) Check if the requested SOFTWARE has licenses available using tools.\n"
            "2) Check the TEAM budget using tools.\n"
            "Only approve the request if there is a license available AND the team has reasonable budget.\n"
            "Explain clearly why you approve or reject a request using the tool results."
        )
    )

    result = model_with_tools.invoke([system] + state["messages"])

    return {
        "messages": [result],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


def tool_node(state: MessagesState) -> MessagesState:
    """Execute the tools requested by the last LLM message."""

    last_msg = state["messages"][-1]
    tool_messages: list[ToolMessage] = []

    for tool_call in getattr(last_msg, "tool_calls", []) or []:
        tool = tools_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])
        tool_messages.append(
            ToolMessage(content=observation, tool_call_id=tool_call["id"])
        )

    return {"messages": tool_messages, "llm_calls": state.get("llm_calls", 0)}


def should_continue(state: MessagesState) -> Literal["tool_node", END]:
    """Route either to the tool node or end based on LLM output.

    - If the last AI message contains tool calls, we go to `tool_node`.
    - Otherwise we stop (and return the final answer to the user).
    - As a simple safety, if we already called the LLM many times in one
      run, we also stop.
    """

    messages = state["messages"]
    last_message = messages[-1]

    # Hard stop if too many LLM calls in a single interaction
    if state.get("llm_calls", 0) >= 5:
        return END

    if getattr(last_message, "tool_calls", None):
        return "tool_node"

    return END


# ---------------------------------------------------------------------------
# Build the agent graph
# ---------------------------------------------------------------------------


agent_builder = StateGraph(MessagesState)

agent_builder.add_node("llm_call", llm_call)
agent_builder.add_node("tool_node", tool_node)

agent_builder.add_edge(START, "llm_call")
agent_builder.add_conditional_edges("llm_call", should_continue, ["tool_node", END])
agent_builder.add_edge("tool_node", "llm_call")

agent = agent_builder.compile()


# ---------------------------------------------------------------------------
# Helper: Pretty-print the reasoning / audit log
# ---------------------------------------------------------------------------


def print_agent_thought_process(messages: list[AnyMessage]) -> None:
    """Print a simple audit trail of what the agent did.

    This is meant for workshop participants (including non-developers) to see
    when the agent decided to call tools and what they returned.
    """

    print("\n--- AGENT AUDIT LOG ---")
    for m in messages:
        msg_type = getattr(m, "type", None)
        if msg_type == "ai" and getattr(m, "tool_calls", None):
            first_call = m.tool_calls[0]
            print(f"[AGENT DECISION] Needs tool: {first_call['name']}")
            print(f"  Reasoning: {m.content}")
        elif msg_type == "tool":
            print(f"[TOOL RESULT] {m.content}")
        elif msg_type == "ai":
            print(f"[AGENT RESPONSE] {m.content}")
    print("-----------------------\n")


# ---------------------------------------------------------------------------
# Simple CLI entry point
# ---------------------------------------------------------------------------


def main() -> None:
    print("Software License Procurement Agent (complete demo)")
    print("Type an empty line or Ctrl+C to exit.\n")

    # Keep full conversation history across turns so the agent can
    # remember previous questions and answers.
    conversation: list[AnyMessage] = []

    while True:
        try:
            user_text = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not user_text:
            print("Goodbye.")
            break

        # Add the new user message to the ongoing conversation
        conversation.append(HumanMessage(content=user_text))

        # Invoke the agent with the full history
        state = agent.invoke({
            "messages": conversation,
            "llm_calls": 0,
        })
        msgs = state["messages"]

        # Update conversation with all messages produced in this turn
        conversation = msgs

        print_agent_thought_process(msgs)

        # Show final assistant message (last AI message)
        final_ai = [m for m in msgs if getattr(m, "type", None) == "ai"]
        if final_ai:
            print(f"Assistant: {final_ai[-1].content}\n")


if __name__ == "__main__":
    main()
