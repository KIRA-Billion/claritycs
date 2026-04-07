# 🎯 ClarityCS — AI-Powered CX Intelligence Agent

<div align="center">

![LangChain](https://img.shields.io/badge/LangChain-0.3-7c3aed?style=for-the-badge)
![Groq](https://img.shields.io/badge/Groq-Llama%203.1-10b981?style=for-the-badge)
![ChromaDB](https://img.shields.io/badge/ChromaDB-RAG-f59e0b?style=for-the-badge)
![Streamlit](https://img.shields.io/badge/Streamlit-Live%20Demo-ea4335?style=for-the-badge)

**[🚀 Live Demo](https://claritycs.streamlit.app) · [📧 Contact](mailto:bitan1basu@gmail.com) · [👤 GitHub Profile](https://github.com/KIRA-Billion)**

</div>

---

## The Business Problem

Enterprise CS teams are haemorrhaging money in two places nobody is watching:

**Problem 1 — Agent Context Collapse**
Every agent spends 3–5 minutes reading history before opening a ticket. At 200 tickets/day that's 10–16 hours of wasted senior capacity daily — every single day — before a single issue gets resolved.

**Problem 2 — Invisible Bad Resolutions**
When a ticket closes, nothing happens. No quality review. Bad resolutions sit undetected until a customer escalates or cancels. One churned Enterprise account can mean ₹50–500 lakhs in lost ARR.

ClarityCS solves both with a LangChain multi-agent system that takes a ticket ID and returns either a structured agent brief or a resolution quality analysis — in seconds.

---

## Live Demo

**[→ claritycs.streamlit.app](https://claritycs.streamlit.app)**

Try these tickets for best results:

| Ticket | Scenario | Tab |
|--------|----------|-----|
| `TKT-1004` | MediTrack Health — data loss, HIPAA, HIGH churn risk | Pre-Brief |
| `TKT-1010` | Pulse Analytics — CEO CC'd, 5 critical tickets | Pre-Brief |
| `TKT-1012` | SwiftShip — SLA breach, penalty clause active | Pre-Brief |
| `TKT-1007` | Zenith Retail — workaround only, CSAT 2 | Resolution Analyser |
| `TKT-1001` | Axiom Logistics — root cause documented | Resolution Analyser |
| `TKT-1002` | NovaPay Fintech — clean resolution, CSAT 5 | Resolution Analyser |

---

## Architecture

```
User Input (Ticket ID)
      │
      ▼
LangChain Agent (orchestrator — decides tool call sequence)
      │
      ├── Tool 1: get_ticket_details()        ← structured ticket data
      ├── Tool 2: get_ticket_history()        ← customer pattern analysis
      ├── Tool 3: check_churn_risk_signals()  ← policy-based risk detection
      ├── Tool 4: search_knowledge_base()     ← ChromaDB RAG over CS policies
      └── Tool 5: score_resolution_quality()  ← algorithmic quality scoring
      │
      ▼
Groq / Llama 3.1 (reasoning + structured output formatting)
      │
      ▼
Agent Brief / Resolution Quality Report
```

**Key design decision:** The LangChain agent decides which tools to call and in what order — it's not hardcoded. This means it handles edge cases (missing data, unusual ticket types) gracefully by reasoning through what information it needs.

---

## Two Agents

### Agent 1 — Pre-Briefing Agent
**Input:** Any open or escalated ticket ID
**Output:** Structured 30-second brief containing:
- One-sentence situation summary
- Customer history pattern and sentiment
- Churn risk level (LOW / MEDIUM / HIGH) with reasoning
- Recommended approach with specific actions
- Red flags and sensitivities to watch for

**Business impact:** 3–5 minutes saved per ticket × volume = significant AHT reduction without headcount changes.

### Agent 2 — Resolution Quality Analyser
**Input:** Any closed ticket ID
**Output:** Quality analysis containing:
- Resolution score 1–10 against CS policy standards
- What was done well vs what was missed
- Churn risk assessment based on pattern signals
- One specific team lead action required

**Business impact:** Catches bad resolutions before customers escalate. One Enterprise account saved from churn covers months of operating cost.

---

## Setup

### Prerequisites
- Python 3.10+
- Groq API key (free at [console.groq.com](https://console.groq.com))

### Installation

```bash
# Clone the repo
git clone https://github.com/KIRA-Billion/claritycs.git
cd claritycs

# Create virtual environment
python3 -m venv venv
source venv/bin/activate   # Mac/Linux
# venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt

# Set your API key
echo "GROQ_API_KEY=your_key_here" > .env

# Run
python -m streamlit run app.py
```

Opens at `http://localhost:8501`

---

## Project Structure

```
claritycs/
├── app.py                      ← Streamlit frontend (entire UI)
├── requirements.txt
├── .env                        ← API key (not committed)
├── .env.example
├── data/
│   ├── sample_tickets.csv      ← 15 realistic enterprise tickets
│   └── knowledge_base.txt      ← CS policy document (RAG source)
└── agents/
    ├── __init__.py
    ├── tools.py                ← 5 LangChain tools
    ├── briefing_agent.py       ← Pre-briefing agent
    └── analyser_agent.py       ← Resolution quality agent
```

---

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Agent orchestration | LangChain 0.3 | Industry standard, tool-calling, memory |
| LLM reasoning | Groq / Llama 3.1 | Free tier, fast inference |
| Vector storage | ChromaDB | Local RAG, no external dependency |
| Embeddings | HuggingFace (all-MiniLM-L6-v2) | Free, runs locally |
| Data handling | Pandas | CSV → structured data |
| Interface | Streamlit | Rapid deployment, shareable URL |

---

## Production Extension

In production this connects to live ticketing APIs. The agent logic is identical — only the data layer changes:

```python
# Current (demo)
def load_tickets():
    return pd.read_csv("data/sample_tickets.csv")

# Production (Freshdesk example)
def load_tickets():
    response = requests.get(
        f"https://{domain}.freshdesk.com/api/v2/tickets/{ticket_id}",
        auth=(api_key, "X")
    )
    return pd.DataFrame([response.json()])
```

Supported platforms: Zendesk · Freshdesk · JIRA Service Management · Salesforce · ServiceNow

---

## Related Projects

**[NexusCS](https://github.com/KIRA-Billion/nexuscs)** — Full 12-module CS Operations Intelligence Platform
Executive Dashboard · ML Pipeline · Client Health Scoring · SLA Tracker · RAG Ops Assistant

---

## About

Built by **Bitan Basu** — AI CX Automation Specialist

8+ years enterprise CS Operations at HP Inc. and Replicon (Deltek). ClarityCS demonstrates the AI-Human Workflow Bridge: taking AI outputs and wiring them into operational CS workflows with measurable business impact.

[GitHub](https://github.com/KIRA-Billion) · [Email](mailto:bitan1basu@gmail.com)
