# 🔬 Multi-Agent Research System

A full-stack, autonomous team of collaborating AI agents that conduct in-depth research on any topic, gather and clean web sources, cross-validate facts, perform statistical analysis, and generate publication-ready structured reports in Markdown and PDF formats.

Powered by **LangGraph**, **Groq API** (`llama-3.3-70b-versatile` & `llama-3.1-8b-instant`), **DuckDuckGo Search (`ddgs`)**, **ChromaDB**, and **Streamlit**.

---

## 🌟 Key Features

- **Autonomous Agent Team (6 Agents)**: Orchestrator, Search, Analysis, Fact-Check, Data, and Writer agents operating in a stateful LangGraph execution machine.
- **Zero API Key Web Search**: Uses DuckDuckGo (`ddgs`) for 100% free web search with retries and exponential backoff.
- **High-Speed Reasoning & Search**: Groq API provides sub-second LLM inference with fast 8B models for query generation/fact-checks and 70B models for deep reasoning and writing.
- **Local Vector RAG**: Scrapes and indexes full webpage content into ChromaDB (or Pinecone) for accurate context retrieval.
- **Source Verification & Fact-Checking**: Automatically flags single-source claims and computes credibility ratings.
- **Interactive Streamlit Dashboard**: Real-time agent activity feed, top sources table with credibility badges, network collaboration map, quality gauge, and PDF export.

---

## 🏗️ Architecture & Workflow

```
                  User Research Goal
                          │
                          ▼
              ┌───────────────────────┐
              │  Orchestrator Agent   │
              │  (Plans Subtopics)    │
              └───────────┬───────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │     Search Agent      │
              │ (DuckDuckGo + Chroma) │
              └───────────┬───────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │    Analysis Agent     │
              │ (Vector Chunk RAG)    │
              └───────────┬───────────┘
                          │
            ┌─────────────┴─────────────┐
            ▼                           ▼
┌───────────────────────┐   ┌───────────────────────┐
│   Fact-Check Agent    │   │      Data Agent       │
│  (Cross-Verification) │   │ (Metrics & Visuals)   │
└───────────┬───────────┘   └───────────┬───────────┘
            │                           │
            └─────────────┬─────────────┘
                          ▼
              ┌───────────────────────┐
              │     Writer Agent      │
              │ (Markdown & PDF Output)│
              └───────────────────────┘
```

### The Agent Team:
1. **Orchestrator Agent**: Breaks user question into 3–5 subtopics and plans task routing.
2. **Search Agent**: Formulates queries, fetches DuckDuckGo web results, cleans text via Trafilatura, and indexes into ChromaDB.
3. **Analysis Agent**: Pulls relevant vector chunks and synthesizes structured findings per subtopic.
4. **Fact-Check Agent**: Cross-verifies claims against source evidence and assigns confidence scores.
5. **Data Agent**: Extracts quantitative data, metrics, and generates Plotly visual charts.
6. **Writer Agent**: Synthesizes final report sections, calculates quality score (0–100), and exports styled PDF.

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.11 or higher
- Free Groq API Key ([Get your key here](https://console.groq.com/keys))

> **Note:** DuckDuckGo Web Search requires **NO API key or signup** — it works out of the box.

### 2. Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/your-username/multi-agent-research-system.git
cd multi-agent-research-system

# Create virtual environment (optional but recommended)
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 3. Environment Configuration

Copy `.env.example` to `.env` and fill in your Groq API key:

```bash
cp .env.example .env
```

Edit `.env`:
```env
GROQ_API_KEY=gsk_your_groq_api_key_here
VECTOR_DB=chroma
```

### 4. Run the Streamlit Dashboard

Launch the interactive dashboard:

```bash
streamlit run dashboard/app.py
```

Open your browser at `http://localhost:8501`.

---

## 🧪 Running Tests

Run the pytest test suite to verify agent schemas and tools:

```bash
pytest tests/test_agents.py
```

---

## 📁 Project Structure

```
multi-agent-research-system/
├── .env.example                # Template for environment variables
├── requirements.txt            # Core dependencies
├── README.md                   # Documentation & guide
├── config/
│   └── agents_config.yaml     # Configurable agent parameters & model settings
├── core/
│   ├── state.py                # Pydantic v2 ResearchState model
│   ├── llm.py                  # Groq client initializer (langchain-groq)
│   ├── vector_store.py         # ChromaDB / Pinecone abstraction
│   ├── tools.py                # DDGS search, Trafilatura scraper, Plotly, PDF export
│   └── graph.py                # LangGraph state graph workflow
├── agents/
│   ├── orchestrator_agent.py   # Subtopic planning & task breakdown
│   ├── search_agent.py         # Query generation, web search, vector indexing
│   ├── analysis_agent.py       # Context retrieval & insight synthesis
│   ├── fact_check_agent.py     # Claim cross-validation & confidence scoring
│   ├── data_agent.py           # Quantitative metrics & chart generation
│   └── writer_agent.py         # Report writing & PDF generation
├── dashboard/
│   ├── app.py                  # Main Streamlit dashboard application
│   └── components/
│       ├── agent_activity.py   # Live execution feed & task checklist
│       ├── sources_table.py    # Top sources with credibility badges
│       ├── report_preview.py   # Rendered Markdown & PDF download
│       ├── collaboration_map.py# Agent network graph
│       └── quality_gauge.py   # Quality index & security info panel
├── outputs/
│   └── reports/                # Saved JSON sessions and PDF reports
└── tests/
    └── test_agents.py          # Unit & integration smoke tests
```

---

## 🔒 Security & Privacy

- **Zero-Data Training**: Your queries and search results are processed statelessly without model training storage.
- **Local Persistence**: Vector storage defaults to local ChromaDB on your machine.
- **Source Transparency**: Every statement in the generated report links directly to source IDs.
