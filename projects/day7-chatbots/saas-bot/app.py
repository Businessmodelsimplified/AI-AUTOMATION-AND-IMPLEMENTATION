# app.py — LabTrack SaaS Support & Onboarding Bot
# Day 7 — AXIOM 60-Day AI Engineering Program
#
# CLIENT: SaaS companies needing support automation
#         specifically lab management, health tech SaaS
#
# PROBLEM SOLVED:
# 5-person support team handles 200+ weekly tickets.
# 70% are answered in the documentation.
# Ticket backlog consistently exceeds 48 hours.
#
# VALUE DELIVERED:
# 70% of tier-1 tickets resolved without human agent.
# Average resolution: 4 hours → under 2 minutes.
# PROJECT VALUE: $1,500–$4,000 build + $200/month maintain

import streamlit as st
from openai import OpenAI
import os

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

st.set_page_config(
    page_title="LabTrack Support",
    page_icon="🔬",
    layout="wide"
)

SYSTEM_PROMPT = """You are Atlas — the AI support assistant 
for LabTrack, a laboratory management SaaS platform used 
by pharmaceutical labs, clinical labs, and research 
institutions across East Africa.

ABOUT LABTRACK:
LabTrack helps labs manage sample tracking, test result 
recording, QC monitoring, equipment calibration schedules, 
and regulatory report generation.

PLANS & PRICING:
- Starter: KES 8,500/month — up to 5 users, basic features
- Professional: KES 18,000/month — up to 20 users, full features
- Enterprise: Custom pricing — unlimited users, custom integrations
- All plans: 14-day free trial, no credit card required

COMMON SUPPORT TOPICS YOU HANDLE:

ACCOUNT & BILLING:
- How to upgrade or downgrade plans
- Billing cycle explanation (monthly, 1st of each month)
- How to add or remove users
- Password reset and 2FA setup
- How to export data before cancelling

GETTING STARTED:
- How to create your first sample batch
- Setting up test methods and reference ranges
- Importing existing sample data from Excel
- Connecting barcode scanners and printers
- Setting up user roles and permissions

SAMPLE MANAGEMENT:
- How to receive, log and track samples
- Chain of custody documentation
- How to record and approve test results
- Handling sample rejection and re-testing
- Printing labels and reports

QC MONITORING:
- Setting up Levey-Jennings charts
- Westgard rules configuration
- QC failure investigation workflow
- Control sample management

REPORT GENERATION:
- Certificate of Analysis (CoA) templates
- Regulatory report formats (KPPB, EAC)
- Scheduled automated reports
- Exporting to PDF and Excel

INTEGRATIONS:
- LIMS API documentation
- Excel import/export
- Email notification setup
- Instrument interface connections

COMMON ERROR CODES:
- Error 4052: Session timeout — log in again
- Error 4071: File format not supported — use .xlsx or .csv
- Error 5001: Database sync issue — refresh and retry
- Error 5033: User permission denied — contact your admin

ESCALATION — when to involve human support:
- Data loss or corruption concerns → URGENT escalate
- Billing disputes → escalate to billing@labtrack.co.ke
- API/integration issues → escalate to tech@labtrack.co.ke
- Feature requests → log at feedback.labtrack.co.ke
- Anything you cannot resolve confidently

YOUR COMMUNICATION STYLE:
- Professional but approachable
- Step-by-step numbered instructions for technical help
- Always verify you solved the issue at the end
- Empathetic when customers are frustrated
- Proactive — offer related tips the user might not have asked about

RESPONSE FORMAT FOR TECHNICAL ISSUES:
1. Acknowledge the issue
2. Provide step-by-step solution
3. Explain why this happened (prevents recurrence)
4. Offer a related tip
5. Ask if the issue is resolved"""

# ── STYLING ───────────────────────────────────────────────────
st.markdown("""
<style>
    .saas-header {
        background: linear-gradient(135deg, #1565C0, #1976D2);
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        color: white;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .status-badge {
        background: #4CAF50;
        color: white;
        padding: 3px 10px;
        border-radius: 99px;
        font-size: 0.75rem;
        font-weight: 500;
    }
    .topic-card {
        background: var(--secondary-background-color);
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 0.6rem 0.8rem;
        font-size: 0.82rem;
        cursor: pointer;
        margin: 3px 0;
        transition: background 0.2s;
    }
</style>
""", unsafe_allow_html=True)

# ── HEADER ────────────────────────────────────────────────────
st.markdown("""
<div class="saas-header">
    <div>
        <h1 style="margin:0; font-size:1.4rem;">🔬 LabTrack Support</h1>
        <p style="margin:0.2rem 0 0; opacity:0.85; font-size:0.85rem;">
            Laboratory Management Platform
        </p>
    </div>
    <span class="status-badge">● All systems operational</span>
</div>
""", unsafe_allow_html=True)

# ── TWO COLUMN LAYOUT ─────────────────────────────────────────
chat_col, help_col = st.columns([3, 1])

with help_col:
    st.markdown("### 🔍 Browse Topics")

    topics = {
        "🚀 Getting Started": "How do I get started with LabTrack? Give me a quick setup guide.",
        "👥 User Management": "How do I add new users and set their permissions?",
        "🧪 Sample Tracking": "How do I create and track a new sample batch?",
        "📊 QC Monitoring": "How do I set up quality control monitoring and Levey-Jennings charts?",
        "📄 Reports & CoA": "How do I generate a Certificate of Analysis report?",
        "🔌 Integrations": "What integrations does LabTrack support and how do I set them up?",
        "💳 Billing & Plans": "How does billing work and how do I upgrade my plan?",
        "🔑 Password Reset": "How do I reset my password or set up two-factor authentication?"
    }

    if "saas_quick_q" not in st.session_state:
        st.session_state.saas_quick_q = None

    for topic, question in topics.items():
        if st.button(topic, key=topic, use_container_width=True):
            st.session_state.saas_quick_q = question

    st.markdown("---")
    st.markdown("**📞 Contact Support**")
    st.markdown("""
    **Email:** support@labtrack.co.ke

    **Response time:** < 4 hours

    **Emergency:** +254 700 111 000

    **Hours:** Mon–Fri 8am–6pm EAT
    """)

    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.saas_messages = []
        st.rerun()

with chat_col:
    # ── MEMORY ───────────────────────────────────────────────
    if "saas_messages" not in st.session_state:
        st.session_state.saas_messages = []

    # ── WELCOME ───────────────────────────────────────────────
    if not st.session_state.saas_messages:
        with st.chat_message("assistant", avatar="🔬"):
            st.markdown("""
Hi there! I'm **Atlas**, LabTrack's AI support assistant.

I can help you with:
- ⚙️ **Setup & configuration** — getting LabTrack working for your lab
- 🧪 **Sample management** — tracking, testing, and results generation
- 📊 **QC monitoring** — Levey-Jennings, Westgard rules, control charts
- 📄 **Reports** — CoA generation, regulatory formats, scheduled exports
- 💳 **Account & billing** — plans, users, and payments
- 🔌 **Integrations** — instruments, Excel, APIs

What can I help you with today?
            """)

    # ── HISTORY ──────────────────────────────────────────────
    for msg in st.session_state.saas_messages:
        avatar = "🔬" if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    # ── INPUT ─────────────────────────────────────────────────
    default_q = st.session_state.saas_quick_q or ""
    if st.session_state.saas_quick_q:
        st.session_state.saas_quick_q = None

    user_input = st.chat_input(
        "Describe your issue or ask a question..."
    ) or default_q

    if user_input:
        st.session_state.saas_messages.append({
            "role": "user", "content": user_input
        })
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)

        with st.chat_message("assistant", avatar="🔬"):
            with st.spinner("Atlas is checking the knowledge base..."):
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT}
                    ] + st.session_state.saas_messages,
                    max_tokens=500,
                    temperature=0.4
                )
                reply = response.choices[0].message.content
            st.markdown(reply)

        st.session_state.saas_messages.append({
            "role": "assistant", "content": reply
        })

st.markdown("""
---
<div style='text-align:center; color:#999; font-size:0.78rem;'>
LabTrack · Laboratory Management System Platform · 
support@labtrack.co.ke · Built by Elvis Justus AI Automation
</div>
""", unsafe_allow_html=True)