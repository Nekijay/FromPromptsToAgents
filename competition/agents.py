"""
Agents — Smart Budget RobotChef (A2A Pipeline)
===============================================
Competition: Smart Budget RobotChef
University of Hertfordshire - 18 April 2026

Two-agent pipeline:
  Agent 1 — Smart Budget Food Agent
      Takes budget, people, dietary filter.
      Uses fit_budget + get_nutrition + get_price + analyse_dish + get_cooking_techniques.
      Picks the best dish and explains the budget/nutrition trade-off.

  Agent 2 — Robotics Designer Agent
      Receives the task specification from Agent 1.
      Designs a complete robotic cooking platform using the robotics MCP server.
"""

import asyncio
import json
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Add competition directory to path so recipe_mcp_server is importable
_COMP_DIR = Path(__file__).parent
sys.path.insert(0, str(_COMP_DIR))
from recipe_mcp_server import DISH_DATABASE, find_best_dish

import llm_client

SERVER_DIR = _COMP_DIR


# ---------------------------------------------------------------------------
# Core: run an agent loop connected to an MCP server
# ---------------------------------------------------------------------------

async def run_agent_with_mcp(
    server_script: str,
    system_prompt: str,
    user_message: str,
    status_callback=None,
) -> str:
    """
    Generic agent loop that connects to an MCP server via stdio, discovers
    tools, and runs the LLM until it produces a final text response.
    """

    def _status(msg: str):
        if status_callback:
            status_callback(msg)

    _status(f"Starting MCP server: {Path(server_script).name}")
    server_params = StdioServerParameters(command=sys.executable, args=[server_script])

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            _status("MCP session initialised")

            tools_result = await session.list_tools()
            tools = [
                {
                    "name": t.name,
                    "description": t.description or "",
                    "parameters": t.inputSchema if t.inputSchema else {"type": "object", "properties": {}},
                }
                for t in tools_result.tools
            ]
            _status(f"Discovered {len(tools)} tools: {', '.join(t['name'] for t in tools)}")

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ]

            last_content = ""
            for iteration in range(10):
                _status(f"LLM call (iteration {iteration + 1})")
                response = llm_client.chat(messages, tools=tools)

                if response["tool_calls"]:
                    messages.append({"role": "assistant", "content": response["raw"]})
                    for tc in response["tool_calls"]:
                        fn_name = tc["name"]
                        fn_args = tc["arguments"]
                        _status(f"Calling tool: {fn_name}")
                        try:
                            result = await session.call_tool(fn_name, fn_args)
                            tool_output = ""
                            if result.content:
                                for block in result.content:
                                    if hasattr(block, "text"):
                                        tool_output += block.text
                            _status(f"Tool {fn_name} returned {len(tool_output)} chars")
                        except Exception as e:
                            tool_output = json.dumps({"error": str(e)})
                            _status(f"Tool {fn_name} error: {e}")
                        messages.append({"role": "tool", "name": fn_name, "content": tool_output})
                else:
                    _status("Agent produced final response")
                    return response["content"] or ""

                last_content = response.get("content") or ""

            _status("Max iterations reached")
            return last_content or "Agent did not produce a final response."


# ---------------------------------------------------------------------------
# Agent 1: Smart Budget Food Agent
# ---------------------------------------------------------------------------

SMART_BUDGET_FOOD_AGENT_SYSTEM_PROMPT = """\
You are the Smart Budget Food Agent — an expert culinary analyst who balances \
nutrition and cost for families on a budget.

You operate in two modes:

MODE A — USER SPECIFIED A DISH:
The user has chosen a specific dish. Your job is to:
1. Try to look it up with analyse_dish(dish_name) and get_cooking_techniques(dish_name).
2. If not found in the database, use your own culinary knowledge about that dish.
3. Estimate the cost for the number of people and check if it fits the budget.
4. Estimate protein, calories, and key vitamins from your knowledge.
5. Explain whether it fits the budget and any trade-offs.

MODE B — AI RECOMMENDS A DISH:
No dish was specified. Your job is to:
1. Call fit_budget(budget_gbp, people, dietary_filter) to see all affordable options.
2. Call get_nutrition(dish_name) on the top candidates to compare protein and vitamins.
3. Call get_price(dish_name, servings=people) for exact cost and shopping list.
4. Call analyse_dish(dish_name) and get_cooking_techniques(dish_name) for cooking details.
5. Choose the best dish and explain WHY it best balances budget and nutrition.

In BOTH modes, produce a STRUCTURED TASK SPECIFICATION with these sections:

## Chosen Dish and Reasoning
- Dish name and why it was selected (or why the user's choice fits/doesn't fit)
- Budget analysis: estimated total cost vs. budget, cost per person
- Nutrition justification: protein (g), calories (kcal), key vitamins
- Trade-off explanation

## Shopping List
Every ingredient with quantity and estimated UK supermarket cost.
Total cost and remaining budget.

## Nutritional Summary
Protein per serving, calories per serving, key vitamins, dietary flags.

## Cooking Task Specification (for Robotics Agent)
A precise robotics specification:
- All physical manipulation tasks (cutting, stirring, pouring, heating)
- Temperatures (°C) and durations (minutes) for each step
- Equipment needed and how the robot interacts with it
- Critical precision requirements
- Safety constraints

Be specific about temperatures (°C), durations (minutes), and forces where known. \
The Robotics Agent depends entirely on your analysis. If a dish is not in the \
database, use your culinary knowledge — do NOT refuse, just estimate confidently.
"""


async def run_smart_budget_agent(
    budget_gbp: float,
    people: int,
    dietary_filter: str,
    dish_request: str = "",
    extra_request: str = "",
    status_callback=None,
) -> str:
    """
    Run Agent 1: Smart Budget Food Agent.

    If dish_request is provided, analyses that specific dish (even if not in
    the database — the agent falls back to its own culinary knowledge).
    Otherwise, uses fit_budget to recommend the best dish for the budget.
    """
    server_script = str(SERVER_DIR / "recipe_mcp_server.py")

    if dish_request:
        user_message = (
            f"The user wants to cook: '{dish_request}'.\n"
            f"Budget: £{budget_gbp:.2f} total for {people} people "
            f"(£{budget_gbp/people:.2f} per person).\n"
            f"Dietary filter: {dietary_filter}.\n"
            f"Extra notes: {extra_request if extra_request else 'none'}.\n\n"
            f"MODE A: Try to look up '{dish_request}' using analyse_dish and "
            f"get_cooking_techniques. If it is not in the database, use your "
            f"culinary knowledge to estimate costs, nutrition, and cooking steps. "
            f"Check whether it fits the budget, explain any trade-offs, then produce "
            f"a complete task specification for the Robotics Design Agent."
        )
    else:
        user_message = (
            f"Budget: £{budget_gbp:.2f} total for {people} people.\n"
            f"Dietary filter: {dietary_filter}.\n"
            f"Extra notes: {extra_request if extra_request else 'none'}.\n\n"
            f"MODE B: Use fit_budget to find the best dish, verify nutrition with "
            f"get_nutrition, get the shopping list with get_price, then analyse the "
            f"dish fully. Explain the budget vs. nutrition trade-off and produce a "
            f"complete task specification for the Robotics Design Agent."
        )

    return await run_agent_with_mcp(
        server_script=server_script,
        system_prompt=SMART_BUDGET_FOOD_AGENT_SYSTEM_PROMPT,
        user_message=user_message,
        status_callback=status_callback,
    )


# ---------------------------------------------------------------------------
# Agent 2: Robotics Designer Agent
# ---------------------------------------------------------------------------

ROBOTICS_DESIGN_SYSTEM_PROMPT = """\
You are the Robotics Design Agent — an expert in designing robotic systems for \
food preparation. You receive a detailed task specification from the Food Agent \
and design a complete robotic cooking platform.

Use the available tools to:
1. Call recommend_platform(task_description) for an initial platform suggestion
2. Call search_components(category, task) for robot arms and bases
3. Call search_sensors(sensor_type, task) for sensing capabilities
4. Call search_actuators(actuator_type, task) for manipulation tools
5. Call get_component_details(component_id) for full specs on selected parts

Then design a complete system with these sections:

## Robot Design Overview
- Robot type and form factor (single/dual arm, stationary/mobile)
- Justification based on the cooking task

## Selected Components
For each component: Component ID, name, key specs, and why chosen.

## Sensor Suite
For each sensor: what it monitors, why it's needed, mounting location.

## Actuators and End-Effectors
For each actuator: what task it performs, key specs for this dish.

## Motion and Control Requirements
- Degrees of freedom and speed requirements
- Force control requirements for delicate operations
- Coordination between multiple tasks

## Safety and Compliance
- High-temperature handling strategy
- Human-robot interaction safety
- Food safety compliance

## Platform Summary Table
All selected components with IDs and roles.

## Estimated Autonomy
- Steps the robot handles fully autonomously
- Steps needing human oversight
- Overall autonomy percentage

Reference actual component IDs (e.g. COMP-001, SENS-003) from the database. \
Justify every selection against the task specification received.
"""


async def run_robotics_agent(task_specification: str, status_callback=None) -> str:
    """Run Agent 2: Robotics Designer Agent."""
    server_script = str(SERVER_DIR / "robotics_mcp_server.py")
    user_message = (
        f"Based on the following task specification from the Smart Budget Food Agent, "
        f"design a complete robotic cooking platform.\n\n"
        f"--- TASK SPECIFICATION ---\n{task_specification}\n--- END SPECIFICATION ---"
    )
    return await run_agent_with_mcp(
        server_script=server_script,
        system_prompt=ROBOTICS_DESIGN_SYSTEM_PROMPT,
        user_message=user_message,
        status_callback=status_callback,
    )


# ---------------------------------------------------------------------------
# Pipeline: Full Smart Budget RobotChef (A2A)
# ---------------------------------------------------------------------------

async def run_robotic_chef_pipeline(
    budget_gbp: float,
    people: int,
    dietary_filter: str = "none",
    dish_request: str = "",
    extra_request: str = "",
    status_callback=None,
) -> dict:
    """
    Full Smart Budget RobotChef pipeline.

    If dish_request is provided, analyses that dish (even custom ones not in
    the database). Otherwise, uses fit_budget to find the best dish.

    Returns dict with:
        food_analysis  — Agent 1's full text output
        robot_design   — Agent 2's full text output
        dish_name      — Dish name (from DB lookup or the user's request)
        total_cost_gbp — Estimated total cost for all people
        protein_g      — Protein per serving (g)
        calories_kcal  — Calories per serving (kcal)
        shopping_list  — List of {item, qty, cost_gbp} (empty for custom dishes)
    """

    def _status(msg: str):
        if status_callback:
            status_callback(msg)

    # For structured metrics: try DB lookup if no custom dish specified
    if dish_request:
        # Try to find it in DB for metrics; if not found metrics come from agent text
        from recipe_mcp_server import _find_dish
        _, matched = _find_dish(dish_request)
        if matched:
            best = {
                "name": matched["name"],
                "total_cost_gbp": round(matched["price_per_serving_gbp"] * people, 2),
                "protein_g_per_serving": matched["protein_g_per_serving"],
                "calories_kcal_per_serving": matched["calories_kcal_per_serving"],
                "shopping_list": matched.get("shopping_list", []),
            }
        else:
            best = None  # custom dish — metrics shown as "see analysis"
    else:
        best = find_best_dish(budget_gbp, people, dietary_filter)

    # Stage 1: Smart Budget Food Agent
    _status("=== Stage 1: Smart Budget Food Agent ===")
    food_analysis = await run_smart_budget_agent(
        budget_gbp=budget_gbp,
        people=people,
        dietary_filter=dietary_filter,
        dish_request=dish_request,
        extra_request=extra_request,
        status_callback=status_callback,
    )
    _status("Food Agent complete")

    # Stage 2: Robotics Designer Agent
    _status("=== Stage 2: Robotics Designer Agent ===")
    robot_design = await run_robotics_agent(
        task_specification=food_analysis,
        status_callback=status_callback,
    )
    _status("Robotics Agent complete")

    return {
        "food_analysis": food_analysis,
        "robot_design": robot_design,
        "dish_name": best["name"] if best else (dish_request or "Unknown"),
        "total_cost_gbp": best["total_cost_gbp"] if best else None,
        "protein_g": best["protein_g_per_serving"] if best else None,
        "calories_kcal": best["calories_kcal_per_serving"] if best else None,
        "shopping_list": best["shopping_list"] if best else [],
    }


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

async def _main():
    import argparse

    parser = argparse.ArgumentParser(description="Smart Budget RobotChef — CLI")
    parser.add_argument("--budget", type=float, default=15.0, help="Budget in GBP")
    parser.add_argument("--people", type=int, default=2, help="Number of people")
    parser.add_argument("--diet", default="none", help="none / vegetarian / vegan / gluten-free")
    parser.add_argument("--dish", default="", help="Specific dish to cook (optional)")
    parser.add_argument("--request", default="", help="Extra notes")
    args = parser.parse_args()

    def print_status(msg: str):
        print(f"  [{msg}]")

    dish_label = f"'{args.dish}'" if args.dish else "AI recommendation"
    print(f"\nSmart Budget RobotChef — £{args.budget} for {args.people} people | dish: {dish_label}")
    print("=" * 60)

    result = await run_robotic_chef_pipeline(
        budget_gbp=args.budget,
        people=args.people,
        dietary_filter=args.diet,
        dish_request=args.dish,
        extra_request=args.request,
        status_callback=print_status,
    )

    print(f"\nDish:       {result['dish_name']}")
    cost = result["total_cost_gbp"]
    print(f"Total cost: £{cost:.2f}" if cost is not None else "Total cost: see analysis")
    print(f"Protein:    {result['protein_g']}g/serving" if result["protein_g"] else "Protein: see analysis")
    print(f"Calories:   {result['calories_kcal']} kcal" if result["calories_kcal"] else "Calories: see analysis")

    print("\n" + "=" * 60)
    print("FOOD ANALYSIS (Agent 1)")
    print("=" * 60)
    print(result["food_analysis"])

    print("\n" + "=" * 60)
    print("ROBOT DESIGN (Agent 2)")
    print("=" * 60)
    print(result["robot_design"])


if __name__ == "__main__":
    asyncio.run(_main())
