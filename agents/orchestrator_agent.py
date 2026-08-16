import json
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from core.state import ResearchState, TaskItem
from core.llm import get_llm

try:
    from langchain_core.messages import SystemMessage, HumanMessage
    HAS_LANGCHAIN = True
except ImportError:
    HAS_LANGCHAIN = False
    SystemMessage, HumanMessage = None, None


class PlanOutput(BaseModel):
    subtopics: List[str] = Field(description="3 to 5 clear research subtopics")
    tasks: List[Dict[str, str]] = Field(description="Initial task list assigned to search and analysis agents")


class OrchestratorAgent:
    """
    Decomposes the research goal into subtopics and task assignments.
    """

    def __init__(self):
        self.agent_name = "Orchestrator Agent"

    def run(self, state: ResearchState) -> ResearchState:
        state.log(self.agent_name, f"Planning research for: '{state.research_goal}'", "in-progress")
        state.current_step = "Planning"

        num_subtopics = 3 if state.depth == "quick" else (4 if state.depth == "standard" else 5)

        system_prompt = f"""You are an Expert Research Orchestrator AI.
Your job is to break down a user's research goal into {num_subtopics} distinct, comprehensive subtopics and generate structured tasks.

Respond strictly in valid JSON format matching this schema:
{{
  "subtopics": ["Subtopic 1", "Subtopic 2", "Subtopic 3"],
  "tasks": [
    {{"agent": "Search Agent", "description": "Search and retrieve sources for Subtopic 1"}},
    {{"agent": "Analysis Agent", "description": "Extract key findings for Subtopic 1"}}
  ]
}}
"""

        user_prompt = f"Research Goal: {state.research_goal}\nDepth: {state.depth}"

        subtopics = []
        tasks_raw = []

        if HAS_LANGCHAIN:
            try:
                llm = get_llm(fast=False, temperature=0.2)
                response = llm.invoke([
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_prompt)
                ])

                content = response.content.strip()
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()

                parsed = json.loads(content)
                subtopics = parsed.get("subtopics", [])
                tasks_raw = parsed.get("tasks", [])
            except Exception as e:
                print(f"[{self.agent_name}] LLM fallback: {e}")

        if not subtopics:
            subtopics = [
                f"Market Overview & Background for {state.research_goal}",
                f"Key Industry Drivers & Technologies",
                f"Future Outlook & Comparative Analysis"
            ]
            tasks_raw = [
                {"agent": "Search Agent", "description": f"Gather web sources for {state.research_goal}"},
                {"agent": "Analysis Agent", "description": "Synthesize core findings and trends"},
                {"agent": "Fact-Check Agent", "description": "Verify extracted claims"},
                {"agent": "Data Agent", "description": "Extract metrics and statistics"},
                {"agent": "Writer Agent", "description": "Generate final comprehensive report"}
            ]

        state.subtopics = subtopics
        
        task_items = []
        for i, t in enumerate(tasks_raw):
            task_items.append(TaskItem(
                id=f"task_{i+1}",
                agent=t.get("agent", "Search Agent"),
                description=t.get("description", "Execute research step"),
                status="pending"
            ))
        state.tasks = task_items

        state.log(self.agent_name, f"Decomposed research into {len(subtopics)} subtopics.", "completed", details=f"Subtopics: {', '.join(subtopics)}")
        return state
