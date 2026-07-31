import os
import json
import re
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain.chat_models import init_chat_model

from src.data_loader import (
    load_orders, get_sales_summary, load_weather_log, load_festivals,
    load_local_news, load_menu_pricing, load_finance_summary,
    load_campaigns, load_suppliers,
)

load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")


class BusinessInsight(BaseModel):
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


def run_business_analysis(store_id: str = "STORE_001", store_name: str = "Chipotle Downtown Mumbai") -> BusinessInsight:
    print("=== RUNNING BUSINESS ANALYSIS ===")

    # Load ALL business data in one go
    orders = load_orders(store_id)
    sales_summary = get_sales_summary(orders)
    weather = load_weather_log(store_id)
    festivals = load_festivals(store_id)
    news = load_local_news(store_id)
    menu_pricing = load_menu_pricing(store_id)
    finance = load_finance_summary(store_id)
    campaigns = load_campaigns(store_id)
    suppliers = load_suppliers(store_id)

    data_context = f"""=== STORE: {store_name} (ID: {store_id}) ===

--- TOP SELLING ITEMS ---
{sales_summary.head(15).to_string()}

--- WEATHER LOG ({len(weather)} entries) ---
{weather.to_string()}

--- FESTIVALS ({len(festivals)} entries) ---
{festivals.to_string()}

--- LOCAL NEWS ({len(news)} entries) ---
{news.to_string()}

--- MENU PRICING ({len(menu_pricing)} items) ---
{menu_pricing.to_string()}

--- FINANCE SUMMARY ({len(finance)} rows) ---
{finance.to_string()}

--- CAMPAIGNS ({len(campaigns)} entries) ---
{campaigns.to_string()}

--- SUPPLIERS ({len(suppliers)} rows) ---
{suppliers.to_string()}"""

    prompt = f"""You are a restaurant business strategist. Analyze the following data for {store_name} and provide a comprehensive business intelligence report.

Focus on: demand forecasting, weather/festival impact, news sentiment, pricing strategy, financial health, marketing ROI, supplier reliability, and menu optimization.

Return EXACT JSON only. No markdown, no extra text.
{{"store_id": "{store_id}", "overall_summary": "2-3 sentence overview of business health", "top_priority_issue": "the single most critical business issue", "cross_agent_pattern": "pattern across multiple business dimensions", "action_items": ["action1", "action2", "action3"], "confidence": 0.0}}

DATA:
{data_context}"""

    llm = init_chat_model("groq:llama-3.3-70b-versatile", temperature=0)
    raw = llm.invoke(prompt).content.strip()
    parsed = _extract_json(raw)
    return BusinessInsight(**parsed)


if __name__ == "__main__":
    run_business_analysis()