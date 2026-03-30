"""
briefing_agent.py — ClarityCS Pre-Briefing Agent

Architecture Overview:
    A LangChain multi-tool agent that prepares CS agents with a
    structured brief BEFORE they open a support ticket.

    Agent flow:
    1. get_ticket_details()        → retrieve full ticket data
    2. get_ticket_history()        → customer pattern analysis
    3. check_churn_risk_signals()  → policy-based risk detection
    4. search_knowledge_base()     → ChromaDB RAG over CS policies

    LLM: Groq / Llama 3.1 (via langchain-groq)
    Memory: ConversationBufferMemory for multi-turn context
    Output: Structured brief with situation, context, churn risk,
            recommended approach, and red flags

Full implementation available on request.
Contact: bitan1basu@gmail.com
GitHub:  https://github.com/KIRA-Billion
Demo:    https://claritycs.streamlit.app
"""

from agents.tools import (
    get_ticket_details,
    get_ticket_history,
    check_churn_risk_signals,
    search_knowledge_base
)


BRIEFING_TOOLS = [
    get_ticket_details,
    get_ticket_history,
    check_churn_risk_signals,
    search_knowledge_base
]


def generate_brief(ticket_id: str) -> str:
    """
    Generates a structured agent pre-brief for the given ticket ID.

    Args:
        ticket_id: Ticket identifier e.g. TKT-1004

    Returns:
        Formatted brief string containing:
        - Situation summary
        - Customer context and history pattern
        - Churn risk assessment (LOW / MEDIUM / HIGH)
        - Recommended approach with specific actions
        - Red flags and sensitivities

    Full implementation available on request.
    Contact: bitan1basu@gmail.com
    """
    raise NotImplementedError(
        "Full agent implementation is not public. "
        "See the live demo at https://claritycs.streamlit.app "
        "or contact bitan1basu@gmail.com for a walkthrough."
    )
