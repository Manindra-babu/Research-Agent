import os
import sys
import time
import streamlit as st
from dotenv import load_dotenv

# Ensure root project directory is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

load_dotenv()

from core.state import ResearchState
from core.graph import build_research_graph
from core.vector_store import VectorStoreManager

# Import UI components
from dashboard.components.agent_activity import render_agent_activity
from dashboard.components.sources_table import render_sources_table
from dashboard.components.report_preview import render_report_preview
from dashboard.components.collaboration_map import render_collaboration_map
from dashboard.components.quality_gauge import render_quality_gauge

st.set_page_config(
    page_title="Multi-Agent Research System",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling for premium look
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border-radius: 8px;
        padding: 1rem;
        border: 1px solid #E2E8F0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "research_state" not in st.session_state:
    st.session_state.research_state = ResearchState()

if "is_running" not in st.session_state:
    st.session_state.is_running = False

# Sidebar Controls
with st.sidebar:
    st.image("https://img.icons8.com/isometric/96/000000/brain.png", width=64)
    st.title("Research Console")
    st.markdown("---")

    goal_input = st.text_area(
        "Enter Research Goal / Question:",
        value=st.session_state.research_state.research_goal or "Impact of Generative AI on Enterprise Cybersecurity in 2026",
        height=100,
        disabled=st.session_state.is_running
    )

    depth_choice = st.radio(
        "Research Depth:",
        options=["quick", "standard", "deep"],
        index=1,
        format_func=lambda x: f"{x.capitalize()} ({'2 queries' if x=='quick' else ('4 queries' if x=='standard' else '6 queries per subtopic')})",
        disabled=st.session_state.is_running
    )

    vector_db_type = os.getenv("VECTOR_DB", "chroma").capitalize()
    st.caption(f"⚙️ Vector Engine: **{vector_db_type}** | Search: **DuckDuckGo (DDGS)**")

    st.markdown("---")

    start_button = st.button(
        "🚀 Start Research",
        type="primary",
        use_container_width=True,
        disabled=st.session_state.is_running
    )

    st.markdown("---")
    st.markdown("### ⏳ Progress Tracker")
    
    current_step = st.session_state.research_state.current_step
    step_progress_map = {
        "initialized": 0,
        "Planning": 15,
        "Searching": 35,
        "Analyzing": 60,
        "Fact-Checking": 75,
        "Data Processing": 88,
        "Writing Report": 95,
        "Completed": 100
    }
    progress_val = step_progress_map.get(current_step, 0)
    st.progress(progress_val / 100)
    st.caption(f"Current Status: **{current_step}** ({progress_val}%)")


# Main Dashboard Area
st.markdown('<div class="main-header">🔬 Multi-Agent Research System</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Collaborative AI Agent Team for Deep Web Intelligence, Verification, and Automated Report Synthesis</div>', unsafe_allow_html=True)


# Execution Trigger
if start_button and goal_input.strip():
    st.session_state.is_running = True
    
    # Initialize fresh state
    new_state = ResearchState(
        research_goal=goal_input.strip(),
        depth=depth_choice
    )
    st.session_state.research_state = new_state

    # Run LangGraph pipeline
    with st.status("🤖 AI Agent Team Collaborating...", expanded=True) as status:
        try:
            vector_store = VectorStoreManager()
            vector_store.clear()
            app = build_research_graph(vector_store)

            # Stream execution
            input_payload = {"state": new_state}
            
            for output in app.stream(input_payload):
                for node_name, node_state in output.items():
                    current_res = node_state["state"]
                    st.session_state.research_state = current_res
                    status.update(label=f"Step complete: {node_name.capitalize()} Agent")
            
            status.update(label="🎉 Research Complete! Final report ready.", state="complete", expanded=False)
        
        except Exception as e:
            status.update(label=f"❌ Error during research: {e}", state="error")
            st.error(f"Execution failed: {e}")
        
        finally:
            st.session_state.is_running = False
            st.rerun()


# Multi-Tab Layout
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🌐 Agent Activity & Feed",
    "📚 Top Sources",
    "📄 Report Preview",
    "🕸️ Collaboration Map",
    "🎯 Quality & Security"
])

with tab1:
    render_agent_activity(st.session_state.research_state)

with tab2:
    render_sources_table(st.session_state.research_state)

with tab3:
    render_report_preview(st.session_state.research_state)

with tab4:
    render_collaboration_map(st.session_state.research_state)

with tab5:
    render_quality_gauge(st.session_state.research_state)
