<div align="center">

# 🔬 Multi-Agent Research System

### *An Autonomous Team of Collaborating AI Agents for Deep Web Intelligence, Fact Validation, and Automated Report Synthesis*

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/Orchestration-LangGraph-FF6F00?logo=langchain&logoColor=white)](https://www.langchain.com/)
[![Groq](https://img.shields.io/badge/LLM_Engine-Groq_API-f55036?logo=groq&logoColor=white)](https://groq.com/)
[![Search](https://img.shields.io/badge/Web_Search-DuckDuckGo_DDGS-00B4D8?logo=duckduckgo&logoColor=white)](https://pypi.org/project/duckduckgo-search/)
[![VectorDB](https://img.shields.io/badge/Vector_RAG-ChromaDB-purple.svg)](https://www.trychroma.com/)
[![Dashboard](https://img.shields.io/badge/UI-Streamlit_1.38%2B-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

<br/>

[ Key Features ](#-key-features) • [ The Agent Team ](#-the-agent-team) • [ Quick Start ](#-quick-start-guide) • [ Dashboard UI ](#-dashboard-ui) • [ Security ](#-security--privacy)

</div>

---

## 📌 Overview

The **Multi-Agent Research System** is an enterprise-grade research application that deploys a team of specialized AI agents working together in a stateful **LangGraph** execution machine. 

Given any research prompt or question, the system breaks the goal down into subtopics, searches the web using **zero-key DuckDuckGo Search**, scrapes and indexes raw source content into **ChromaDB**, synthesizes deep insights, cross-verifies claims across independent sources, extracts numerical datasets, and exports a publication-ready report in **Markdown** and **PDF**.

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
                       │ (DuckDuckGo + RAG)    │
                       └───────────┬───────────┘
                                   │
                                   ▼
                       ┌───────────────────────┐
                       │    Analysis Agent     │
                       │ (Vector Chunk RAG)    │
                       └───────────┬───────────┘
                                   │
             ┌─────────────────────┴─────────────────────┐
             ▼                                           ▼
 ┌───────────────────────┐                   ┌───────────────────────┐
 │   Fact-Check Agent    │                   │      Data Agent       │
 │  (Cross-Verification) │                   │ (Metrics & Visuals)   │
 └───────────┬───────────┘                   └───────────┬───────────┘
             │                                           │
             └─────────────────────┬─────────────────────┘
                                   ▼
                       ┌───────────────────────┐
                       │     Writer Agent      │
                       │ (Markdown & PDF Output)│
                       └───────────────────────┘
```

---

## ✨ Key Features

- **🤖 6 Autonomous Specialized Agents**: Explicit hand-offs between Orchestrator, Search, Analysis, Fact-Check, Data, and Writer agents.
- **⚡ Sub-Second Groq Inferences**: Powered by `llama-3.3-70b-versatile` for complex reasoning/writing and `llama-3.1-8b-instant` for fast query generation and fact checking.
- **🌐 100% Free Web Search**: Integrates DuckDuckGo (`ddgs`) with exponential backoff retries — **no API keys or signups needed for web search**.
- **🧠 Local Vector RAG**: Scrapes full webpage content using `trafilatura` and indexes chunks into local persistent ChromaDB.
- **🔍 Automated Fact Validation**: Cross-checks claims against source evidence and flags single-source findings.
- **📊 Quantitative Data & Plotly Charts**: Extracts statistical metrics and builds interactive charts (Bar, Line, Pie).
- **📥 Direct In-Memory PDF Download**: Instantly exports styled PDF reports directly in your browser.
- **🎛️ Real-Time Streamlit Dashboard**: Live agent activity feed, top sources table with credibility badges, collaboration map, and quality index gauge.

---

## 🤖 The Agent Team

| Agent | Model Engine | Core Responsibilities | Key Output |
| :--- | :--- | :--- | :--- |
| **Orchestrator** | `llama-3.3-70b-versatile` | Goal decomposition, subtopic planning, task routing | Structured Subtopic & Task Plan |
| **Search Agent** | `llama-3.1-8b-instant` | Formulates search queries, calls DDGS, ranks credibility | Cleaned Web Sources & Vector Index |
| **Analysis Agent**| `llama-3.3-70b-versatile` | Vector chunk RAG retrieval, structured insight synthesis | Subtopic Findings & Source Citations |
| **Fact-Check** | `llama-3.1-8b-instant` | Cross-validates claims, calculates confidence score | Verified Claims & Single-Source Flags |
| **Data Agent** | `llama-3.3-70b-versatile` | Extracts numerical metrics, generates chart specifications | Plotly Visualizations & Metric Tables |
| **Writer Agent** | `llama-3.3-70b-versatile` | Synthesizes full report, calculates Quality Index (0-100) | Markdown & Downloadable PDF |

---

## 💻 Dashboard UI Preview

The dashboard features a multi-tab interface built with Streamlit:

1. **🌐 Agent Activity & Feed**: Live timeline of agent actions, handoffs, and status indicators streamed in real time.
2. **📚 Top Sources**: Interactive table of sources with domain reputation badges (`High`, `Medium`, `Low`), relevance scores, and direct links.
3. **📄 Report Preview**: Publication-ready rendered Markdown document with embedded Plotly charts and a single-click **Download PDF** button.
4. **🕸️ Collaboration Map**: Visual network graph showing Orchestrator state routing across specialized agents.
5. **🎯 Quality & Security**: Dynamic 0-100 Quality Score gauge and static privacy panel.

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Python 3.11+**
- **Groq API Key**: Free key from [console.groq.com](https://console.groq.com/keys)

> 💡 **No Web Search Key Needed**: DuckDuckGo search (`ddgs`) works out of the box with zero configuration!

### 2. Installation

Clone the repository and set up a virtual environment:

```bash
# Clone the repository
git clone https://github.com/Manindra-babu/Research-Agent.git
cd Research-Agent

# Create & activate virtual environment
python -m venv venv

# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

Copy `.env.example` to `.env` and add your Groq API key:

```bash
cp .env.example .env
```

Edit your `.env` file:
```env
GROQ_API_KEY=gsk_your_groq_api_key_here
VECTOR_DB=chroma
```

### 4. Launch the Dashboard

```bash
streamlit run dashboard/app.py
```

Open your browser at `http://localhost:8501`.

---

## 🧪 Testing

Run the full pytest suite to verify state machine transitions and agent schemas:

```bash
pytest tests/test_agents.py
```

Expected output:
```text
============================= test session starts =============================
platform win32 -- Python 3.13.9, pytest-8.4.2
collected 6 items

tests\test_agents.py ......                                              [100%]

============================== 6 passed in 0.89s ==============================
```

---

## ⚙️ Configuration & Customization

Domain focus, search query limits, and model choices can be customized in [`config/agents_config.yaml`](file:///c:/Users/manin/OneDrive/Desktop/Projects/Research%20Agent/config/agents_config.yaml):

```yaml
domain_focus: "general" # Options: general, market_research, academic, technology

agents:
  orchestrator:
    model_type: "reasoning" # llama-3.3-70b-versatile
    max_subtopics: 4
  
  search:
    model_type: "fast" # llama-3.1-8b-instant
    default_depth: "standard" # quick, standard, deep
```

---

## 📂 Project Structure

```
multi-agent-research-system/
├── .env.example                # Environment variables template
├── .gitignore                  # Protection against committing keys/local DBs
├── README.md                   # Project documentation
├── requirements.txt            # Package dependencies
├── config/
│   └── agents_config.yaml      # Agent team parameters & thresholds
├── core/
│   ├── state.py                # Shared ResearchState Pydantic v2 model
│   ├── llm.py                  # Groq client via langchain-groq
│   ├── vector_store.py         # ChromaDB / Pinecone vector storage manager
│   ├── tools.py                # DDGS search, Trafilatura scraper, Plotly & PDF
│   └── graph.py                # LangGraph state machine workflow
├── agents/
│   ├── orchestrator_agent.py   # Task planning & routing
│   ├── search_agent.py         # Web search & vector indexing
│   ├── analysis_agent.py       # Context retrieval & insight synthesis
│   ├── fact_check_agent.py     # Claim verification & confidence scoring
│   ├── data_agent.py           # Metric extraction & chart creation
│   └── writer_agent.py         # Report generation & PDF synthesis
├── dashboard/
│   ├── app.py                  # Main Streamlit dashboard application
│   └── components/             # Reusable UI component modules
└── tests/
    └── test_agents.py          # Pytest suite
```

---

## 🔒 Security & Privacy

- **Zero Data Training**: All LLM requests execute statelessly via Groq API without model training storage.
- **Local Persistence**: Vector indexes are stored locally in `./chroma_db_data`.
- **Secret Protection**: `.env` is listed in `.gitignore` by default.

---

<div align="center">

Made with ❤️ using **LangGraph**, **Groq**, **DuckDuckGo**, and **Streamlit**.

</div>
