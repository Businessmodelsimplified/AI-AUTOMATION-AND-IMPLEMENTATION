# app.py — NutriCore Health Supplements Support Bot
# Day 7 — AXIOM 60-Day AI Engineering Program
#
# CLIENT: Health supplement e-commerce brands
#         Fitness coaching businesses
#         Wellness product companies
#
# PROBLEM SOLVED:
# Supplement brands receive 100-200 customer questions daily
# about ingredients, dosing, compatibility, and delivery.
# Staff spend 3+ hours answering repetitive questions.
#
# VALUE DELIVERED:
# 24/7 instant responses. Staff focus on sales and strategy.
# PROJECT VALUE: $800–$2,500 build + $150/month maintain

import streamlit as st
from openai import OpenAI
import os
from datetime import datetime
import uuid
import json
from collections import Counter
import re

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

# ── SESSION TRACKING ─────────────────────────────────────────
# Each browser session gets a unique ID.
# This lets you track conversations per customer visit.
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]

if "full_conversation_log" not in st.session_state:
    st.session_state.full_conversation_log = []
if "captured_leads" not in st.session_state:
    st.session_state.captured_leads = []

if "lead_capture_stage" not in st.session_state:
    st.session_state.lead_capture_stage = None

if "lead_name" not in st.session_state:
    st.session_state.lead_name = None

if "lead_interest" not in st.session_state:
    st.session_state.lead_interest = None

st.set_page_config(
    page_title="NutriCore Health — Support",
    page_icon="🌿",
    layout="centered"
)
# ── LEAD CAPTURE SYSTEM ───────────────────────────────────────
# Detects when a customer is interested in buying.
# Prompts them for contact details naturally.
# Saves captured leads to session state.
# Business owner downloads leads as CSV for follow-up.

# Keywords that signal a customer wants to buy
PURCHASE_INTENT_KEYWORDS = [
    "how do i order", "how to order", "how can i order",
    "where do i buy", "where can i buy", "want to buy",
    "i want to purchase", "i want to order", "place an order",
    "how do i pay", "how to pay", "payment", "m-pesa",
    "paybill", "mpesa", "how much does", "what is the price",
    "price of", "cost of", "how much is", "do you have",
    "is it available", "in stock", "can i get",
    "i need", "i want", "interested in buying",
    "same day delivery", "next day delivery",
    "delivery to", "ship to", "send to"
]

# Keywords that look like contact information
CONTACT_PATTERNS = [
    r'07\d{8}',           # Kenyan mobile starting with 07
    r'01\d{8}',           # Kenyan mobile starting with 01
    r'\+254\d{9}',        # International format
    r'254\d{9}',          # Without plus
    r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',  # Email
]


def detect_purchase_intent(customer_message):
    """
    Checks if a customer message signals they want to buy.
    Returns True if purchase intent is detected.
    """
    message_lower = customer_message.lower()
    for keyword in PURCHASE_INTENT_KEYWORDS:
        if keyword in message_lower:
            return True
    return False


def detect_contact_info(customer_message):
    """
    Checks if a customer message contains contact information.
    Returns the contact info if found, None if not.
    This runs after we have prompted them for their details.
    """
    for pattern in CONTACT_PATTERNS:
        match = re.search(pattern, customer_message)
        if match:
            return match.group()
    return None


def save_lead(name, contact, interest, conversation_context):
    """
    Saves a captured lead to session state.
    In production this also writes to Google Sheets
    and sends email notification to the sales team.
    """
    if "captured_leads" not in st.session_state:
        st.session_state.captured_leads = []

    lead = {
        "date": datetime.now().strftime("%d/%m/%Y"),
        "time": datetime.now().strftime("%H:%M:%S"),
        "session_id": st.session_state.session_id,
        "name": name,
        "contact": contact,
        "interest": interest,
        "context": conversation_context[:200],
        "status": "New Lead",
        "source": "NutriCore Health Bot — Zuri"
    }

    st.session_state.captured_leads.append(lead)
    return lead
# ── URGENT ALERT SYSTEM ───────────────────────────────────────
# These keywords trigger an immediate warning to the customer
# AND log an urgent flag so the business owner can follow up.
# In production this also sends an email via Gmail API or Zapier.

URGENT_KEYWORDS = [
    # Severe physical symptoms
    "chest pain", "difficulty breathing", "cant breathe",
    "cannot breathe", "heart attack", "stroke", "unconscious",
    "fainted", "seizure", "convulsion",
    # Severe allergic reactions
    "allergic reaction", "anaphylaxis", "throat swelling",
    "swelling throat", "hives all over", "severe rash",
    # Overdose or poisoning concerns
    "overdose", "took too many", "too many pills",
    "accidental ingestion", "poisoning", "swallowed wrong",
    # Pregnancy emergencies
    "bleeding during pregnancy", "severe cramps pregnant",
    # General emergency language
    "emergency", "ambulance", "hospital now", "dying",
    "passing out", "blacking out"
]

def check_urgent(customer_message):
    """
    Scans a customer message for urgent health keywords.
    Returns True if urgent, False if normal.

    This runs on EVERY message before the AI responds.
    Speed matters — it must be instant.
    """
    message_lower = customer_message.lower()

    # Check each urgent keyword
    for keyword in URGENT_KEYWORDS:
        if keyword in message_lower:
            return True, keyword  # Return True and which keyword matched

    return False, None


def log_urgent_alert(customer_message, keyword_matched):
    """
    Logs the urgent alert to session state.
    In production this also:
    - Sends email to business owner via Gmail API
    - Posts to Slack channel
    - Creates urgent ticket in CRM
    All of those are Day 9 additions.
    """
    if "urgent_alerts" not in st.session_state:
        st.session_state.urgent_alerts = []

    alert = {
        "date": datetime.now().strftime("%d/%m/%Y"),
        "time": datetime.now().strftime("%H:%M:%S"),
        "session_id": st.session_state.session_id,
        "customer_message": customer_message,
        "keyword_matched": keyword_matched,
        "status": "Unreviewed"
    }

    st.session_state.urgent_alerts.append(alert)

    # Return the alert for logging
    return alert
# ── LOGGING FUNCTION ──────────────────────────────────────────
# This runs after every AI response.
# It saves the conversation to session state.
# The sidebar reads from this data to show the dashboard.
# In production you would also write this to Google Sheets.

def log_conversation(customer_message, bot_response, category="general"):
    """
    Saves every conversation exchange to the session log.

    Parameters:
        customer_message — what the customer typed
        bot_response     — what the AI replied
        category         — type of question (auto-detected)
    """
    # Auto-detect category from keywords in the message
    message_lower = customer_message.lower()

    if any(word in message_lower for word in
           ["price", "cost", "how much", "ksh", "kes"]):
        category = "pricing"
    elif any(word in message_lower for word in
             ["deliver", "ship", "nairobi", "kisumu", "mombasa"]):
        category = "delivery"
    elif any(word in message_lower for word in
             ["order", "buy", "purchase", "mpesa", "payment"]):
        category = "ordering"
    elif any(word in message_lower for word in
             ["protein", "collagen", "vitamin", "supplement",
              "weight", "muscle"]):
        category = "product_question"
    elif any(word in message_lower for word in
             ["diabetic", "pregnant", "allergy", "medical",
              "doctor", "medication"]):
        category = "health_advice"
    else:
        category = "general"

    # Build the log entry
    log_entry = {
    "date": datetime.now().strftime("%d/%m/%Y"),
    "time": datetime.now().strftime("%H:%M:%S"),
    "session_id": st.session_state.session_id,
    "customer_message": customer_message,
    "bot_response_preview": bot_response[:150] + "...",
    "category": category,
    "bot_name": "NutriCore Health Bot — Zuri"
}

    # Add to session log
    st.session_state.full_conversation_log.append(log_entry)

    # Return category so we can use it later
    return category
SYSTEM_PROMPT = """You are Zuri — the friendly and knowledgeable 
AI wellness assistant for NutriCore Health, a premium health 
supplements company based in Nairobi, Kenya.

ABOUT NUTRICORE HEALTH:
Our product range includes:
- **Protein Supplements:** Whey protein, plant protein, casein
  Available in: Chocolate, Vanilla, Strawberry, Unflavoured
  Sizes: 1kg (KES 3,500), 2kg (KES 6,200), 5kg (KES 13,500)
- **Vitamins & Minerals:** Vitamin D3, B-Complex, Zinc, Magnesium,
  Iron supplements, Multivitamins for men/women
- **Collagen:** Marine collagen, Bovine collagen peptides
  Popular for: Skin, joints, gut health
- **Weight Management:** Fat burners, appetite suppressants,
  meal replacement shakes
- **Energy & Performance:** Pre-workout, creatine, BCAAs
- **Wellness:** Omega-3, probiotics, ashwagandha, turmeric

DELIVERY & ORDERING:
- Nairobi same-day delivery: Orders before 12pm (KES 200)
- Nairobi next-day delivery: KES 150
- Countrywide Kenya: 2-3 business days (KES 350)
- International: DHL available on request
- Minimum order: No minimum
- Payment: M-Pesa (0793 775 356), Visa/Mastercard, Cash on delivery
- WhatsApp orders: +254 793 775 356

YOUR PERSONALITY AS ZURI:
- Warm, knowledgeable and encouraging
- Speak in clear, jargon-free language
- Use Swahili greetings naturally (Habari, Sawa, Asante)
- Address customers by name when they share it
- Always be honest — never oversell or make unrealistic claims

HEALTH GUIDANCE YOU PROVIDE:
- Product recommendations based on customer goals
- Ingredient information and transparency
- Dosing guidance based on product labels
- Supplement combinations (what works well together)
- What to avoid combining (drug-supplement interactions — basic)
- Timing of supplements (when to take for best results)

SAFETY BOUNDARIES:
- For medical conditions: always recommend consulting a doctor
  before starting supplements
- Never claim supplements treat or cure diseases
- Flag potential interactions with common medications
- For pregnancy/breastfeeding: always recommend doctor consultation
- Keep health claims within legal wellness boundaries

WHEN YOU CANNOT HELP:
"For this question, I'd recommend speaking directly with 
our team at +254 793 775 356 or nutricore@gmail.com — 
they'll be able to give you personalised guidance."

RESPONSE STYLE:
- Conversational and warm
- Under 120 words for simple questions
- Use emojis sparingly but naturally 🌿
- End with a helpful follow-up offer"""

# ── STYLING ───────────────────────────────────────────────────
st.markdown("""
<style>
    .health-header {
        background: linear-gradient(135deg, #2E7D32, #388E3C);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 1.5rem;
        color: white;
    }
    .product-chip {
        display: inline-block;
        background: #E8F5E9;
        color: #2E7D32;
        padding: 3px 10px;
        border-radius: 99px;
        font-size: 0.8rem;
        margin: 2px;
    }
</style>
""", unsafe_allow_html=True)

# ── HEADER ────────────────────────────────────────────────────
st.markdown("""
<div class="health-header">
    <h1 style="margin:0; font-size:1.6rem;">🌿 NutriCore Health</h1>
    <p style="margin:0.4rem 0 0; opacity:0.9; font-size:0.9rem;">
        Premium Supplements · Nairobi, Kenya · Est. 2019
    </p>
</div>
""", unsafe_allow_html=True)

# ── PRODUCT CATEGORIES ────────────────────────────────────────
st.markdown("""
<div style='text-align:center; margin-bottom:1rem;'>
<span class="product-chip">💪 Protein</span>
<span class="product-chip">🧬 Vitamins</span>
<span class="product-chip">✨ Collagen</span>
<span class="product-chip">🔥 Weight Management</span>
<span class="product-chip">⚡ Energy</span>
<span class="product-chip">🫀 Wellness</span>
</div>
""", unsafe_allow_html=True)

# ── QUICK QUESTIONS ───────────────────────────────────────────
st.markdown("**What can I help you with?**")
col1, col2 = st.columns(2)

if "health_quick_q" not in st.session_state:
    st.session_state.health_quick_q = None

with col1:
    if st.button("🥛 Best protein for weight loss", use_container_width=True):
        st.session_state.health_quick_q = "What is the best protein supplement for weight loss?"
    if st.button("🚚 Delivery to my area", use_container_width=True):
        st.session_state.health_quick_q = "How does delivery work and what are the costs?"

with col2:
    if st.button("💊 Safe for diabetics?", use_container_width=True):
        st.session_state.health_quick_q = "Which of your supplements are safe for someone with diabetes?"
    if st.button("📦 How to order with M-Pesa", use_container_width=True):
        st.session_state.health_quick_q = "How do I pay with M-Pesa and place an order?"

st.markdown("---")

# ── MEMORY & HISTORY ─────────────────────────────────────────
if "health_messages" not in st.session_state:
    st.session_state.health_messages = []

# ── WELCOME ───────────────────────────────────────────────────
if not st.session_state.health_messages:
    with st.chat_message("assistant", avatar="🌿"):
        st.markdown("""
Habari! 👋 I'm **Zuri**, your NutriCore Health assistant.

Whether you're looking for the right protein powder, wondering about delivery to your area, or need help choosing supplements for your health goals — I'm here to help!

What would you like to know today? 🌿
        """)

# ── DISPLAY HISTORY ───────────────────────────────────────────
for msg in st.session_state.health_messages:
    avatar = "🌿" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# ── HANDLE INPUT ──────────────────────────────────────────────
default_q = st.session_state.health_quick_q or ""
if st.session_state.health_quick_q:
    st.session_state.health_quick_q = None

user_input = st.chat_input("Ask about products, delivery, health advice...") or default_q

if user_input:
    st.session_state.health_messages.append({
        "role": "user", "content": user_input
    })
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

# ── URGENT CHECK ─────────────────────────────────────────
    # Runs before AI responds — instant detection
    is_urgent, matched_keyword = check_urgent(user_input)

    if is_urgent:
        # Log the alert immediately
        alert = log_urgent_alert(user_input, matched_keyword)

        # Show urgent warning in the main chat area
        st.warning(
            "⚠️ **Urgent health concern detected.**\n\n"
            "Our team has been notified and will contact "
            "you as soon as possible.\n\n"
            "**For immediate emergencies please call:**\n"
            "🚨 Kenya Emergency: **0800 720 999** (free)\n"
            "🏥 Nairobi Hospital: **+254 20 284 5000**\n"
            "💊 Poison Control: **+254 20 272 2000**"
        )
with st.chat_message("assistant", avatar="🌿"):
        with st.spinner("Zuri is typing..."):
            optimised_history = get_optimised_messages(
                st.session_state.health_messages
            )
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT}
                ] + optimised_history,
                max_tokens=400,
                temperature=0.7
            )
            reply = response.choices[0].message.content
        st.markdown(reply)
        detected_category = log_conversation(user_input, reply)
        

st.session_state.health_messages.append({
        "role": "assistant", "content": reply
    })
    
    # ── LEAD CAPTURE FLOW ─────────────────────────────────────
    # Stage 1: Detect purchase intent and prompt for details
if (detect_purchase_intent(user_input) and
            st.session_state.lead_capture_stage is None and
            not st.session_state.get("lead_captured")):

        # Save what they are interested in
        st.session_state.lead_interest = user_input
        st.session_state.lead_capture_stage = "prompted"

        # Show a natural lead capture prompt
        with st.chat_message("assistant", avatar="🌿"):
            capture_message = (
                "I'd love to help you with this! 🌿\n\n"
                "To check stock availability and arrange "
                "delivery to your area, could I get:\n\n"
                "1. Your **name**\n"
                "2. Your **WhatsApp number** or email\n"
                "3. Your **location** in Kenya\n\n"
                "Or you can reach us directly on "
                "WhatsApp: **+254 700 000 000** 😊"
            )
            st.markdown(capture_message)

        st.session_state.health_messages.append({
            "role": "assistant",
            "content": capture_message
        })

    # Stage 2: Receive their name    elif st.session_state.lead_capture_stage == "prompted":

        # Check if this message has contact info
        contact_found = detect_contact_info(user_input)

        if contact_found or len(user_input) > 5:
            # Treat the whole message as their details
            # Extract name (first word or two if no contact found)
            words = user_input.split()
            name_guess = " ".join(words[:2]) if len(words) >= 2 else user_input

            # Save the lead
            lead = save_lead(
                name=name_guess,
                contact=contact_found or user_input,
                interest=st.session_state.lead_interest or "General inquiry",
                conversation_context=user_input
            )

            st.session_state.lead_capture_stage = "captured"
            st.session_state.lead_captured = True

            # Show confirmation
            with st.chat_message("assistant", avatar="🌿"):
                confirm_message = (
                    f"Asante sana! 🙏 We have your details.\n\n"
                    "Our team will contact you on WhatsApp "
                    "within **30 minutes** to confirm your "
                    "order and arrange delivery.\n\n"
                    "We are open Monday to Saturday, "
                    "8am–6pm EAT. Have a healthy day! 🌿"
                )
                st.markdown(confirm_message)

            st.session_state.health_messages.append({
                "role": "assistant",
                "content": confirm_message
            })

            # Show success indicator
            st.success(
                f"✅ Lead captured! "
                f"Total leads today: "
                f"{len(st.session_state.captured_leads)}"
            )

# ── SIDEBAR ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📞 Contact NutriCore")
    st.markdown("""
    **WhatsApp:** +254 793 775 356

    **Email:** nutricore@gmail.com

    **Hours:** Mon–Sat, 8am–6pm EAT

    ---
    🚚 **Delivery**
    - Nairobi same-day: KES 200
    - Countrywide: KES 350

    💳 **Payment**
    M-Pesa · Card · Cash on Delivery
    """)

    st.markdown("---")
    st.markdown("*AI Assistant powered by NutriCore*")

    if st.button("🗑️ Clear chat"):
        st.session_state.health_messages = []
        st.rerun()
        
        # ── CONVERSATION DASHBOARD ────────────────────────────────
    st.markdown("---")
    st.markdown("### 📊 Live Dashboard")

    log = st.session_state.full_conversation_log

    if not log:
        st.markdown(
            "*No conversations yet. "
            "Dashboard updates after first message.*"
        )
    else:
        # Show key metrics
        total = len(log)
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Conversations", total)
        with col_b:
            # Count unique categories
            categories = list(set(e["category"] for e in log))
            st.metric("Categories", len(categories))

        # Category breakdown
        st.markdown("**By category:**")
        from collections import Counter
        cat_counts = Counter(e["category"] for e in log)
        for cat, count in cat_counts.most_common():
            # Show a simple bar using emoji blocks
            bar = "█" * count
            st.markdown(
                f"`{cat}` {bar} {count}"
            )

        # Recent conversations
        st.markdown("**Recent queries:**")
        for entry in reversed(log[-5:]):
            preview = entry["customer_message"][:45]
            st.markdown(
                f"• `{entry.get('time', 'unknown')}` [{entry.get('category', 'general')}]"
                f"\n  {preview}..."
            )

        # Download the full log as JSON
        st.markdown("---")
        log_export = json.dumps(log, indent=2, ensure_ascii=False)
        # ── LEADS CAPTURED PANEL ──────────────────────────────────
    leads = st.session_state.get("captured_leads", [])

    if leads:
        st.markdown("---")
        st.markdown("### 💰 Leads Captured")

        st.success(
            f"**{len(leads)} lead(s)** captured this session"
        )

        # Show each lead
        for lead in reversed(leads):
            with st.expander(
                f"🌿 {lead.get('time','--')} — "
                f"{lead.get('name','Unknown')}"
            ):
                st.markdown(
                    f"**Contact:** {lead.get('contact','Not provided')}"
                )
                st.markdown(
                    f"**Interest:** {lead.get('interest','')[:80]}..."
                )
                st.markdown(
                    f"**Status:** {lead.get('status','New Lead')}"
                )
                st.markdown(
                    f"**Session:** {lead.get('session_id','')}"
                )

        # Download leads as CSV for the sales team
        import csv
        import io

        output = io.StringIO()
        if leads:
            writer = csv.DictWriter(
                output,
                fieldnames=leads[0].keys()
            )
            writer.writeheader()
            writer.writerows(leads)

        st.download_button(
            label="⬇️ Download leads CSV",
            data=output.getvalue(),
            file_name=(
                f"nutricore_leads_"
                f"{datetime.now().strftime('%Y%m%d')}.csv"
            ),
            mime="text/csv",
            use_container_width=True
        )
        # ── URGENT ALERTS PANEL ───────────────────────────────────
    urgent_list = st.session_state.get("urgent_alerts", [])

    if urgent_list:
        st.markdown("---")
        st.markdown("### 🚨 Urgent Alerts")

        # Red metric showing count
        st.error(
            f"**{len(urgent_list)} urgent alert(s)** "
            f"require follow-up"
        )

        # Show each urgent alert
        for alert in reversed(urgent_list):
            with st.expander(
                f"🚨 {alert.get('time','--')} — "
                f"Keyword: {alert.get('keyword_matched','unknown')}"
            ):
                st.markdown(
                    f"**Date:** {alert.get('date','unknown')}"
                )
                st.markdown(
                    f"**Session:** {alert.get('session_id','unknown')}"
                )
                st.markdown(
                    f"**Message:** {alert.get('customer_message','')}"
                )
                st.markdown(
                    f"**Status:** {alert.get('status','Unreviewed')}"
                )

        # Download urgent alerts separately
        urgent_export = json.dumps(urgent_list, indent=2)
        st.download_button(
            label="⬇️ Download urgent alerts",
            data=urgent_export,
            file_name=(
                f"urgent_alerts_"
                f"{datetime.now().strftime('%Y%m%d')}.json"
            ),
            mime="application/json",
            use_container_width=True
        )
        st.download_button(
            label="⬇️ Download full log",
            data=log_export,
            file_name=(
                f"nutricore_log_"
                            ),
            mime="application/json",
            use_container_width=True
        )
        # ── TOKEN COST ESTIMATOR ──────────────────────────────────────
st.markdown("---")
st.markdown("### 💰 Cost Tracker")

message_count = len(st.session_state.health_messages)
# Rough estimate: 150 tokens per message exchange
estimated_tokens = message_count * 150
# gpt-4o-mini cost: $0.00015 per 1K input tokens
estimated_cost_usd = (estimated_tokens / 1000) * 0.00015
estimated_cost_kes = estimated_cost_usd * 130

col_cost1, col_cost2 = st.columns(2)
with col_cost1:
    st.metric(
        "Est. tokens",
        f"{estimated_tokens:,}"
    )
with col_cost2:
    st.metric(
        "Est. cost",
        f"KES {estimated_cost_kes:.4f}"
    )

st.markdown(
    f"*At this rate, 1,000 conversations "
    f"costs approximately "
    f"KES {estimated_cost_kes * 1000:.2f}*"
)

st.markdown("""
---
<div style='text-align:center; color:#999; font-size:0.78rem;'>
🌿 NutriCore Health · Nairobi, Kenya · nutricore@gmail.com<br>
<em>Supplement advice does not replace medical consultation</em>
</div>
""", unsafe_allow_html=True)