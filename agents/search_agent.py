import json
import uuid
from typing import List, Dict, Any
from core.state import ResearchState, SourceItem
from core.llm import get_llm
from core.tools import search_duckduckgo, rank_and_deduplicate_sources, extract_page_content
from core.vector_store import VectorStoreManager

try:
    from langchain_core.messages import SystemMessage, HumanMessage
    HAS_LANGCHAIN = True
except ImportError:
    HAS_LANGCHAIN = False
    SystemMessage, HumanMessage = None, None


class SearchAgent:
    """
    Formulates search queries, executes DuckDuckGo web searches, scrapes page content,
    and indexes sources into the vector store.
    """

    def __init__(self, vector_store: VectorStoreManager):
        self.agent_name = "Search Agent"
        self.vector_store = vector_store

    def run(self, state: ResearchState) -> ResearchState:
        state.log(self.agent_name, "Generating search queries and fetching web sources...", "in-progress")
        state.current_step = "Searching"

        all_sources: List[SourceItem] = []
        documents_for_vector_db = []

        max_sources_per_subtopic = 2 if state.depth == "quick" else (4 if state.depth == "standard" else 6)

        for subtopic in state.subtopics:
            state.log(self.agent_name, f"Searching sources for subtopic: '{subtopic}'", "in-progress")
            
            queries = [f"{state.research_goal} {subtopic}"]
            if HAS_LANGCHAIN:
                try:
                    llm = get_llm(fast=True, temperature=0.1)
                    system_prompt = "You generate 2 targeted search queries for a given research subtopic. Return ONLY JSON list of strings, e.g. [\"query 1\", \"query 2\"]"
                    user_prompt = f"Goal: {state.research_goal}\nSubtopic: {subtopic}"
                    
                    resp = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)])
                    content = resp.content.strip()
                    if "```json" in content:
                        content = content.split("```json")[1].split("```")[0].strip()
                    elif "```" in content:
                        content = content.split("```")[1].split("```")[0].strip()
                    
                    extra_queries = json.loads(content)
                    if isinstance(extra_queries, list):
                        queries.extend([str(q) for q in extra_queries[:2]])
                except Exception as e:
                    print(f"[{self.agent_name}] Query gen fallback: {e}")

            # Execute search across queries
            subtopic_raw_sources = []
            for query in set(queries):
                results = search_duckduckgo(query, max_results=max_sources_per_subtopic)
                subtopic_raw_sources.extend(results)

            # Rank & deduplicate
            query_kw = subtopic.split() + state.research_goal.split()
            ranked_sources = rank_and_deduplicate_sources(subtopic_raw_sources, query_kw)

            # Extract full page text for top ranked sources
            for idx, src in enumerate(ranked_sources[:max_sources_per_subtopic]):
                source_id = f"SRC_{len(all_sources)+1:03d}"
                url = src.get("url", "")
                
                full_text = extract_page_content(url) or src.get("snippet", "")
                
                source_item = SourceItem(
                    id=source_id,
                    title=src.get("title", "Untitled Source"),
                    url=url,
                    snippet=src.get("snippet", ""),
                    content=full_text,
                    credibility=src.get("credibility", "Medium"),
                    relevance_score=src.get("relevance_score", 0.5),
                    subtopic=subtopic
                )
                all_sources.append(source_item)

                documents_for_vector_db.append({
                    "source_id": source_id,
                    "title": source_item.title,
                    "url": url,
                    "subtopic": subtopic,
                    "content": f"Title: {source_item.title}\nSubtopic: {subtopic}\nSnippet: {source_item.snippet}\nContent: {full_text[:1500]}"
                })

        self.vector_store.add_documents(documents_for_vector_db)
        state.sources = all_sources

        state.log(
            self.agent_name,
            f"Successfully found & indexed {len(all_sources)} sources into vector store.",
            "completed",
            details=f"Stored {len(documents_for_vector_db)} document chunks."
        )

        for task in state.tasks:
            if task.agent == "Search Agent":
                task.status = "completed"

        return state
