import os
import sys
import pytest

# Ensure root directory is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.state import ResearchState, SourceItem, FindingItem, FactCheckItem, ChartDataItem
from core.tools import rank_and_deduplicate_sources, export_report_to_pdf, export_report_to_pdf_bytes
from agents.orchestrator_agent import OrchestratorAgent
from agents.search_agent import SearchAgent
from agents.analysis_agent import AnalysisAgent
from agents.fact_check_agent import FactCheckAgent
from agents.data_agent import DataAgent
from agents.writer_agent import WriterAgent
from core.vector_store import VectorStoreManager


def test_research_state_serialization(tmp_path):
    """Test state persistence to JSON and reload."""
    state = ResearchState(research_goal="Test Quantum Computing", depth="quick")
    state.subtopics = ["Qubits", "Algorithms"]
    
    file_path = tmp_path / "test_session.json"
    saved_path = state.save_to_disk(str(file_path))
    assert os.path.exists(saved_path)
    
    loaded_state = ResearchState.load_from_disk(saved_path)
    assert loaded_state.research_goal == "Test Quantum Computing"
    assert loaded_state.subtopics == ["Qubits", "Algorithms"]


def test_source_ranking_and_deduplication():
    """Test domain credibility heuristic and keyword scoring."""
    raw_sources = [
        {"title": "Quantum Computing MIT", "url": "https://news.mit.edu/quantum", "snippet": "Breakthroughs in qubit stability."},
        {"title": "Blog post", "url": "https://randomblog.com/post", "snippet": "My thoughts on quantum computing."},
        {"title": "Duplicate MIT", "url": "https://news.mit.edu/quantum", "snippet": "Duplicate link check."}
    ]
    
    ranked = rank_and_deduplicate_sources(raw_sources, ["quantum", "qubit"])
    assert len(ranked) == 2  # Deduplicated
    assert ranked[0]["credibility"] == "High"  # MIT domain ranked top


def test_orchestrator_agent_fallback():
    """Test Orchestrator Agent execution and state mutation."""
    state = ResearchState(research_goal="Autonomous Vehicles 2026", depth="quick")
    agent = OrchestratorAgent()
    updated_state = agent.run(state)
    
    assert len(updated_state.subtopics) >= 3
    assert len(updated_state.tasks) >= 3
    assert updated_state.current_step == "Planning"


def test_fact_check_agent():
    """Test Fact-Check Agent confidence scoring and flagging."""
    state = ResearchState(research_goal="AI Safety")
    state.findings = [
        FindingItem(
            subtopic="Alignment",
            key_takeaway="RLHF improves safety.",
            details="Details on alignment training.",
            citations=["SRC_001"] # Single source -> should flag
        )
    ]
    
    agent = FactCheckAgent()
    updated_state = agent.run(state)
    
    assert len(updated_state.fact_checks) == 1
    assert updated_state.fact_checks[0].flagged is True


def test_data_agent():
    """Test Data Agent chart generation fallback."""
    state = ResearchState(research_goal="Renewable Energy Adoption")
    state.findings = [
        FindingItem(subtopic="Solar", key_takeaway="Solar costs fell 80%", details="Capacity reached 1TW", citations=["SRC_001"])
    ]
    state.sources = [
        SourceItem(id="SRC_001", title="Solar Energy", url="https://org.com", snippet="...", credibility="High")
    ]
    
    agent = DataAgent()
    updated_state = agent.run(state)
    
    assert len(updated_state.chart_data) >= 1
    assert updated_state.chart_data[0].chart_type in ["bar", "line", "pie"]


def test_pdf_generation_bytes():
    """Test in-memory PDF generation via ReportLab."""
    pdf_bytes = export_report_to_pdf_bytes(
        title="Test Research Report",
        markdown_content="# Executive Summary\nTest content.\n## Key Findings\n- Point 1\n- Point 2"
    )
    assert pdf_bytes is not None
    assert len(pdf_bytes) > 0
