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

Your job is to recommend the BEST dish that:
1. Fits within the user's budget (total cost for all people)
2. Maximises nutrition (protein and key vitamins)
3. Respects any dietary restrictions (vegetarian, vegan, gluten-free)
4. Is practically cookable by a robot

ALWAYS follow this reasoning process:
Step 1: Call fit_budget(budget_gbp, people, dietary_filter) to see all affordable options.
Step 2: For the top candidates, call get_nutrition(dish_name) to compare protein and vitamins.
Step 3: Call get_price(dish_name, servings=people) to get the exact cost and shopping list.
Step 4: Call analyse_dish(dish_name) to understand the cooking process.
Step 5: Call get_cooking_techniques(dish_name) for robotic feasibility details.
Step 6: Explain your choice — WHY this dish best balances budget and nutrition.

After reasoning, produce a STRUCTURED TASK SPECIFICATION with these sections:

## Chosen Dish and Reasoning
- Dish name and why it was selected
- Budget analysis: total cost vs. budget, cost per person
- Nutrition justification: protein, calories, key vitamins
- Trade-off explanation (what you prioritised and why)

## Shopping List
List every ingredient with quantity and estimated cost.
Show the total cost and remaining budget.

## Nutritional Summary
- Protein per serving, calories per serving, key vitamins
- How this meets the nutritional targets

## Cooking Task Specification (for Robotics Agent)
A precise specification for the Robotics Design Agent:
- All physical manipulation tasks (cutting, stirring, pouring, heating)
- Temperatures and durations for each step
- Equipment needed
- Critical precision requirements
- Safety constraints

Be specific about forces (Newtons), temperatures (°C), durations (minutes), \
and precision tolerances. The Robotics Agent depends entirely on your analysis.
"""


async def run_smart_budget_agent(
    budget_gbp: float,
    people: int,
    dietary_filter: str,
    extra_request: str,
    status_callback=None,
) -> str:
    """
    Run Agent 1: Smart Budget Food Agent.

    Selects the best dish for the budget/people/dietary constraints,
    then produces a full task specification for the Robotics Agent.
    """
    server_script = str(SERVER_DIR / "recipe_mcp_server.py")

    user_message = (
        f"Budget: £{budget_gbp:.2f} total for {people} people.\n"
        f"Dietary filter: {dietary_filter}.\n"
        f"Additional request: {extra_request if extra_request else 'none'}.\n\n"
        f"Use fit_budget to find the best dish, verify nutrition with get_nutrition, "
        f"get the shopping list with get_price, then analyse the dish fully. "
        f"Explain the budget vs. nutrition trade-off and produce a complete task "
        f"specification for the Robotics Design Agent."
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
    extra_request: str = "",
    status_callback=None,
) -> dict:
    """
    Full Smart Budget RobotChef pipeline.

    1. Looks up the best dish (Python-side, for structured metrics)
    2. Runs Agent 1 to analyse the dish and reason about budget/nutrition
    3. Runs Agent 2 to design the robot
    4. Returns structured result with metrics + agent outputs

    Returns dict with:
        food_analysis    — Agent 1's full text output
        robot_design     — Agent 2's full text output
        dish_name        — Selected dish name
        total_cost_gbp   — Total cost for all people
        protein_g        — Protein per serving (g)
        calories_kcal    — Calories per serving (kcal)
        shopping_list    — List of {item, qty, cost_gbp}
    """

    def _status(msg: str):
        if status_callback:
            status_callback(msg)

    # Pre-compute best dish for structured metrics in the UI
    best = find_best_dish(budget_gbp, people, dietary_filter)

    # Stage 1: Smart Budget Food Agent
    _status("=== Stage 1: Smart Budget Food Agent ===")
    food_analysis = await run_smart_budget_agent(
        budget_gbp=budget_gbp,
        people=people,
        dietary_filter=dietary_filter,
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
        "dish_name": best["name"] if best else "Unknown",
        "total_cost_gbp": best["total_cost_gbp"] if best else 0.0,
        "protein_g": best["protein_g_per_serving"] if best else 0,
        "calories_kcal": best["calories_kcal_per_serving"] if best else 0,
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
    parser.add_argument("--request", default="", help="Extra request")
    args = parser.parse_args()

    def print_status(msg: str):
        print(f"  [{msg}]")

    print(f"\nSmart Budget RobotChef — £{args.budget} for {args.people} people ({args.diet})")
    print("=" * 60)

    result = await run_robotic_chef_pipeline(
        budget_gbp=args.budget,
        people=args.people,
        dietary_filter=args.diet,
        extra_request=args.request,
        status_callback=print_status,
    )

    print(f"\nSelected dish: {result['dish_name']}")
    print(f"Total cost:    £{result['total_cost_gbp']:.2f}")
    print(f"Protein:       {result['protein_g']}g/serving")
    print(f"Calories:      {result['calories_kcal']} kcal/serving")

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
