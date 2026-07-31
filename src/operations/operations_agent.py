import os
import json
import re
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain.chat_models import init_chat_model

from src.data_loader import (
    load_inventory, load_orders, load_recipes, get_sales_summary,
    get_ingredient_usage, load_kitchen_orders, load_menu_prep_times,
    load_waste_log, load_packaging_inventory, load_packaging_usage,
    load_staff_schedule, load_staff_performance,
)

load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")


class OperationsInsight(BaseModel):
    store_id: str
    overall_summary: str
    top_priority_issue: str
    cross_agent_pattern: str
    action_items: list[str]
    confidence: float


def _extract_json(text: str) -> dict:
    text = text.strip().replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end > start:
        try:
            return json.loads(text[start:end])
        except json.JSONDecodeError:
            pass
    match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    raise ValueError(f"Could not extract valid JSON from LLM output: {text[:200]}")


def run_operations_analysis(store_id: str = "STORE_001", store_name: str = "Chipotle Downtown Mumbai") -> OperationsInsight:
    print("=== RUNNING OPERATIONS ANALYSIS ===")

    # Load ALL operations data in one go
    inventory = load_inventory(store_id)
    orders = load_orders(store_id)
    recipes = load_recipes(store_id)
    sales_summary = get_sales_summary(orders)
    ingredient_usage = get_ingredient_usage(orders, recipes)
    kitchen_orders = load_kitchen_orders(store_id)
    prep_times = load_menu_prep_times(store_id)
    waste = load_waste_log(store_id)
    packaging_inv = load_packaging_inventory(store_id)
    packaging_use = load_packaging_usage(store_id)
    staff_sched = load_staff_schedule(store_id)
    staff_perf = load_staff_performance(store_id)

    data_context = f"""=== STORE: {store_name} (ID: {store_id}) ===

--- INVENTORY ({len(inventory)} items) ---
{inventory.to_string(max_rows=30)}

--- TOP SELLING ITEMS ---
{sales_summary.head(15).to_string()}

--- INGREDIENT USAGE (top 15) ---
{ingredient_usage.head(15).to_string()}

--- KITCHEN ORDERS ({len(kitchen_orders)} rows) ---
{kitchen_orders.to_string(max_rows=20)}

--- MENU PREP TIMES ({len(prep_times)} items) ---
{prep_times.to_string(max_rows=20)}

--- WASTE LOG ({len(waste)} entries) ---
{waste.to_string(max_rows=20)}

--- PACKAGING INVENTORY ({len(packaging_inv)} items) ---
{packaging_inv.to_string()}

--- PACKAGING USAGE ({len(packaging_use)} entries) ---
{packaging_use.head(20).to_string()}

--- STAFF SCHEDULE ({len(staff_sched)} rows) ---
{staff_sched.to_string()}

--- STAFF PERFORMANCE ({len(staff_perf)} rows) ---
{staff_perf.to_string()}"""

    prompt = f"""You are a restaurant operations analyst. Analyze the following data for {store_name} and provide a comprehensive operations report.

Focus on: inventory levels, expiry risks, kitchen efficiency, waste management, packaging needs, and staff scheduling.

Return EXACT JSON only. No markdown, no extra text.
{{"store_id": "{store_id}", "overall_summary": "2-3 sentence overview of operations health", "top_priority_issue": "the single most critical issue found", "cross_agent_pattern": "pattern across multiple operational areas", "action_items": ["action1", "action2", "action3"], "confidence": 0.0}}

DATA:
{data_context}"""

    llm = init_chat_model("groq:llama-3.3-70b-versatile", temperature=0)
    raw = llm.invoke(prompt).content.strip()
    parsed = _extract_json(raw)
    return OperationsInsight(**parsed)


if __name__ == "__main__":
    run_operations_analysis()