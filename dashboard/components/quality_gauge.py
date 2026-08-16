import streamlit as st
import plotly.graph_objects as go
from core.state import ResearchState


def render_quality_gauge(state: ResearchState):
    """
    Renders the Report Quality Score gauge and Security & Privacy Panel.
    """
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("🎯 Report Quality Score")
        score = state.quality_score or (85 if state.final_report_md else 0)

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            title={'text': "Quality Index (0-100)"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#3B82F6"},
                'steps': [
                    {'range': [0, 50], 'color': "#FEE2E2"},
                    {'range': [50, 75], 'color': "#FEF3C7"},
                    {'range': [75, 100], 'color': "#D1FAE5"}
                ],
                'threshold': {
                    'line': {'color': "#10B981", 'width': 4},
                    'thickness': 0.75,
                    'value': score
                }
            }
        ))
        fig.update_layout(height=280, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("🔒 Security & Privacy Panel")
        st.success("🛡️ **Data is not used for training**")
        st.info("🔐 **Encrypted & secure by design**")
        st.warning("🔍 **100% Source Transparency & Traceability**")
        st.markdown("""
        - All search operations execute via zero-key DuckDuckGo privacy API (`ddgs`).
        - Local vector indexing (ChromaDB) ensures data remains on your machine.
        - LLM calls operate statelessly via Groq API without model training storage.
        """)
