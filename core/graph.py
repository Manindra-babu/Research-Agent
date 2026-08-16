from typing import TypedDict, Dict, Any
from core.state import ResearchState
from core.vector_store import VectorStoreManager

from agents.orchestrator_agent import OrchestratorAgent
from agents.search_agent import SearchAgent
from agents.analysis_agent import AnalysisAgent
from agents.fact_check_agent import FactCheckAgent
from agents.data_agent import DataAgent
from agents.writer_agent import WriterAgent

try:
    from langgraph.graph import StateGraph, START, END
    HAS_LANGGRAPH = True
except ImportError:
    HAS_LANGGRAPH = False
    StateGraph, START, END = None, None, None


class GraphState(TypedDict):
    state: ResearchState


def build_research_graph(vector_store: VectorStoreManager = None):
    """
    Constructs the multi-agent execution state machine using LangGraph or sequential pipeline fallback.
    """
    if vector_store is None:
        vector_store = VectorStoreManager()

    orchestrator = OrchestratorAgent()
    search = SearchAgent(vector_store=vector_store)
    analysis = AnalysisAgent(vector_store=vector_store)
    fact_check = FactCheckAgent()
    data = DataAgent()
    writer = WriterAgent()

    if not HAS_LANGGRAPH or StateGraph is None:
        class SequentialPipeline:
            def invoke(self, input_data: dict) -> dict:
                st = input_data["state"]
                st = orchestrator.run(st)
                st = search.run(st)
                st = analysis.run(st)
                st = fact_check.run(st)
                st = data.run(st)
                st = writer.run(st)
                return {"state": st}

            def stream(self, input_data: dict):
                st = input_data["state"]
                for agent_name, agent_fn in [
                    ("orchestrator", orchestrator.run),
                    ("search", search.run),
                    ("analysis", analysis.run),
                    ("fact_check", fact_check.run),
                    ("data", data.run),
                    ("writer", writer.run)
                ]:
                    st = agent_fn(st)
                    yield {agent_name: {"state": st}}

        return SequentialPipeline()

    def orchestrator_step(gstate: GraphState) -> GraphState:
        res = orchestrator.run(gstate["state"])
        res.save_to_disk()
        return {"state": res}

    def search_step(gstate: GraphState) -> GraphState:
        res = search.run(gstate["state"])
        res.save_to_disk()
        return {"state": res}

    def analysis_step(gstate: GraphState) -> GraphState:
        res = analysis.run(gstate["state"])
        res.save_to_disk()
        return {"state": res}

    def fact_check_step(gstate: GraphState) -> GraphState:
        res = fact_check.run(gstate["state"])
        res.save_to_disk()
        return {"state": res}

    def data_step(gstate: GraphState) -> GraphState:
        res = data.run(gstate["state"])
        res.save_to_disk()
        return {"state": res}

    def writer_step(gstate: GraphState) -> GraphState:
        res = writer.run(gstate["state"])
        res.save_to_disk()
        return {"state": res}

    workflow = StateGraph(GraphState)

    workflow.add_node("orchestrator", orchestrator_step)
    workflow.add_node("search", search_step)
    workflow.add_node("analysis", analysis_step)
    workflow.add_node("fact_check", fact_check_step)
    workflow.add_node("data", data_step)
    workflow.add_node("writer", writer_step)

    workflow.add_edge(START, "orchestrator")
    workflow.add_edge("orchestrator", "search")
    workflow.add_edge("search", "analysis")
    workflow.add_edge("analysis", "fact_check")
    workflow.add_edge("fact_check", "data")
    workflow.add_edge("data", "writer")
    workflow.add_edge("writer", END)

    app = workflow.compile()
    return app


def run_research_pipeline(goal: str, depth: str = "standard") -> ResearchState:
    vector_store = VectorStoreManager()
    vector_store.clear()

    initial_state = ResearchState(research_goal=goal, depth=depth)
    app = build_research_graph(vector_store)
    
    final_output = app.invoke({"state": initial_state})
    return final_output["state"]
