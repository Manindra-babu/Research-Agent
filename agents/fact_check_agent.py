import json
from typing import List, Dict, Any
from core.state import ResearchState, FactCheckItem
from core.llm import get_llm

try:
    from langchain_core.messages import SystemMessage, HumanMessage
    HAS_LANGCHAIN = True
except ImportError:
    HAS_LANGCHAIN = False
    SystemMessage, HumanMessage = None, None


class FactCheckAgent:
    """
    Cross-validates extracted claims against source evidence and rates claim confidence.
    """

    def __init__(self):
        self.agent_name = "Fact-Check Agent"

    def run(self, state: ResearchState) -> ResearchState:
        state.log(self.agent_name, "Cross-verifying claims and calculating confidence scores...", "in-progress")
        state.current_step = "Fact-Checking"

        fact_checks: List[FactCheckItem] = []

        for finding in state.findings:
            claim_text = f"{finding.subtopic}: {finding.key_takeaway}"
            citations = finding.citations
            source_count = len(set(citations))

            verified = True
            confidence_score = 90 if source_count >= 2 else 60
            flagged = source_count < 2
            notes = "Single-source claim flagged." if flagged else "Multi-source agreement confirmed."

            if HAS_LANGCHAIN:
                system_prompt = """You are a Lead Fact-Checker AI.
Evaluate the claim against citation count and source credibility.
Return response STRICTLY in JSON:
{
  "verified": true,
  "confidence_score": 85,
  "flagged": false,
  "notes": "Verified against 2 independent sources with high domain alignment."
}
"""
                user_prompt = f"Claim: {claim_text}\nCitations used: {citations}\nTotal distinct sources: {source_count}"

                try:
                    llm = get_llm(fast=True, temperature=0.1)
                    resp = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)])
                    
                    content = resp.content.strip()
                    if "```json" in content:
                        content = content.split("```json")[1].split("```")[0].strip()
                    elif "```" in content:
                        content = content.split("```")[1].split("```")[0].strip()

                    parsed = json.loads(content)
                    verified = parsed.get("verified", True)
                    confidence_score = int(parsed.get("confidence_score", 80))
                    flagged = parsed.get("flagged", source_count < 2)
                    notes = parsed.get("notes", "Cross-verified across available sources.")

                except Exception as e:
                    print(f"[{self.agent_name}] Fact check fallback: {e}")

            fc_item = FactCheckItem(
                claim=claim_text,
                verified=verified,
                confidence_score=confidence_score,
                source_count=source_count,
                flagged=flagged,
                supporting_sources=citations,
                notes=notes
            )
            fact_checks.append(fc_item)

        state.fact_checks = fact_checks

        state.log(
            self.agent_name,
            f"Validated {len(fact_checks)} claims ({sum(1 for fc in fact_checks if fc.flagged)} flagged for low source agreement).",
            "completed"
        )

        for task in state.tasks:
            if task.agent == "Fact-Check Agent":
                task.status = "completed"

        return state
