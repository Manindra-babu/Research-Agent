import streamlit as st
from core.state import ResearchState


def render_agent_activity(state: ResearchState):
    """
    Renders the live Agent Activity Feed and Task Breakdown.
    """
    st.subheader("🤖 Live Agent Activity Feed")

    if not state.agent_logs:
        st.info("No research active yet. Enter a goal in the sidebar and click **Start Research**.")
        return

    # Task Breakdown Grid
    st.markdown("### Agent Task Checklist")
    cols = st.columns(min(len(state.tasks) or 1, 5))
    for idx, task in enumerate(state.tasks):
        col = cols[idx % len(cols)]
        badge = "✅" if task.status == "completed" else ("⏳" if task.status == "in-progress" else "⏸️")
        col.metric(label=f"{badge} {task.agent}", value=task.status.capitalize(), help=task.description)

    st.markdown("---")
    st.markdown("### Execution Timeline & Logs")
    
    for log in reversed(state.agent_logs):
        icon = "🟢" if log.status == "completed" else ("🟡" if log.status == "in-progress" else "🔴")
        with st.expander(f"{icon} [{log.timestamp}] **{log.agent}**: {log.action}", expanded=(log.status == "in-progress")):
            st.write(f"**Status:** {log.status.capitalize()}")
            if log.details:
                st.write(f"**Details:** {log.details}")
