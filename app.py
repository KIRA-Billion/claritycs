"""
app.py — ClarityCS Streamlit Frontend
Run with: python -m streamlit run app.py
"""
import os
import streamlit as st
import pandas as pd

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="ClarityCS — AI CX Intelligence",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #4f2d7f 100%);
        padding: 2rem 2.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
    }
    .output-box {
        background: #0f0f1a;
        border-left: 4px solid #7c3aed;
        border-radius: 0 8px 8px 0;
        padding: 1.5rem;
        margin-top: 1rem;
        font-family: 'Courier New', monospace;
        white-space: pre-wrap;
        line-height: 1.8;
        color: #e2e8f0;
    }
    .kb-badge {
        background: #1a2e1a;
        border: 1px solid #2d6a2d;
        border-radius: 6px;
        padding: 0.4rem 0.8rem;
        font-size: 0.8rem;
        color: #6fcf97;
        display: inline-block;
        margin-top: 0.5rem;
    }
    .upload-section {
        background: #1a1a2e;
        border: 1px dashed #4f2d7f;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ── Load ticket data ──────────────────────────────────────────
@st.cache_data
def load_tickets():
    return pd.read_csv("data/sample_tickets.csv")

df = load_tickets()

# ── Knowledge base session state ─────────────────────────────
if "kb_docs" not in st.session_state:
    st.session_state.kb_docs = []
if "kb_names" not in st.session_state:
    st.session_state.kb_names = []

# ── Header ────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1 style='color: white; margin: 0; font-size: 2.2rem;'>🎯 ClarityCS</h1>
    <p style='color: #c4b5fd; margin: 0.4rem 0 0 0; font-size: 1.1rem;'>
        AI-Powered CX Intelligence — Agent Pre-Briefing & Resolution Quality Analysis
    </p>
    <p style='color: #7c3aed; margin: 0.3rem 0 0 0; font-size: 0.85rem;'>
        LangChain · ChromaDB · Groq / Llama 3.1 · HuggingFace Embeddings · Streamlit
    </p>
</div>
""", unsafe_allow_html=True)

# ── Metrics row ───────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("AHT Saved Per Ticket", "3–5 min", help="Time agents spend reading history before each ticket")
with col2:
    st.metric("Daily Capacity Saved", "10–16 hrs", help="At 200 tickets/day across a team")
with col3:
    st.metric("Ticket Deflection", "65%", help="RAG-based ops assistant simulation")
with col4:
    st.metric("Churn Risk Detection", "Pre-escalation", help="Catches bad resolutions before customers escalate")

st.markdown("---")

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📋 Available Tickets")
    st.caption("15 realistic enterprise scenarios")

    status_filter = st.selectbox("Filter by Status", ["All", "Open", "Closed", "Escalated"])
    filtered_df = df if status_filter == "All" else df[df["status"] == status_filter]
    st.dataframe(
        filtered_df[["ticket_id", "customer_name", "priority", "status"]],
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    # ── Document uploader ─────────────────────────────────────
    st.markdown("### 📂 Upload Your Documents")
    st.caption("Upload your own CS policies, SLAs, or ticket data to ground the AI in your company's context.")

    uploaded_docs = st.file_uploader(
        "Upload SOPs, policies, or ticket CSVs",
        type=["pdf", "txt", "md", "csv"],
        accept_multiple_files=True,
        key="doc_uploader",
        help="Supported: PDF, TXT, MD, CSV. The AI will use these as context when generating briefs and analysis."
    )

    if uploaded_docs:
        new_names = []
        new_docs = []
        for f in uploaded_docs:
            if f.name not in st.session_state.kb_names:
                content = ""
                if f.name.endswith(".csv"):
                    try:
                        df_upload = pd.read_csv(f)
                        content = df_upload.to_string(index=False)
                    except Exception:
                        content = f.read().decode("utf-8", errors="ignore")
                else:
                    try:
                        content = f.read().decode("utf-8", errors="ignore")
                    except Exception:
                        content = ""
                if content:
                    new_docs.append({"name": f.name, "content": content})
                    new_names.append(f.name)

        if new_docs:
            st.session_state.kb_docs.extend(new_docs)
            st.session_state.kb_names.extend(new_names)

    if st.session_state.kb_names:
        st.markdown("**Active in knowledge base:**")
        for name in st.session_state.kb_names:
            st.markdown(f'<div class="kb-badge">📄 {name}</div>', unsafe_allow_html=True)
        if st.button("🗑 Clear uploaded documents", key="clear_kb"):
            st.session_state.kb_docs = []
            st.session_state.kb_names = []
            st.rerun()
    else:
        st.caption("No documents uploaded — using built-in CS policy knowledge base.")

    st.markdown("---")
    st.markdown("### 🎯 Suggested Tests")
    st.markdown("""
**Pre-Brief (dramatic results):**
- `TKT-1004` — Data loss, compliance risk
- `TKT-1010` — CEO involved, 5 critical tickets
- `TKT-1012` — SLA breach, penalty clause

**Resolution Analysis:**
- `TKT-1007` — Poor resolution (score 4–5)
- `TKT-1001` — Good resolution (score 8–9)
- `TKT-1002` — Excellent resolution (score 9+)
    """)

    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.caption(
        "Demo uses Groq free-tier API (Llama 3.1) with simulated enterprise data. "
        "Production connects to live Zendesk, Freshdesk, or JIRA APIs."
    )
    st.markdown(
        "Built by [Bitan Basu](https://github.com/KIRA-Billion) · "
        "[NexusCS Platform](https://kira-billion.github.io/nexuscs)"
    )

# ── Helper: build context from uploaded docs ──────────────────
def _uploaded_context() -> str:
    if not st.session_state.kb_docs:
        return ""
    parts = ["\n\n=== UPLOADED DOCUMENTS (use these as additional context) ===\n"]
    for doc in st.session_state.kb_docs:
        parts.append(f"\n--- {doc['name']} ---\n{doc['content'][:3000]}\n")
    return "".join(parts)

# ── Main tabs ─────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "🧠 Agent Pre-Brief",
    "🔍 Resolution Analyser",
    "📖 How It Works"
])

# ── TAB 1 — Agent Pre-Briefing ────────────────────────────────
with tab1:
    st.subheader("Agent Pre-Briefing — Know Before You Open")

    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.markdown("""
        **The Problem:** Agents spend 3–5 minutes reading ticket history before every interaction.
        At 200 tickets/day that's 10–16 hours of wasted senior capacity — every single day.

        **The Solution:** Enter a ticket ID. ClarityCS retrieves history, checks churn risk signals
        against CS policy, and generates a structured 30-second brief before the agent opens the ticket.
        """)
    with col_b:
        st.info("💡 Try **TKT-1004** first — it produces the most dramatic output showing compliance risk and HIGH churn detection.")

    if st.session_state.kb_names:
        st.success(f"📂 Using your uploaded documents: {', '.join(st.session_state.kb_names)}")

    st.markdown("---")

    col1, col2 = st.columns([3, 1])
    with col1:
        ticket_id_brief = st.text_input(
            "Enter Ticket ID",
            placeholder="e.g. TKT-1004",
            key="brief_input",
            label_visibility="collapsed"
        )
    with col2:
        run_brief = st.button("🧠 Generate Brief", type="primary", key="brief_btn", use_container_width=True)

    if ticket_id_brief:
        preview = df[df["ticket_id"] == ticket_id_brief.strip().upper()]
        if not preview.empty:
            row = preview.iloc[0]
            priority_color = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}.get(row["priority"], "⚪")
            st.caption(
                f"{priority_color} **{row['customer_name']}** at {row['company']} "
                f"({row['plan']}) — {row['issue_type']} — Status: {row['status']}"
            )

    if run_brief and ticket_id_brief:
        ticket_clean = ticket_id_brief.strip().upper()
        with st.spinner(f"Analysing {ticket_clean} — retrieving history, checking risk signals, searching policy knowledge base..."):
            try:
                from agents.briefing_agent import generate_brief
                extra_context = _uploaded_context()
                result = generate_brief(ticket_clean + extra_context if extra_context else ticket_clean)
                st.success("✅ Brief ready — share with agent before they open the ticket")
                st.markdown("---")
                st.markdown(f"<div class='output-box'>{result}</div>", unsafe_allow_html=True)
                st.download_button(
                    label="📥 Download Brief",
                    data=result,
                    file_name=f"brief_{ticket_clean}.txt",
                    mime="text/plain"
                )
            except Exception as e:
                err = str(e)
                st.error(f"Error: {err}")
                if "GROQ_API_KEY" in err or "NoneType" in err:
                    st.warning(
                        "⚠️ API key issue detected.\n\n"
                        "**Local:** Add `GROQ_API_KEY=gsk_...` to your `.env` file in the project root.\n\n"
                        "**Streamlit Cloud:** Go to App Settings → Secrets and add:\n```\nGROQ_API_KEY = \"gsk_...\"\n```"
                    )
    elif run_brief:
        st.warning("Please enter a ticket ID from the sidebar list.")

# ── TAB 2 — Resolution Analyser ───────────────────────────────
with tab2:
    st.subheader("Post-Interaction Quality Analysis")

    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.markdown("""
        **The Problem:** Most CS teams never review closed tickets unless a customer
        complains again. Bad resolutions sit undetected until they become churned accounts.

        **The Solution:** Enter a closed ticket ID. ClarityCS scores resolution quality
        1–10 against policy standards, flags churn risk patterns, and recommends
        one specific team lead action — before the customer escalates.
        """)
    with col_b:
        st.info("💡 Try **TKT-1007** for a poor resolution, then **TKT-1002** for a good one — see how the scoring differs.")

    if st.session_state.kb_names:
        st.success(f"📂 Scoring against your uploaded documents: {', '.join(st.session_state.kb_names)}")

    st.markdown("---")

    col1, col2 = st.columns([3, 1])
    with col1:
        ticket_id_analyse = st.text_input(
            "Enter Closed Ticket ID",
            placeholder="e.g. TKT-1001",
            key="analyse_input",
            label_visibility="collapsed"
        )
    with col2:
        run_analyse = st.button("🔍 Analyse Resolution", type="primary", key="analyse_btn", use_container_width=True)

    if ticket_id_analyse:
        preview = df[df["ticket_id"] == ticket_id_analyse.strip().upper()]
        if not preview.empty:
            row = preview.iloc[0]
            if row["status"] != "Closed":
                st.warning(
                    f"⚠️ Ticket **{ticket_id_analyse.upper()}** is **{row['status']}** — not Closed. "
                    "Try: TKT-1001, TKT-1002, TKT-1005, TKT-1007, TKT-1009, TKT-1011, TKT-1013"
                )
            else:
                st.caption(
                    f"✅ **{row['customer_name']}** at {row['company']} "
                    f"({row['plan']}) — {row['issue_type']} — CSAT: {row['csat_score']}"
                )

    if run_analyse and ticket_id_analyse:
        ticket_clean = ticket_id_analyse.strip().upper()
        ticket_row = df[df["ticket_id"] == ticket_clean]
        if not ticket_row.empty and ticket_row.iloc[0]["status"] != "Closed":
            pass
        else:
            with st.spinner(f"Scoring resolution quality for {ticket_clean}..."):
                try:
                    from agents.analyser_agent import analyse_ticket
                    extra_context = _uploaded_context()
                    result = analyse_ticket(ticket_clean + extra_context if extra_context else ticket_clean)
                    st.success("✅ Analysis complete")
                    st.markdown("---")
                    st.markdown(f"<div class='output-box'>{result}</div>", unsafe_allow_html=True)
                    st.download_button(
                        label="📥 Download Analysis",
                        data=result,
                        file_name=f"analysis_{ticket_clean}.txt",
                        mime="text/plain"
                    )
                except Exception as e:
                    err = str(e)
                    st.error(f"Error: {err}")
                    if "GROQ_API_KEY" in err or "NoneType" in err:
                        st.warning(
                            "⚠️ API key issue.\n\n"
                            "**Local:** Add `GROQ_API_KEY=gsk_...` to your `.env` file.\n\n"
                            "**Streamlit Cloud:** App Settings → Secrets → add `GROQ_API_KEY = \"gsk_...\"`"
                        )
    elif run_analyse:
        st.warning("Please enter a ticket ID.")

# ── TAB 3 — How It Works ──────────────────────────────────────
with tab3:
    st.subheader("The Business Problem ClarityCS Solves")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🧠 Problem 1 — Agent Context Collapse")
        st.markdown("""
        Every CS agent spends **3–5 minutes reading history** before opening a ticket.
        At 200 tickets per day across a team, that's **10–16 hours of senior
        capacity lost daily** to reading, not resolving.

        ClarityCS eliminates this entirely. The brief is ready before the agent opens the ticket.

        **ROI:** At ₹800/hr agent cost, 10 hours/day saved = ₹8,000/day = **₹24 lakhs/year**.
        """)
    with col2:
        st.markdown("#### 🔍 Problem 2 — Invisible Bad Resolutions")
        st.markdown("""
        When a ticket closes, nothing happens. Bad resolutions sit undetected
        until the customer cancels their contract.

        For Enterprise accounts, **one churned account = ₹50–500 lakhs in lost ARR**.

        ClarityCS automatically scores every closed ticket and flags the ones
        that need a team lead look — before the customer escalates.

        **ROI:** Catching one at-risk Enterprise account per quarter covers the cost
        of an entire AI automation hire.
        """)

    st.markdown("---")

    st.markdown("#### 📂 Upload Your Own Documents")
    st.markdown("""
    Use the **sidebar uploader** to add your company's actual documents:
    - **CS policy PDFs** → grounds churn risk detection in your real escalation rules
    - **SLA agreements** → scores resolution quality against your actual commitments
    - **Ticket CSV exports** → replaces the demo data with your real ticket history

    The AI reads your uploaded documents and uses them as context — every brief
    and analysis becomes specific to your company, not generic best practices.
    """)

    st.markdown("---")
    st.markdown("#### 🏗️ How the System Works")
    st.markdown("""
    ClarityCS uses a **multi-tool LangChain agent** where the model decides
    which tools to call, in what order, based on the task.

    For each ticket, the agent:
    1. Retrieves structured ticket data and full customer history
    2. Checks against churn risk signals defined in CS policy
    3. Searches a knowledge base of CS policies using RAG (Retrieval-Augmented Generation)
    4. Synthesises everything into a structured, actionable output

    In production, the data layer connects directly to **Zendesk, Freshdesk,
    JIRA, or Salesforce APIs** — replacing the CSV with live ticket data.
    The agent logic, RAG system, and output format remain identical.
    """)

    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Tech Stack**")
        st.markdown("""
        - LangChain (agent orchestration)
        - ChromaDB (vector storage / RAG)
        - Groq / Llama 3.1 (LLM reasoning)
        - HuggingFace Embeddings (local)
        - Streamlit (interface)
        - Python / Pandas (data layer)
        """)
    with col2:
        st.markdown("**Integration Ready For**")
        st.markdown("""
        - Zendesk REST API
        - Freshdesk REST API
        - JIRA Service Management
        - Salesforce Cases API
        - ServiceNow Incidents
        - Any webhook-based platform
        """)
    with col3:
        st.markdown("**Built By**")
        st.markdown("""
        **Bitan Basu**
        AI CX Automation Specialist

        8+ years enterprise CS Ops
        HP Inc. · Replicon (Deltek)

        [GitHub](https://github.com/KIRA-Billion) · [NexusCS](https://kira-billion.github.io/nexuscs) · [Email](mailto:bitan1basu@gmail.com)
        """)

# ── Footer ────────────────────────────────────────────────────
st.markdown("---")
st.caption(
    "ClarityCS v1.1 · LangChain multi-agent system for CX workflow automation · "
    "Built by Bitan Basu · "
    "Demo uses Groq free-tier API with simulated enterprise data · "
    "Production version connects to live ticketing APIs"
)
