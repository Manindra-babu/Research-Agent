import json
from typing import List, Dict, Any
from core.state import ResearchState, ChartDataItem
from core.llm import get_llm

try:
    from langchain_core.messages import SystemMessage, HumanMessage
    HAS_LANGCHAIN = True
except ImportError:
    HAS_LANGCHAIN = False
    SystemMessage, HumanMessage = None, None


class DataAgent:
    """
    Extracts quantitative metrics, statistical comparisons, and generates chart datasets.
    """

    def __init__(self):
        self.agent_name = "Data Agent"

    def run(self, state: ResearchState) -> ResearchState:
        state.log(self.agent_name, "Extracting quantitative data and generating chart specifications...", "in-progress")
        state.current_step = "Data Processing"

        chart_list: List[ChartDataItem] = []

        context_findings = "\n".join([f"- {f.subtopic}: {f.key_takeaway} {f.details[:200]}" for f in state.findings])

        if HAS_LANGCHAIN:
            system_prompt = """You are a Data Analyst AI.
Extract or synthesize 1-2 realistic quantitative data tables/charts relevant to the research goal.
Return response STRICTLY in JSON format matching this array:
[
  {
    "title": "Market Adoption & Growth Rate (%)",
    "chart_type": "bar",
    "categories": ["2022", "2023", "2024", "2025 (Est)"],
    "values": [18.5, 29.4, 45.1, 62.0],
    "unit": "%"
  }
]
"""
            user_prompt = f"Research Goal: {state.research_goal}\nFindings Summary:\n{context_findings}"

            try:
                llm = get_llm(fast=False, temperature=0.2)
                resp = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)])
                
                content = resp.content.strip()
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()

                parsed = json.loads(content)
                for c in parsed:
                    chart_list.append(ChartDataItem(
                        title=c.get("title", "Key Metric Trend"),
                        chart_type=c.get("chart_type", "bar"),
                        categories=c.get("categories", ["Category A", "Category B", "Category C"]),
                        values=[float(v) for v in c.get("values", [10.0, 20.0, 30.0])],
                        unit=c.get("unit", "")
                    ))

            except Exception as e:
                print(f"[{self.agent_name}] Data extraction fallback: {e}")

        if not chart_list:
            chart_list.append(ChartDataItem(
                title=f"Source Distribution for {state.research_goal[:25]}",
                chart_type="bar",
                categories=["High Credibility", "Medium Credibility", "Low Credibility"],
                values=[
                    float(sum(1 for s in state.sources if s.credibility == "High")),
                    float(sum(1 for s in state.sources if s.credibility == "Medium")),
                    float(sum(1 for s in state.sources if s.credibility == "Low"))
                ],
                unit="sources"
            ))

        state.chart_data = chart_list

        state.log(
            self.agent_name,
            f"Successfully generated {len(chart_list)} data visualizations.",
            "completed"
        )

        for task in state.tasks:
            if task.agent == "Data Agent":
                task.status = "completed"

        return state
