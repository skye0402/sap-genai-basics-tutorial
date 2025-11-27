# 05 – Agent Graph (Exercise)

In this step you will build an **Agent** using LangGraph.
The agent acts as a **Software License Procurement Assistant** that:

- Checks software license availability (IT perspective)
- Checks team budget (Finance perspective)
- Decides whether a license request can be approved

This folder contains an **exercise skeleton**. A complete reference solution
is available in `05-agent-graph-complete/`, but you should try the exercise
here first.

## Files

- `pyproject.toml` – Dependencies and Python version for this step
- `license_agent_exercise.py` – Skeleton LangGraph agent with TODOs

## Setup

From the project root:

```bash
cd 05-agent-graph
uv sync
```

## Exercise Overview

You will complete two main parts:

1. **EXERCISE 1 – Define cross‑department tools**
   - Implement two tools:
     - `check_software_license(software_name: str)` – mocked IT inventory
     - `check_team_budget(team_name: str)` – mocked Finance budget
2. **EXERCISE 2 – Implement routing logic**
   - Fix `should_continue` so the agent knows when to call tools and when to stop.

Optionally, you can also try a third exercise:

3. **EXERCISE 3 – Add a state-changing tool (deduct_budget)**
   - Implement a new tool that deducts a license cost from the team's budget.

The rest of the code (state definition, LangGraph wiring, CLI loop, audit log)
is already implemented for you.

---

## EXERCISE 1 – Implement the tools

Open `license_agent_exercise.py` and find:

- `check_software_license(software_name: str)`
- `check_team_budget(team_name: str)`

Both functions currently return placeholder strings and have detailed TODO
comments.

### Your task

- Replace the placeholder returns with simple, deterministic logic. For example:
  - For `check_software_license`:
    - If the name contains "sap" → return "Available: we have spare SAP licenses."
    - If the name contains "adobe" → return "Out of stock: no Adobe licenses available."
    - Otherwise → return an "unknown availability" message.
  - For `check_team_budget`:
    - "IT" team → high budget (e.g. `Budget: 10000 USD remaining.`)
    - "Marketing" team → very low budget (e.g. `Budget: 100 USD remaining.`)
    - "Finance" team → medium budget (e.g. `Budget: 5000 USD remaining.`)
    - Any other team → unknown/very low budget.

You do **not** need to change the `tools` list or `model_with_tools` – this is
already wired for you.

---

## EXERCISE 2 – Fix the routing logic

Next, find the function:

```python
def should_continue(state: MessagesState) -> Literal["tool_node", END]:
    ...
```

Right now it always returns `END`, so the agent never calls tools.

### Your task

- Implement the logic as described in the docstring:
  - Look at the last AI message in `state["messages"]`.
  - If it has `tool_calls` → return `"tool_node"`.
  - Otherwise → return `END`.
- **Optional:** add a safety stop, e.g. if `state["llm_calls"] > 3` → `END`.

You do **not** need to modify the graph wiring code that uses `should_continue`.

---

## (Optional) EXERCISE 3 – Add a state-changing tool

In the complete demo (`05-agent-graph-complete`), there is an extra tool
called `deduct_budget` that updates an in-memory `TEAM_BUDGETS` dictionary
whenever a license is approved.

You can try something similar here:

1. Define a global dictionary at the top of `license_agent_exercise.py`, e.g.:

   ```python
   TEAM_BUDGETS = {
       "it": 10000.0,
       "marketing": 100.0,
       "finance": 5000.0,
   }
   ```

2. Create a new tool:

   ```python
   @tool
   def deduct_budget(team_name: str, amount_usd: float) -> str:
       """Deduct an amount from the team's budget (demo only)."""
       # TODO: look up TEAM_BUDGETS[team_name], subtract, store and return a message
   ```

3. Add this tool to the `tools` list and `tools_by_name` mapping.

4. Update the system prompt in `llm_call` to instruct the agent:
   - When it approves a request, it should call `deduct_budget` with a
     reasonable cost estimate (for example, ~3000 USD for SAP, ~600 USD for Adobe).

5. Run the agent again and make multiple approved requests for the same team.
   - Watch how the budget decreases over time in the AGENT AUDIT LOG.

---

## Running the agent

After finishing EXERCISE 1 and EXERCISE 2, run:

```bash
uv run license_agent_exercise.py
```

Try prompts like:

- `I am from the IT team. Can I get an SAP license?`
- `I am from the Marketing team. Can I get an Adobe license?`
- `I am from Marketing and I need an SAP license.`

Watch the **AGENT AUDIT LOG** printed in the console. It will show:

- When the agent decides to call tools (`check_software_license`, `check_team_budget`)
- What the tools return
- How the agent explains its final decision

If your logic is working, you should see different outcomes for different
team/software combinations (for example, IT+SAP approved, Marketing+SAP
rejected due to budget).

---

## Need help?

If you get stuck, you can:

- Inspect the complete reference implementation in `05-agent-graph-complete/`.
- Compare how the tools and `should_continue` are implemented there.

Once you are comfortable with this example, think about how you could add
more tools (for example, `create_ticket`, `escalate_request`) or where you
would want a **human approval step** in a real SAP system.
