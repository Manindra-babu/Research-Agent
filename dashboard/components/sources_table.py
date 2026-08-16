import streamlit as st
import pandas as pd
from core.state import ResearchState


def render_sources_table(state: ResearchState):
    """
    Renders the Top Sources table with credibility badges and links.
    """
    st.subheader("📚 Top Web Sources Retrieved")

    if not state.sources:
        st.info("No sources retrieved yet.")
        return

    data = []
    for s in state.sources:
        data.append({
            "ID": s.id,
            "Title": s.title,
            "Credibility": s.credibility,
            "Relevance Score": f"{int(s.relevance_score * 100)}%",
            "Subtopic": s.subtopic,
            "URL": s.url,
            "Snippet": s.snippet
        })

    df = pd.DataFrame(data)

    # Metrics top summary
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Sources", len(state.sources))
    col2.metric("High Credibility", sum(1 for s in state.sources if s.credibility == "High"))
    col3.metric("Avg Relevance", f"{int(sum(s.relevance_score for s in state.sources)/len(state.sources)*100)}%")

    st.markdown("---")

    for s in state.sources:
        cred_color = "green" if s.credibility == "High" else ("orange" if s.credibility == "Medium" else "red")
        with st.container():
            st.markdown(f"#### [{s.id}] [{s.title}]({s.url})")
            st.markdown(f":{cred_color}[**Credibility:** {s.credibility}] | **Relevance:** {int(s.relevance_score * 100)}% | **Subtopic:** `{s.subtopic}`")
            st.write(f"*{s.snippet}*")
            st.markdown("---")
