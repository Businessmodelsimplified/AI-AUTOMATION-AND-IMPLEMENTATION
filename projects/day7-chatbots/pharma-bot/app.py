# app.py — Pharmaceutical Compliance Assistant
# Day 7 — AXIOM 60-Day AI Engineering Program
#
# CLIENT: Pharmaceutical manufacturers, distributors,
#         importers regulated by KPPB in East Africa
#
# PROBLEM SOLVED:
# Compliance teams spend 2-4 hours daily searching
# regulatory documents and SOPs to answer internal
# questions about GMP, documentation, and quality systems.
#
# VALUE DELIVERED:
# Instant answers to compliance questions with context.
# Reduces compliance query time from hours to seconds.
# PROJECT VALUE: $2,000–$6,000 build + $200/month maintain

import streamlit as st
from openai import OpenAI
import os

# ── LOAD API KEY ─────────────────────────────────────────────
# Works both locally and on Streamlit Cloud
# Works on Streamlit Cloud (reads from Secrets)
# AND works locally (reads from .env file)
try:
    api_key = st.secrets["OPENAI_API_KEY"]
except Exception:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=r"C:\Users\pc\ai-engineering\.env")
    api_key = os.getenv("OPENAI_API_KEY")

# Final safety check
if not api_key:
    st.error("""
    ⚠️ **API Key Missing**
    
    If you are the developer:
    - **Streamlit Cloud:** Add OPENAI_API_KEY in App Settings → Secrets
    - **Local:** Add OPENAI_API_KEY to your .env file
    """)
    st.stop()

client = OpenAI(api_key=api_key)

# ── PAGE CONFIGURATION ────────────────────────────────────────
st.set_page_config(
    page_title="PharmaCompliance AI",
    page_icon="⚗️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ── SYSTEM PROMPT — THE BRAIN OF THIS CHATBOT ─────────────────
# This is what you customise per client.
# Your chemistry background makes this prompt more accurate
# than anything a generic AI engineer would write.

SYSTEM_PROMPT = """You are PharmAssist — an expert pharmaceutical
compliance AI for companies regulated by KPPB and WHO-GMP in
East Africa.

YOUR EXPERTISE:
- WHO-GMP requirements (TRS 986, 992, 1010)
- KPPB Pharmacy and Poisons Act (Cap 244)
- ICH Guidelines Q8, Q9, Q10
- EAC Pharmaceutical Regulatory Harmonisation
- USP and British Pharmacopoeia standards
- Cold chain management and temperature monitoring
- Batch manufacturing records and quality systems
- Pharmacovigilance and adverse event reporting

REASONING APPROACH — CHAIN OF THOUGHT:
For every compliance question follow this reasoning process:

Step 1 — IDENTIFY: What specific regulation or guideline applies?
Step 2 — REQUIREMENT: What exactly does that regulation require?
Step 3 — GAP: What might be missing or non-compliant?
Step 4 — RISK: What is the consequence of non-compliance?
Step 5 — ACTION: What specific steps must be taken?

RESPONSE FORMAT — use this exact structure:

## 📋 Regulatory Basis
[Cite the specific regulation, section, and requirement]

## ✅ What is Required
[Exactly what must be done or documented]

## ⚠️ Common Compliance Gaps
[What organisations typically get wrong in this area]

## 🎯 Action Items
[Numbered list of specific steps to achieve compliance]

## 📅 Timeline Recommendation
[Realistic timeline for implementation]

---
*Reference: [Regulation name and section]*

CRITICAL RULES:
- Never guess on regulatory requirements — say clearly if uncertain
- Always cite the specific regulation and section number
- Flag HIGH RISK items with ⚠️ WARNING
- If a question requires product-specific regulatory advice,
  recommend engaging a qualified Regulatory Affairs professional
- Temperature is set to 0.2 — you should be consistent and precise"""

# ── CUSTOM STYLING ────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1a237e, #283593);
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 1.5rem;
        color: white;
    }
    .disclaimer {
        background: #fff3e0;
        border-left: 4px solid #ff6f00;
        padding: 0.75rem 1rem;
        border-radius: 0 8px 8px 0;
        font-size: 0.85rem;
        color: #e65100;
        margin-bottom: 1rem;
    }
    .quick-btn {
        font-size: 0.8rem;
        margin: 0.2rem;
    }
</style>
""", unsafe_allow_html=True)

# ── HEADER ────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1 style="margin:0; font-size:1.6rem;">⚗️ PharmaCompliance AI</h1>
    <p style="margin:0.4rem 0 0; opacity:0.85; font-size:0.9rem;">
        GMP · KPPB Regulatory · Quality Systems · Documentation
    </p>
</div>
""", unsafe_allow_html=True)

# ── COMPLIANCE DISCLAIMER ─────────────────────────────────────
st.markdown("""
<div class="disclaimer">
    ⚠️ <strong>Regulatory Guidance Tool:</strong> Responses are 
    based on published GMP and KPPB standards. Always verify 
    critical compliance decisions against current official 
    documentation and qualified regulatory expertise.
</div>
""", unsafe_allow_html=True)

# ── QUICK QUESTION BUTTONS ────────────────────────────────────
# These are the most common questions compliance teams ask.
# Clicking them pre-fills the chat input.
st.markdown("**Common compliance questions:**")

col1, col2, col3 = st.columns(3)
quick_questions = {
    "col1": [
        "Cold chain deviation procedure",
        "SOP documentation requirements"
    ],
    "col2": [
        "Batch record retention period",
        "KPPB import permit process"
    ],
    "col3": [
        "Out of spec investigation steps",
        "GMP audit preparation checklist"
    ]
}

# Store selected quick question in session state
if "quick_q" not in st.session_state:
    st.session_state.quick_q = None

with col1:
    for q in quick_questions["col1"]:
        if st.button(q, key=q, use_container_width=True):
            st.session_state.quick_q = q

with col2:
    for q in quick_questions["col2"]:
        if st.button(q, key=q, use_container_width=True):
            st.session_state.quick_q = q

with col3:
    for q in quick_questions["col3"]:
        if st.button(q, key=q, use_container_width=True):
            st.session_state.quick_q = q

st.markdown("---")

# ── CONVERSATION MEMORY ───────────────────────────────────────
if "pharma_messages" not in st.session_state:
    st.session_state.pharma_messages = []

# ── WELCOME MESSAGE ───────────────────────────────────────────
if not st.session_state.pharma_messages:
    with st.chat_message("assistant", avatar="⚗️"):
        st.markdown("""
Hello! I'm **PharmAssist** — your pharmaceutical compliance AI.

I can help your team with:

**📋 Documentation & Records**
GMP batch records, SOP structure, deviation reports

**🏭 Quality Systems**
QA/QC requirements, validation protocols, equipment qualification

**📜 Regulatory Affairs**
KPPB registration, WHO-GMP compliance, import requirements

**⚠️ Quality Events**
Out-of-spec investigations, recalls, CAPA procedures

What compliance question can I help you with today?
        """)

# ── DISPLAY HISTORY ───────────────────────────────────────────
for msg in st.session_state.pharma_messages:
    avatar = "⚗️" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# ── HANDLE INPUT ──────────────────────────────────────────────
# Use quick question if selected, otherwise use typed input
default_input = st.session_state.quick_q or ""
if st.session_state.quick_q:
    st.session_state.quick_q = None

user_input = st.chat_input(
    "Ask a compliance question...",
    key="pharma_input"
) or default_input

if user_input:
    st.session_state.pharma_messages.append({
        "role": "user",
        "content": user_input
    })
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    messages_to_send = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ] + st.session_state.pharma_messages

    with st.chat_message("assistant", avatar="⚗️"):
        with st.spinner("Checking regulatory references..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages_to_send,
                max_tokens=600,
                temperature=0.3  # Low temperature for factual compliance info
            )
            reply = response.choices[0].message.content
        st.markdown(reply)

    st.session_state.pharma_messages.append({
        "role": "assistant",
        "content": reply
    })

# ── SIDEBAR INFO ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("### About PharmAssist")
    st.markdown("""
    Built for pharmaceutical companies operating under:
    - **KPPB** regulations (Kenya)
    - **WHO-GMP** standards
    - **EAC** harmonised guidelines
    - **ICH** technical guidelines

    ---
    **Need a custom compliance system?**

    Contact: elvisjustus18@gmail.com

    *Built by Elvis Justus — AI Automation Engineer*
    """)

    if st.button("🗑️ Clear conversation"):
        st.session_state.pharma_messages = []
        st.rerun()

# ── FOOTER ────────────────────────────────────────────────────
st.markdown("""
---
<div style='text-align:center; color:#999; font-size:0.78rem;'>
PharmaCompliance AI · Powered by OpenAI GPT-4 · 
Built by Elvis Justus AI Automation<br>
<em>For verified compliance decisions, always consult 
qualified regulatory professionals and current KPPB guidelines</em>
</div>
""", unsafe_allow_html=True)