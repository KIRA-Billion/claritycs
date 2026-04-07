"""
analyser_agent.py — ClarityCS Resolution Quality Analyser
"""
import os
from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage
from agents.tools import get_ticket_details, get_ticket_history, score_resolution_quality, check_churn_risk_signals, search_knowledge_base

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def _get_groq_key():
    try:
        import streamlit as st
        key = st.secrets.get("GROQ_API_KEY", None)
        if key:
            return key
    except Exception:
        pass
    key = os.environ.get("GROQ_API_KEY", "")
    if key:
        return key
    raise ValueError(
        "GROQ_API_KEY not found.\n"
        "Local: add GROQ_API_KEY=gsk_... to your .env file.\n"
        "Streamlit Cloud: Settings → Secrets → add GROQ_API_KEY = 'gsk_...'"
    )

ANALYSER_TOOLS = [get_ticket_details, get_ticket_history, score_resolution_quality, check_churn_risk_signals, search_knowledge_base]

ANALYSER_SYSTEM_PROMPT = """You are ClarityCS Resolution Analyser. Review closed tickets for quality and churn risk.

ALWAYS call tools in this order:
1) get_ticket_details — get full ticket info
2) score_resolution_quality — get the quality score
3) check_churn_risk_signals — assess ongoing churn risk
4) get_ticket_history — check if this is a pattern
5) search_knowledge_base — find relevant quality standards

Output format EXACTLY:
---
POST-INTERACTION ANALYSIS — [Ticket ID]
Customer: [Name] | [Company] | [Plan]
---
RESOLUTION QUALITY: [score]/10 — [EXCELLENT/GOOD/NEEDS IMPROVEMENT/POOR]

WHAT WENT WELL: specific positive observation

WHAT NEEDS IMPROVEMENT: specific gap in the resolution

CHURN RISK: [LOW/MEDIUM/HIGH] — two clear sentences explaining the risk

RECOMMENDED FOLLOW-UP: one specific action for the team lead

ACTION FLAG: [Team Lead Review] or [CSM Escalation Required] or [No Action Needed]
---"""

prompt = ChatPromptTemplate.from_messages([
    ("system", ANALYSER_SYSTEM_PROMPT),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder("agent_scratchpad")
])

chat_history = []

def analyse_ticket(ticket_id: str) -> str:
    global chat_history
    groq_key = _get_groq_key()
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0, groq_api_key=groq_key)
    agent = create_openai_tools_agent(llm, ANALYSER_TOOLS, prompt)
    executor = AgentExecutor(
        agent=agent,
        tools=ANALYSER_TOOLS,
        verbose=False,
        max_iterations=8,
        handle_parsing_errors=True
    )
    response = executor.invoke({
        "input": f"Analyse resolution quality for closed ticket {ticket_id.strip().upper()}",
        "chat_history": chat_history
    })
    result = response["output"]
    chat_history.append(HumanMessage(content=ticket_id))
    chat_history.append(AIMessage(content=result))
    return result
