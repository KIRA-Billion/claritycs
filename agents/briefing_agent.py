"""
briefing_agent.py — ClarityCS Agent Pre-Briefing Pipeline
"""
import os
from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage
from agents.tools import get_ticket_details, get_ticket_history, check_churn_risk_signals, search_knowledge_base

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def _get_groq_key():
    # Streamlit Cloud secrets
    try:
        import streamlit as st
        key = st.secrets.get("GROQ_API_KEY", None)
        if key:
            return key
    except Exception:
        pass
    # Local .env
    key = os.environ.get("GROQ_API_KEY", "")
    if key:
        return key
    raise ValueError(
        "GROQ_API_KEY not found.\n"
        "Local: add GROQ_API_KEY=gsk_... to your .env file.\n"
        "Streamlit Cloud: Settings → Secrets → add GROQ_API_KEY = 'gsk_...'"
    )

BRIEFING_TOOLS = [get_ticket_details, get_ticket_history, check_churn_risk_signals, search_knowledge_base]

BRIEFING_SYSTEM_PROMPT = """You are ClarityCS Briefing Agent. Prepare pre-briefs for CS agents before they open tickets.

ALWAYS call tools in this order:
1) get_ticket_details — get full ticket info
2) get_ticket_history — get customer's full history  
3) check_churn_risk_signals — assess churn risk
4) search_knowledge_base — find relevant SLA/escalation policy

Output format EXACTLY:
---
AGENT BRIEF — [Ticket ID] | [Customer] | [Company] | [Priority]
---
SITUATION: one clear sentence about the issue.

CUSTOMER CONTEXT:
- History pattern (from ticket history)
- Current sentiment
- Account importance (plan tier, ARR risk)

CHURN RISK: [LOW/MEDIUM/HIGH] — specific reason from signals

RECOMMENDED APPROACH:
1. First action to take
2. Key thing to address in the conversation  
3. SLA commitment to make

WATCH OUT FOR: specific red flags or sensitivities
---"""

prompt = ChatPromptTemplate.from_messages([
    ("system", BRIEFING_SYSTEM_PROMPT),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder("agent_scratchpad")
])

chat_history = []

def generate_brief(ticket_id: str) -> str:
    global chat_history
    groq_key = _get_groq_key()
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0, groq_api_key=groq_key)
    agent = create_openai_tools_agent(llm, BRIEFING_TOOLS, prompt)
    executor = AgentExecutor(
        agent=agent,
        tools=BRIEFING_TOOLS,
        verbose=False,
        max_iterations=8,
        handle_parsing_errors=True
    )
    response = executor.invoke({
        "input": f"Generate agent pre-brief for ticket {ticket_id.strip().upper()}",
        "chat_history": chat_history
    })
    result = response["output"]
    chat_history.append(HumanMessage(content=ticket_id))
    chat_history.append(AIMessage(content=result))
    return result
