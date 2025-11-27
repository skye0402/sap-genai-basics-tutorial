# 05 – Agent Graph (Complete Demo)

This folder contains a **complete, working example** of an agent built with LangGraph.
The agent acts as a **Software License Procurement Assistant** that:

- Checks software license availability (IT perspective)
- Checks team budget (Finance perspective)
- Deducts the estimated license cost from the team's budget when a request is approved
- Decides whether a license request can be approved
- Prints an audit log of its reasoning, tool usage, and budget changes

This is the **reference solution** for the workshop. In the actual exercise
(05-agent-graph), participants will start from a skeleton and implement the
key parts themselves.

## Files

- `pyproject.toml` – Dependencies and Python version for this step
- `license_agent_complete.py` – Complete LangGraph agent implementation
- `README.md` – This file

## Setup

From the project root:

```bash
cd 05-agent-graph-complete
uv sync
```

## Usage

Run the complete demo:

```bash
uv run license_agent_complete.py
```

Example prompts to try:

- `I am from the IT team. Can I get an SAP license?`
- `I am from the Marketing team. Can I get an Adobe license?`

Watch the **AGENT AUDIT LOG** in the console to see:

- When the agent decides to call tools (`check_software_license`, `check_team_budget`, `deduct_budget`)
- What the tools return
- How the agent explains its final decision
- How the Finance / IT / Marketing team budgets change over time after approvals

This example will later be mirrored by a skeleton version in `05-agent-graph/`,
where participants will:

1. Implement the tools themselves
2. Fix the routing logic that decides whether to call a tool or stop
3. Experiment with prompts and personas
