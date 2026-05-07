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

try:
    api_key = st.secrets["OPENAI_API_KEY"]
except:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=r"C:\Users\pc\ai-engineering\.env")
    api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

st.set_page_config(
    page_title="NutriCore Health — Support",
    page_icon="🌿",
    layout="centered"
)

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

    with st.chat_message("assistant", avatar="🌿"):
        with st.spinner("Zuri is typing..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT}
                ] + st.session_state.health_messages,
                max_tokens=300,
                temperature=0.7
            )
            reply = response.choices[0].message.content
        st.markdown(reply)

    st.session_state.health_messages.append({
        "role": "assistant", "content": reply
    })

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

st.markdown("""
---
<div style='text-align:center; color:#999; font-size:0.78rem;'>
🌿 NutriCore Health · Nairobi, Kenya · nutricore@gmail.com<br>
<em>Supplement advice does not replace medical consultation</em>
</div>
""", unsafe_allow_html=True)