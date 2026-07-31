import os
import json
import re
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain.chat_models import init_chat_model

from src.operations.operations_agent import run_operations_analysis
from src.customer.customer_agent import run_customer_analysis
from src.business.business_agent import run_business_analysis

load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

class CEOReport(BaseModel):
    store_id: str
    executive_summary: str
    top_priority_issue: str
    cross_cluster_pattern: str
    final_action_plan: list[str]
    confidence: float

def _extract_json(text: str) -> dict:
    """Extract the first valid JSON object from LLM output."""
    text = text.strip().replace("```json", "").replace("```", "").strip()
    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Try finding JSON between first { and last }
    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end > start:
        try:
            return json.loads(text[start:end])
        except json.JSONDecodeError:
            pass
    # Try regex for JSON object
    match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    raise ValueError(f"Could not extract valid JSON from LLM output: {text[:200]}")

def run_ceo_analysis(store_id: str = "STORE_001", store_name: str = "Chipotle Downtown Mumbai") -> CEOReport:
    print("=== RUNNING FULL RESTAURANT AI SYSTEM ===\n")
    ops = run_operations_analysis(store_id, store_name)
    cust = run_customer_analysis(store_id, store_name)
    biz = run_business_analysis(store_id, store_name)

    combined = f"OPERATIONS REPORT:\n- Summary: {ops.overall_summary}\n- Top Issue: {ops.top_priority_issue}\n- Pattern: {ops.cross_agent_pattern}\n- Actions: {ops.action_items}\n\nCUSTOMER REPORT:\n- Summary: {cust.overall_summary}\n- Top Issue: {cust.top_priority_issue}\n- Pattern: {cust.cross_agent_pattern}\n- Actions: {cust.action_items}\n\nBUSINESS REPORT:\n- Summary: {biz.overall_summary}\n- Top Issue: {biz.top_priority_issue}\n- Pattern: {biz.cross_agent_pattern}\n- Actions: {biz.action_items}"
    
    llm = init_chat_model("groq:llama-3.3-70b-versatile", temperature=0)
    raw = llm.invoke(f"""You are a CEO of a restaurant chain. Read these three department reports and produce a final executive summary.

Return EXACT JSON only. No markdown, no extra text.
{{"store_id": "{store_id}", "executive_summary": "3-4 sentence executive summary", "top_priority_issue": "the #1 issue across all departments", "cross_cluster_pattern": "pattern that spans operations, customers, and business", "final_action_plan": ["prioritized action 1", "action 2", "action 3", "action 4"], "confidence": 0.0}}

REPORTS:
{combined}""").content.strip()
    
    parsed = _extract_json(raw)
    report = CEOReport(**parsed)
    print("\n=== CEO REPORT COMPLETE ===")
    print(f"Priority: {report.top_priority_issue}")
    return report

if __name__ == "__main__":
    run_ceo_analysis()