"""
tools.py — ClarityCS LangChain Tool Definitions (Full Implementation)
"""

import os
import pandas as pd
from langchain.tools import tool
from langchain_community.embeddings import HuggingFaceEmbeddings
import chromadb

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "sample_tickets.csv")
KB_PATH   = os.path.join(os.path.dirname(__file__), "..", "data", "knowledge_base.txt")

def _load_df() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)

_chroma_collection = None

def _get_kb_collection():
    global _chroma_collection
    if _chroma_collection is not None:
        return _chroma_collection
    with open(KB_PATH, "r") as f:
        kb_text = f.read()
    chunks = [c.strip() for c in kb_text.split("===") if len(c.strip()) > 80]
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    client = chromadb.Client()
    try:
        client.delete_collection("claritycs_kb")
    except Exception:
        pass
    collection = client.create_collection("claritycs_kb")
    vectors = embeddings.embed_documents(chunks)
    collection.add(
        documents=chunks,
        embeddings=vectors,
        ids=[f"chunk_{i}" for i in range(len(chunks))]
    )
    _chroma_collection = (collection, embeddings)
    return _chroma_collection

CHURN_KEYWORDS = ["cancel", "terminate", "switch", "competitor", "legal", "contract", "leave", "alternative", "lawyer"]

def _assess_churn(row, df):
    signals = []
    level = "LOW"
    prev = str(row.get("previous_interactions", "")).lower()
    if "critical" in prev and any(str(n) in prev for n in ["3 ", "4 ", "5 "]):
        signals.append("3+ Critical tickets in last 90 days — CSM escalation required")
        level = "HIGH"
    desc = str(row.get("description", "")).lower()
    res  = str(row.get("resolution_notes", "")).lower()
    found = [k for k in CHURN_KEYWORDS if k in desc or k in res]
    if found:
        signals.append(f"Churn language detected: {', '.join(found)}")
        level = "HIGH"
    try:
        if float(row.get("csat_score")) < 3:
            signals.append(f"CSAT score {row['csat_score']} — below threshold")
            if level != "HIGH": level = "MEDIUM"
    except (TypeError, ValueError):
        pass
    if any(t in desc for t in ["ceo", "cfo", "cto", "coo", "vp ", "director"]):
        signals.append("C-suite directly involved — automatic CSM escalation")
        level = "HIGH"
    if str(row.get("sentiment_raw", "")).lower() == "very_negative":
        signals.append("Sentiment flagged as very_negative")
        if level == "LOW": level = "MEDIUM"
    if str(row.get("status", "")).lower() == "escalated":
        signals.append("Ticket is currently Escalated")
        if level == "LOW": level = "MEDIUM"
    if "pattern" in prev or "5 critical" in prev:
        signals.append("Pattern of repeat critical issues — systemic instability")
        level = "HIGH"
    if not signals:
        signals.append("No churn risk indicators detected")
    return level, signals

@tool
def get_ticket_details(ticket_id: str) -> str:
    """
    Retrieves full details of a specific ticket by ticket ID.
    Use this as the first step when analysing any ticket.
    Input: ticket ID like TKT-1004
    """
    df = _load_df()
    row = df[df["ticket_id"] == ticket_id.strip().upper()]
    if row.empty:
        return f"Ticket {ticket_id} not found. Available: {', '.join(df['ticket_id'].tolist())}"
    r = row.iloc[0]
    csat = r["csat_score"] if pd.notna(r["csat_score"]) else "Not yet rated"
    res  = r["resolution_notes"] if pd.notna(r["resolution_notes"]) and str(r["resolution_notes"]) not in ["None","nan",""] else "No resolution notes yet"
    resolved = r["resolved_date"] if pd.notna(r["resolved_date"]) and str(r["resolved_date"]) not in ["None","nan",""] else "Not yet resolved"
    return f"""TICKET DETAILS — {r['ticket_id']}
Customer:   {r['customer_name']}
Company:    {r['company']}
Plan:       {r['plan']}
Issue:      {r['issue_type']}
Priority:   {r['priority']}
Status:     {r['status']}
Created:    {r['created_date']}
Resolved:   {resolved}
Agent:      {r['agent_name']}
Sentiment:  {r['sentiment_raw']}
CSAT:       {csat}

DESCRIPTION:
{r['description']}

RESOLUTION NOTES:
{res}"""

@tool
def get_ticket_history(customer_name: str) -> str:
    """
    Retrieves all previous tickets for a given customer name.
    Use this to understand the customer's history before briefing an agent.
    Input: customer name as a string.
    """
    df = _load_df()
    mask = df["customer_name"].str.lower().str.contains(customer_name.strip().lower(), na=False)
    history = df[mask].copy()
    if history.empty:
        mask2 = df["company"].str.lower().str.contains(customer_name.strip().lower(), na=False)
        history = df[mask2].copy()
    if history.empty:
        return f"No ticket history found for '{customer_name}'."
    history = history.sort_values("created_date", ascending=False)
    lines = [f"TICKET HISTORY — {history.iloc[0]['customer_name']} at {history.iloc[0]['company']}",
             f"Total tickets: {len(history)}\n"]
    for _, row in history.iterrows():
        csat = row['csat_score'] if pd.notna(row['csat_score']) else "N/A"
        icon = {"Closed":"✓","Open":"○","Escalated":"⚠"}.get(row['status'],"·")
        lines.append(f"{icon} {row['ticket_id']} | {row['created_date']} | {row['priority']} | {row['issue_type']} | {row['status']} | CSAT: {csat}")
        lines.append(f"  → {str(row['description'])[:120]}...")
        if pd.notna(row['resolution_notes']) and str(row['resolution_notes']) not in ["None","nan",""]:
            lines.append(f"  Resolution: {str(row['resolution_notes'])[:100]}")
        lines.append("")
    return "\n".join(lines)

@tool
def check_churn_risk_signals(ticket_id: str) -> str:
    """
    Checks a ticket against known churn risk indicators from CS policy.
    Use this to flag whether a customer needs urgent CSM attention.
    Input: ticket ID like TKT-1004
    """
    df = _load_df()
    row = df[df["ticket_id"] == ticket_id.strip().upper()]
    if row.empty:
        return f"Ticket {ticket_id} not found."
    r = row.iloc[0]
    level, signals = _assess_churn(r, df)
    plan_note = {
        "Enterprise": "ENTERPRISE account — churn impact is HIGH. Significant ARR at risk.",
        "Pro": "PRO account — moderate ARR impact if churned.",
    }.get(r["plan"], "STARTER account — lower ARR impact but monitor for pattern.")
    action_map = {
        "HIGH":   "Immediate CSM call required. Loop in team lead. Do not close without CSM sign-off.",
        "MEDIUM": "Flag for CSM review within 24 hours. Add account note.",
        "LOW":    "No immediate action required. Standard resolution flow."
    }
    return f"""CHURN RISK ANALYSIS — {ticket_id}
Customer:  {r['customer_name']} at {r['company']}
Plan:      {r['plan']}
{plan_note}

CHURN RISK LEVEL: {level}

SIGNALS DETECTED:
{chr(10).join(f'  • {s}' for s in signals)}

RECOMMENDED ACTION:
{action_map[level]}"""

@tool
def search_knowledge_base(query: str) -> str:
    """
    Searches the CS policy knowledge base using ChromaDB RAG.
    Use this to find escalation policies, SLA rules, or handling guidance.
    Input: natural language question about CS policies.
    """
    try:
        collection, embeddings = _get_kb_collection()
        query_vec = embeddings.embed_query(query)
        results = collection.query(query_embeddings=[query_vec], n_results=2)
        docs = results.get("documents", [[]])[0]
        if not docs:
            return "No relevant policy found for that query."
        output = [f"KB SEARCH — '{query}'\n"]
        for i, doc in enumerate(docs, 1):
            output.append(f"[Result {i}]\n{doc.strip()}\n")
        return "\n".join(output)
    except Exception:
        with open(KB_PATH, "r") as f:
            kb = f.read()
        sections = kb.split("===")
        keywords = query.lower().split()
        relevant = [s.strip() for s in sections if any(k in s.lower() for k in keywords)]
        if relevant:
            return f"KB SEARCH — '{query}'\n\n" + "\n\n---\n\n".join(relevant[:2])
        return f"No direct match for '{query}'. General escalation policy:\n\n" + (sections[1] if len(sections) > 1 else "Policy unavailable.")

@tool
def score_resolution_quality(ticket_id: str) -> str:
    """
    Scores the quality of a closed ticket's resolution on a scale of 1-10.
    Use this only on tickets with status Closed.
    Input: ticket ID like TKT-1001
    """
    df = _load_df()
    row = df[df["ticket_id"] == ticket_id.strip().upper()]
    if row.empty:
        return f"Ticket {ticket_id} not found."
    r = row.iloc[0]
    if r["status"] != "Closed":
        return f"Ticket {ticket_id} is {r['status']} — scoring only works on Closed tickets."
    res = str(r.get("resolution_notes", "")).lower()
    score = 5
    breakdown = []
    if any(p in res for p in ["identified","root cause","confirmed","found","discovered"]):
        score += 2; breakdown.append("+2 Root cause identified and documented")
    else:
        breakdown.append(" 0 Root cause not clearly documented")
    if any(p in res for p in ["confirmed","restored","working","resolved","fixed","applied"]):
        score += 1.5; breakdown.append("+1.5 Fix confirmed working")
    else:
        breakdown.append(" 0 Fix confirmation unclear")
    if any(p in res for p in ["permanent","sprint","scheduled","deployed","v2","next release"]):
        score += 1; breakdown.append("+1 Permanent fix timeline communicated")
    else:
        breakdown.append(" 0 No permanent fix mentioned")
    if any(p in res for p in ["prevent","monitor","measures","recurrence","avoid"]):
        score += 0.5; breakdown.append("+0.5 Preventative measures documented")
    else:
        breakdown.append(" 0 No preventative measures noted")
    try:
        csat = float(r["csat_score"])
        if csat <= 2:
            score -= 2; breakdown.append(f"-2 CSAT {csat} — very low satisfaction")
        elif csat == 3:
            score -= 1; breakdown.append(f"-1 CSAT {csat} — below threshold")
        elif csat >= 5:
            score += 0.5; breakdown.append(f"+0.5 CSAT {csat} — excellent")
        else:
            breakdown.append(f" 0 CSAT {csat} — acceptable")
    except (TypeError, ValueError):
        breakdown.append(" 0 CSAT not yet collected")
    score = max(1, min(10, round(score, 1)))
    label = "EXCELLENT" if score >= 8 else "GOOD" if score >= 6 else "NEEDS IMPROVEMENT" if score >= 4 else "POOR"
    rec = "No action required — strong resolution." if score >= 8 else "Team lead review recommended." if score >= 5 else "Immediate team lead review required — poor resolution, churn risk elevated."
    return f"""RESOLUTION QUALITY SCORE — {ticket_id}
Customer:  {r['customer_name']} at {r['company']} ({r['plan']})
Issue:     {r['issue_type']} | Priority: {r['priority']}

SCORE: {score}/10 — {label}

SCORING BREAKDOWN:
{chr(10).join(f'  {b}' for b in breakdown)}

RESOLUTION NOTES:
{r['resolution_notes']}

RECOMMENDATION: {rec}"""
