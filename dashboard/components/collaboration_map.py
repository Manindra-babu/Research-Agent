import streamlit as st
import plotly.graph_objects as go
from core.state import ResearchState


def render_collaboration_map(state: ResearchState):
    """
    Renders the Agent Collaboration Map network diagram.
    """
    st.subheader("🕸️ Agent Collaboration Network Map")
    st.write("Orchestrator coordinates workflow state across specialized autonomous agents:")

    try:
        # Try rendering using streamlit-agraph if available
        from streamlit_agraph import agraph, Node, Edge, Config
        
        nodes = [
            Node(id="Orchestrator", label="Orchestrator Agent\n(Planning & Routing)", size=25, color="#3B82F6", shape="circle"),
            Node(id="Search", label="Search Agent\n(Web & DDGS)", size=20, color="#10B981" if state.current_step != "initialized" else "#6B7280"),
            Node(id="Analysis", label="Analysis Agent\n(Vector RAG)", size=20, color="#8B5CF6" if state.findings else "#6B7280"),
            Node(id="FactCheck", label="Fact-Check Agent\n(Validation)", size=20, color="#F59E0B" if state.fact_checks else "#6B7280"),
            Node(id="Data", label="Data Agent\n(Charts & Stats)", size=20, color="#EC4899" if state.chart_data else "#6B7280"),
            Node(id="Writer", label="Writer Agent\n(Markdown & PDF)", size=20, color="#06B6D4" if state.final_report_md else "#6B7280"),
        ]

        edges = [
            Edge(source="Orchestrator", target="Search", label="hand-off"),
            Edge(source="Search", target="Analysis", label="index & query"),
            Edge(source="Analysis", target="FactCheck", label="claims"),
            Edge(source="Analysis", target="Data", label="metrics"),
            Edge(source="FactCheck", target="Writer", label="validated info"),
            Edge(source="Data", target="Writer", label="charts"),
        ]

        config = Config(
            width=700,
            height=400,
            directed=True,
            physics=True,
            hierarchical=False
        )

        agraph(nodes=nodes, edges=edges, config=config)

    except Exception:
        # Fallback to Plotly Network Graph if agraph encounters environment issues
        fig = go.Figure()
        
        # Node positions
        pos = {
            "Orchestrator": (0, 0),
            "Search": (-1, 1),
            "Analysis": (1, 1),
            "Fact-Check": (-1, -1),
            "Data": (1, -1),
            "Writer": (0, -1.8)
        }

        # Draw Edges
        edge_x, edge_y = [], []
        edges_list = [
            ("Orchestrator", "Search"), ("Search", "Analysis"),
            ("Analysis", "Fact-Check"), ("Analysis", "Data"),
            ("Fact-Check", "Writer"), ("Data", "Writer")
        ]
        for src, tgt in edges_list:
            x0, y0 = pos[src]
            x1, y1 = pos[tgt]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=2, color='#94A3B8'),
            hoverinfo='none',
            mode='lines'
        ))

        # Draw Nodes
        node_x = [pos[k][0] for k in pos]
        node_y = [pos[k][1] for k in pos]
        node_text = list(pos.keys())

        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            text=node_text,
            textposition="top center",
            marker=dict(
                size=30,
                color=['#3B82F6', '#10B981', '#8B5CF6', '#F59E0B', '#EC4899', '#06B6D4'],
                line=dict(width=2, color='#FFFFFF')
            )
        ))

        fig.update_layout(
            showlegend=False,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            margin=dict(l=20, r=20, t=20, b=20),
            height=350,
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)
