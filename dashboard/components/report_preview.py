import streamlit as st
from core.state import ResearchState

try:
    from core.tools import create_chart_figure, export_report_to_pdf_bytes
except ImportError:
    from core.tools import create_chart_figure, export_report_to_pdf
    def export_report_to_pdf_bytes(title: str, markdown_content: str) -> bytes:
        path = export_report_to_pdf(title, markdown_content)
        with open(path, "rb") as f:
            return f.read()


def render_report_preview(state: ResearchState):
    """
    Renders rendered report sections, data charts, sample insights, and in-memory PDF download option.
    """
    st.subheader("📄 Generated Research Report")

    if not state.final_report_md:
        st.info("Report has not been generated yet.")
        return

    # In-Memory PDF Download Button
    try:
        pdf_bytes = export_report_to_pdf_bytes(
            title=f"Research Report: {state.research_goal}",
            markdown_content=state.final_report_md
        )
    except Exception as e:
        pdf_bytes = f"{state.research_goal}\n\n{state.final_report_md}".encode("utf-8")

    st.download_button(
        label="📥 Download PDF Report",
        data=pdf_bytes,
        file_name=f"research_report_{state.session_id}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
    
    st.markdown("---")

    # Sample Insight Highlight Callout
    if state.findings:
        top_finding = state.findings[0]
        st.info(f"💡 **Sample Key Insight ({top_finding.subtopic}):** {top_finding.key_takeaway}")

    # Charts Section
    if state.chart_data:
        st.markdown("### 📊 Data & Visualizations")
        chart_cols = st.columns(min(len(state.chart_data), 2))
        for idx, chart in enumerate(state.chart_data):
            col = chart_cols[idx % len(chart_cols)]
            fig = create_chart_figure(
                chart_type=chart.chart_type,
                title=chart.title,
                data={"categories": chart.categories, "values": chart.values}
            )
            if fig:
                col.plotly_chart(fig, use_container_width=True)

    # Rendered Markdown Report Body
    st.markdown("### 📝 Full Markdown Document")
    st.markdown(state.final_report_md)
