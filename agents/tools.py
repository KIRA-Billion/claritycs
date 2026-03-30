"""
tools.py — ClarityCS LangChain Tool Definitions

Five tools the LangChain agents can call.
The agent decides which tools to use and in what order
based on the task — this is the core of the agentic behaviour.

Tool Summary:
    get_ticket_details()        → retrieves full structured ticket data
    get_ticket_history()        → retrieves all tickets for a customer
    check_churn_risk_signals()  → checks against CS policy churn indicators
    search_knowledge_base()     → ChromaDB RAG search over CS policy docs
    score_resolution_quality()  → algorithmic resolution quality scoring 1-10

Architecture Notes:
    - Data layer: Pandas CSV (demo) → swap for Zendesk/Freshdesk API in production
    - Vector store: ChromaDB (local) with HuggingFace all-MiniLM-L6-v2 embeddings
    - Churn signals: pattern-matched against CS policy rules (escalation count,
      sentiment, CSAT, churn language detection, account tier)
    - Resolution scoring: rule-based against quality standards (root cause,
      fix confirmation, preventative measures, CSAT validation)

Production Extension:
    Replace load_tickets() CSV read with a live API call:

    # Freshdesk example
    def load_tickets():
        response = requests.get(
            f"https://{{domain}}.freshdesk.com/api/v2/tickets/{{ticket_id}}",
            auth=(api_key, "X")
        )
        return pd.DataFrame([response.json()])

    Supported platforms: Zendesk · Freshdesk · JIRA · Salesforce · ServiceNow

Full implementation available on request.
Contact: bitan1basu@gmail.com
GitHub:  https://github.com/KIRA-Billion
Demo:    https://claritycs.streamlit.app
"""

from langchain.tools import tool


@tool
def get_ticket_details(ticket_id: str) -> str:
    """
    Retrieves full details of a specific ticket by ticket ID.
    Use this as the first step when analysing any ticket.
    Input: ticket ID like TKT-1001
    """
    raise NotImplementedError("Full implementation not public.")


@tool
def get_ticket_history(customer_name: str) -> str:
    """
    Retrieves all previous tickets for a given customer name.
    Use this to understand the customer's history before briefing an agent.
    Input: customer name as a string.
    """
    raise NotImplementedError("Full implementation not public.")


@tool
def check_churn_risk_signals(ticket_id: str) -> str:
    """
    Checks a ticket against known churn risk indicators from CS policy.
    Use this to flag whether a customer needs urgent CSM attention.
    Input: ticket ID like TKT-1001
    """
    raise NotImplementedError("Full implementation not public.")


@tool
def search_knowledge_base(query: str) -> str:
    """
    Searches the CS policy knowledge base using ChromaDB RAG.
    Use this to find escalation policies, SLA rules, or handling guidance.
    Input: natural language question about CS policies.
    """
    raise NotImplementedError("Full implementation not public.")


@tool
def score_resolution_quality(ticket_id: str) -> str:
    """
    Scores the quality of a closed ticket's resolution on a scale of 1-10.
    Use this only on tickets with status Closed.
    Input: ticket ID like TKT-1001
    """
    raise NotImplementedError("Full implementation not public.")
