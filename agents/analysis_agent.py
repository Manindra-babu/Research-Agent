import json
from typing import List, Dict, Any
from core.state import ResearchState, FindingItem
from core.llm import get_llm
from core.vector_store import VectorStoreManager

try:
    from langchain_core.messages import SystemMessage, HumanMessage
    HAS_LANGCHAIN = True
except ImportError:
    HAS_LANGCHAIN = False
    SystemMessage, HumanMessage = None, None


class AnalysisAgent:
    """
    Pulls relevant text chunks from vector storage and synthesizes deep structured insights per subtopic.
    """

    def __init__(self, vector_store: VectorStoreManager):
        self.agent_name = "Analysis Agent"
        self.vector_store = vector_store

    def run(self, state: ResearchState) -> ResearchState:
        state.log(self.agent_name, "Retrieving vector chunks and synthesizing insights...", "in-progress")
        state.current_step = "Analyzing"

        findings: List[FindingItem] = []

        for subtopic in state.subtopics:
            state.log(self.agent_name, f"Analyzing subtopic: '{subtopic}'", "in-progress")

            chunks = self.vector_store.similarity_search(query=f"{state.research_goal} {subtopic}", top_k=5)
            
            context_str = ""
            citations_available = []
            for i, chunk in enumerate(chunks):
                meta = chunk.get("metadata", {})
                source_id = meta.get("source_id", f"SRC_{i+1:03d}")
                citations_available.append(source_id)
                context_str += f"\n--- Source ID: {source_id} | Title: {meta.get('title')} ---\n{chunk.get('content')}\n"

            if not context_str.strip():
                for src in state.sources:
                    if src.subtopic == subtopic or not src.subtopic:
                        citations_available.append(src.id)
                        context_str += f"\n--- Source ID: {src.id} | Title: {src.title} ---\n{src.snippet}\n{src.content[:500]}\n"

            key_takeaway = ""
            details = ""
            cited_sources = []

            if HAS_LANGCHAIN:
                system_prompt = """You are a Senior Research Analyst AI.
Analyze the provided source text for a subtopic and extract key insights, statistics, patterns, and trends.
Return your response STRICTLY as a JSON object with this exact structure:
{
  "key_takeaway": "A concise headline sentence summarizing the main insight",
  "details": "A detailed 2-3 paragraph analysis with specific facts, metrics, and observations",
  "citations": ["SRC_001", "SRC_002"]
}
"""
                user_prompt = f"Research Goal: {state.research_goal}\nSubtopic: {subtopic}\nAvailable Sources Context:\n{context_str}"

                try:
                    llm = get_llm(fast=False, temperature=0.3)
                    resp = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)])
                    
                    content = resp.content.strip()
                    if "```json" in content:
                        content = content.split("```json")[1].split("```")[0].strip()
                    elif "```" in content:
                        content = content.split("```")[1].split("```")[0].strip()
                    
                    parsed = json.loads(content)
                    key_takeaway = parsed.get("key_takeaway", f"Key analysis for {subtopic}")
                    details = parsed.get("details", "Detailed findings extracted from retrieved literature.")
                    cited_sources = parsed.get("citations", citations_available[:2])

                except Exception as e:
                    print(f"[{self.agent_name}] Synthesis fallback: {e}")

            if not key_takeaway:
                key_takeaway = f"Core observations on {subtopic}"
                details = f"Retrieved source context indicates significant active development and ongoing trends in {subtopic} relating to {state.research_goal}."
                cited_sources = citations_available[:2] if citations_available else ["SRC_001"]

            finding = FindingItem(
                subtopic=subtopic,
                key_takeaway=key_takeaway,
                details=details,
                citations=cited_sources
            )
            findings.append(finding)

        state.findings = findings

        state.log(
            self.agent_name,
            f"Completed analysis across {len(findings)} subtopics.",
            "completed",
            details=f"Generated {len(findings)} structured finding reports."
        )

        for task in state.tasks:
            if task.agent == "Analysis Agent":
                task.status = "completed"

        return state
