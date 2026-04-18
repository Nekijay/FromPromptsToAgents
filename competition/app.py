"""
Smart Budget RobotChef — Streamlit UI
=======================================
Competition: University of Hertfordshire - 18 April 2026

Run with:
    cd competition
    streamlit run app.py
"""

import asyncio
import sys
from pathlib import Path

import streamlit as st

# Ensure competition/ is on the path for agents.py import
sys.path.insert(0, str(Path(__file__).parent))
from agents import run_robotic_chef_pipeline

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Smart Budget RobotChef",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 Smart Budget RobotChef")
st.caption("Agent-to-Agent AI System — University of Hertfordshire Workshop 2026")

# ---------------------------------------------------------------------------
# Sidebar: meal parameters
# ---------------------------------------------------------------------------

with st.sidebar:
    st.header("Meal Parameters")

    dish_request = st.text_input(
        "Dish to cook (optional)",
        placeholder="e.g. Jollof rice and chicken, pasta carbonara...",
        help="Leave blank and the AI will pick the best dish for your budget.",
    )

    budget = st.slider(
        "Budget (£)",
        min_value=5,
        max_value=50,
        value=15,
        step=1,
        help="Total budget in GBP for all people",
    )

    people = st.number_input(
        "Number of People",
        min_value=1,
        max_value=10,
        value=2,
        step=1,
    )

    dietary = st.selectbox(
        "Dietary Filter",
        options=["none", "vegetarian", "vegan", "gluten-free"],
        help="Filter dishes by dietary requirement",
    )

    st.divider()
    extra = st.text_area(
        "Extra notes (optional)",
        placeholder="e.g. high protein, quick to cook, kid-friendly...",
        height=70,
    )

    st.divider()
    st.markdown(
        f"**Budget per person:** £{budget / people:.2f}\n\n"
        f"**Diet:** {dietary}"
    )

# ---------------------------------------------------------------------------
# Main area: prompt preview + run button
# ---------------------------------------------------------------------------

prompt_parts = [f"£{budget} budget", f"{people} people"]
if dish_request:
    prompt_parts.insert(0, f"Dish: {dish_request}")
if dietary != "none":
    prompt_parts.append(dietary)
if extra:
    prompt_parts.append(extra)
mode = "Custom dish" if dish_request else "AI picks best dish for budget"
prompt_preview = ", ".join(prompt_parts) + ". Design a robot to cook it."

st.info(f"**Mode:** {mode}  \n**Prompt:** {prompt_preview}")

col_run, col_info = st.columns([1, 3])
with col_run:
    run_button = st.button("🍳 Design Robot Chef", type="primary", use_container_width=True)

# ---------------------------------------------------------------------------
# Pipeline execution
# ---------------------------------------------------------------------------

if run_button:
    status_messages = []

    with st.status("Running agents...", expanded=True) as status_box:

        def update_status(msg: str):
            status_messages.append(msg)
            st.write(msg)

        try:
            result = asyncio.run(
                run_robotic_chef_pipeline(
                    budget_gbp=float(budget),
                    people=int(people),
                    dietary_filter=dietary,
                    dish_request=dish_request.strip(),
                    extra_request=extra,
                    status_callback=update_status,
                )
            )
            status_box.update(label="Agents finished!", state="complete", expanded=False)
        except Exception as e:
            status_box.update(label=f"Error: {e}", state="error")
            st.error(f"Pipeline failed: {e}")
            st.stop()

    # ---- Metrics row ----
    st.subheader(f"Dish: {result['dish_name']}")

    m1, m2, m3, m4 = st.columns(4)
    cost = result["total_cost_gbp"]
    m1.metric("Total Cost", f"£{cost:.2f}" if cost is not None else "See analysis", f"Budget: £{budget}")
    m2.metric("Protein / serving", f"{result['protein_g']}g" if result["protein_g"] else "See analysis")
    m3.metric("Calories / serving", f"{result['calories_kcal']} kcal" if result["calories_kcal"] else "See analysis")
    budget_remaining = budget - cost if cost is not None else None
    m4.metric("Budget remaining", f"£{budget_remaining:.2f}" if budget_remaining is not None else "—")

    # ---- Shopping list ----
    if result["shopping_list"]:
        with st.expander("Shopping List", expanded=False):
            cols = st.columns([3, 2, 1])
            cols[0].markdown("**Item**")
            cols[1].markdown("**Qty**")
            cols[2].markdown("**Cost**")
            for item in result["shopping_list"]:
                c1, c2, c3 = st.columns([3, 2, 1])
                c1.write(item["item"])
                c2.write(item["qty"])
                c3.write(f"£{item['cost_gbp']:.2f}")

    st.divider()

    # ---- Agent outputs ----
    col_a1, col_a2 = st.columns(2)

    with col_a1:
        with st.expander("Agent 1 — Food Analysis & Budget Reasoning", expanded=True):
            st.markdown(result["food_analysis"])

    with col_a2:
        with st.expander("Agent 2 — Robot Design", expanded=True):
            st.markdown(result["robot_design"])
