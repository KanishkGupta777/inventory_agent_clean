import os
import json
import re
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain.chat_models import init_chat_model

from src.data_loader import (
    load_customers, load_customer_orders, load_customer_feedback, load_offers,
)

load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")


class CustomerInsight(BaseModel):
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


def run_customer_analysis(store_id: str = "STORE_001", store_name: str = "Chipotle Downtown Mumbai") -> CustomerInsight:
    print("=== RUNNING CUSTOMER ANALYSIS ===")

    # Load ALL customer data in one go
    customers = load_customers(store_id)
    cust_orders = load_customer_orders(store_id)
    feedback = load_customer_feedback(store_id)
    offers = load_offers(store_id)

    data_context = f"""=== STORE: {store_name} (ID: {store_id}) ===

--- CUSTOMERS ({len(customers)} rows) ---
{customers.to_string()}

--- CUSTOMER ORDERS ({len(cust_orders)} rows) ---
{cust_orders.to_string(max_rows=30)}

--- CUSTOMER FEEDBACK ({len(feedback)} entries) ---
{feedback.to_string()}

--- ACTIVE OFFERS ({len(offers)} offers) ---
{offers.to_string()}"""

    prompt = f"""You are a restaurant customer analytics expert. Analyze the following data for {store_name} and provide a comprehensive customer report.

Focus on: CRM health, loyalty trends, feedback sentiment, churn risk, personalization opportunities, and offer effectiveness.

Return EXACT JSON only. No markdown, no extra text.
{{"store_id": "{store_id}", "overall_summary": "2-3 sentence overview of customer health", "top_priority_issue": "the single most critical customer issue", "cross_agent_pattern": "pattern across multiple customer dimensions", "action_items": ["action1", "action2", "action3"], "confidence": 0.0}}

DATA:
{data_context}"""

    llm = init_chat_model("groq:llama-3.3-70b-versatile", temperature=0)
    raw = llm.invoke(prompt).content.strip()
    parsed = _extract_json(raw)
    return CustomerInsight(**parsed)


if __name__ == "__main__":
    run_customer_analysis()