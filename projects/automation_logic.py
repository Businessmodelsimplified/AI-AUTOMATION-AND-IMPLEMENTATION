# automation_logic.py
# Day 4 — AXIOM 60-Day AI Engineering Program
# Automation Logic Simulator
# Real pattern: intelligent email/message routing for a health clinic
#
# THIS IS THE THINKING BEHIND EVERY AUTOMATION YOU WILL BUILD
# Pattern: Trigger → Condition → Action → Output
#
# Client value: A clinic receiving 100 emails/day saves 3 hours
# of manual sorting. At $15/hr that is $45/day = $1,350/month.
# Building this system: $1,500–$3,000 one-time fee.

import os
import json
import time
from dotenv import load_dotenv
from openai import OpenAI

# -------------------------------------------------------
# CONFIGURATION — all settings at the top
# -------------------------------------------------------
load_dotenv(dotenv_path=r"C:\Users\pc\ai-engineering\.env")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-4o-mini"


# -------------------------------------------------------
# STEP 1 — THE TRIGGER SIMULATION
# In a real system this function would connect to Gmail,
# WhatsApp, or a form submission webhook.
# Today we simulate it with sample messages.
# Same logic — different data source.
# -------------------------------------------------------

def get_incoming_messages():
    """
    Simulates incoming messages to a health clinic.
    In production this pulls from Gmail API, WhatsApp,
    or a webhook. The routing logic below stays identical.
    """
    return [
        {
            "id": "MSG001",
            "from": "patient_jane@gmail.com",
            "text": "Hi, I need to book an appointment with "
                    "Dr. Kamau for next Tuesday afternoon. "
                    "Is he available?"
        },
        {
            "id": "MSG002",
            "from": "supplier_pharma@medkenya.com",
            "text": "Please find attached our updated price "
                    "list for Q2 2026. Kindly confirm receipt "
                    "and update your procurement records."
        },
        {
            "id": "MSG003",
            "from": "patient_john@gmail.com",
            "text": "I have been having chest pains since "
                    "this morning and difficulty breathing. "
                    "What should I do?"
        },
        {
            "id": "MSG004",
            "from": "insurance_aaa@britam.com",
            "text": "Claim number 45821 for patient Mary Wanjiku "
                    "has been approved. Please submit the final "
                    "invoice for processing."
        },
        {
            "id": "MSG005",
            "from": "patient_peter@gmail.com",
            "text": "What are your opening hours on Saturday? "
                    "Also do you accept NHIF insurance?"
        }
    ]


# -------------------------------------------------------
# STEP 2 — THE CONDITION (AI-POWERED CLASSIFIER)
# This is the brain of the automation.
# It reads each message and decides which category
# it belongs to so the right action can be taken.
#
# Notice: the AI returns structured JSON — not freeform
# text. This is CRITICAL for automation. You need data
# you can act on programmatically, not a paragraph.
# -------------------------------------------------------

def classify_message(message_text):
    """
    Uses AI to classify an incoming message into a category.
    Returns structured JSON the automation can act on.

    Categories:
    - appointment_request: patient wants to book/change/cancel
    - medical_emergency: urgent symptoms requiring immediate help
    - general_inquiry: opening hours, services, insurance questions
    - supplier_communication: vendor or supplier messages
    - insurance_claim: insurance related communications
    - other: anything that does not fit above categories
    """

    system_prompt = """You are an intelligent message classifier 
    for HealthFirst Clinic in Nairobi. 
    
    Classify each incoming message into exactly one category:
    - appointment_request
    - medical_emergency  
    - general_inquiry
    - supplier_communication
    - insurance_claim
    - other
    
    Also extract:
    - urgency: high / medium / low
    - sender_type: patient / supplier / insurance / unknown
    - summary: one sentence describing the message
    
    Respond ONLY with valid JSON. No extra text. No markdown.
    Format exactly like this:
    {
        "category": "category_name",
        "urgency": "high/medium/low",
        "sender_type": "patient/supplier/insurance/unknown",
        "summary": "one sentence summary"
    }"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": message_text}
        ],
        max_tokens=150,
        temperature=0      # Temperature 0 for classification
                           # We want consistent, reliable answers
                           # not creative variations
    )

    # Parse the JSON response
    # In production always wrap JSON parsing in try/except
    try:
        result = json.loads(response.choices[0].message.content)
        return result
    except json.JSONDecodeError:
        # If AI returns invalid JSON fall back to safe default
        return {
            "category": "other",
            "urgency": "low",
            "sender_type": "unknown",
            "summary": "Could not classify this message"
        }


# -------------------------------------------------------
# STEP 3 — THE ACTIONS
# Each category gets a different action.
# In production these actions would:
# - Send real emails or WhatsApp messages
# - Create records in a CRM
# - Post alerts to Slack
# - Add rows to Google Sheets
# Today they print to terminal — same logic applies.
# -------------------------------------------------------

def action_appointment_request(message, classification):
    """
    Action for appointment requests.
    Production version: check calendar availability via
    Cal.com API, send booking link via WhatsApp/email,
    create pending appointment in clinic management system.
    """
    print(f"   📅 ACTION: Appointment Request")
    print(f"   → Checking Dr. Kamau's calendar availability")
    print(f"   → Sending booking link to {message['from']}")
    print(f"   → Creating pending appointment record in CRM")

    # Generate a personalised response using AI
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content":
                "You are a friendly clinic receptionist at "
                "HealthFirst Clinic Nairobi. Write a brief, "
                "warm reply acknowledging the appointment "
                "request and providing next steps. "
                "Keep it under 3 sentences."},
            {"role": "user", "content":
                f"Write a reply to this message: {message['text']}"}
        ],
        max_tokens=100,
        temperature=0.7
    )
    draft_reply = response.choices[0].message.content
    print(f"   → Draft reply generated:")
    print(f"      '{draft_reply}'")
    return "appointment_queued"


def action_medical_emergency(message, classification):
    """
    Action for medical emergencies.
    Production version: immediately SMS the on-call doctor,
    send emergency instructions to patient via WhatsApp,
    create urgent alert in clinic management system.
    """
    print(f"   🚨 ACTION: MEDICAL EMERGENCY DETECTED")
    print(f"   → ALERTING on-call doctor immediately")
    print(f"   → Sending emergency response to {message['from']}")
    print(f"   → Creating URGENT ticket in clinic system")
    print(f"   → Notifying clinic manager via SMS")
    return "emergency_escalated"


def action_general_inquiry(message, classification):
    """
    Action for general inquiries.
    Production version: search FAQ knowledge base with RAG,
    generate personalised answer, send via email/WhatsApp.
    (This becomes the RAG system you build on Day 19-21)
    """
    print(f"   ℹ️  ACTION: General Inquiry")
    print(f"   → Searching FAQ knowledge base")
    print(f"   → Generating personalised answer")
    print(f"   → Sending automated reply to {message['from']}")

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content":
                "You are a helpful assistant for HealthFirst "
                "Clinic Nairobi. Opening hours: Mon-Fri 8am-6pm, "
                "Sat 9am-2pm. We accept NHIF, AAR, Jubilee, "
                "and Britam insurance. Reply briefly and helpfully."},
            {"role": "user", "content": message['text']}
        ],
        max_tokens=150,
        temperature=0.7
    )
    draft_reply = response.choices[0].message.content
    print(f"   → Auto-reply sent:")
    print(f"      '{draft_reply}'")
    return "inquiry_answered"


def action_supplier_communication(message, classification):
    """
    Action for supplier messages.
    Production version: forward to procurement manager,
    log in supplier communication database, auto-acknowledge.
    """
    print(f"   📦 ACTION: Supplier Communication")
    print(f"   → Forwarding to procurement manager")
    print(f"   → Logging in supplier database")
    print(f"   → Sending acknowledgement to {message['from']}")
    return "supplier_routed"


def action_insurance_claim(message, classification):
    """
    Action for insurance communications.
    Production version: route to billing department,
    log claim reference number, update patient record.
    """
    print(f"   🏥 ACTION: Insurance Claim")
    print(f"   → Routing to billing department")
    print(f"   → Logging claim reference")
    print(f"   → Updating patient billing record")
    return "insurance_routed"


def action_other(message, classification):
    """
    Action for unclassified messages.
    Production version: queue for human review,
    send acknowledgement to sender.
    """
    print(f"   📋 ACTION: Queued for Human Review")
    print(f"   → Adding to manual review queue")
    print(f"   → Sending acknowledgement to {message['from']}")
    return "queued_for_review"


# -------------------------------------------------------
# STEP 4 — THE ROUTER
# This connects Classification → Action.
# It is the decision layer of the automation.
# Clean, simple, easy to extend with new categories.
# -------------------------------------------------------

def route_message(message, classification):
    """
    Routes a classified message to the correct action.
    This is the Condition → Action connection.
    """
    category = classification.get("category", "other")

    routes = {
        "appointment_request":    action_appointment_request,
        "medical_emergency":      action_medical_emergency,
        "general_inquiry":        action_general_inquiry,
        "supplier_communication": action_supplier_communication,
        "insurance_claim":        action_insurance_claim,
        "other":                  action_other
    }

    # Get the correct action function
    # If category not found default to other
    action_function = routes.get(category, action_other)
    return action_function(message, classification)


# -------------------------------------------------------
# STEP 5 — THE OUTPUT LOG
# Every automation needs an audit trail.
# In production this writes to Google Sheets,
# a database, or a Notion dashboard.
# -------------------------------------------------------

def log_result(message, classification, result):
    """
    Logs the complete automation result.
    Production version: writes to Google Sheets or database.
    """
    print(f"\n   📊 LOG ENTRY:")
    print(f"   Message ID:   {message['id']}")
    print(f"   From:         {message['from']}")
    print(f"   Category:     {classification['category']}")
    print(f"   Urgency:      {classification['urgency']}")
    print(f"   Sender type:  {classification['sender_type']}")
    print(f"   Summary:      {classification['summary']}")
    print(f"   Result:       {result}")


# -------------------------------------------------------
# STEP 6 — MAIN EXECUTION
# The complete automation pipeline.
# Trigger → Classify → Route → Act → Log
# This runs for every incoming message.
# -------------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print("AXIOM — Automation Logic Simulator")
    print("Day 4 — Trigger → Condition → Action → Output")
    print("Client: HealthFirst Clinic, Nairobi")
    print("=" * 60)

    # TRIGGER — get all incoming messages
    messages = get_incoming_messages()
    print(f"\n{len(messages)} messages received. Processing...\n")

    results_log = []

    for i, message in enumerate(messages, 1):
        print(f"\n{'─' * 60}")
        print(f"MESSAGE {i} of {len(messages)}")
        print(f"From:    {message['from']}")
        print(f"Content: {message['text'][:80]}...")
        print(f"{'─' * 60}")

        # CONDITION — classify the message with AI
        print(f"\n   🤖 Classifying with AI...")
        classification = classify_message(message['text'])
        print(f"   Category: {classification['category'].upper()}")
        print(f"   Urgency:  {classification['urgency'].upper()}")
        print()

        # ACTION — route to correct handler
        result = route_message(message, classification)

        # OUTPUT — log the complete result
        log_result(message, classification, result)

        results_log.append({
            "message_id":   message['id'],
            "category":     classification['category'],
            "urgency":      classification['urgency'],
            "result":       result
        })

        # Small pause between API calls
        # Prevents hitting rate limits
        time.sleep(1)

    # FINAL SUMMARY
    print(f"\n{'=' * 60}")
    print(f"AUTOMATION COMPLETE — SUMMARY")
    print(f"{'=' * 60}")
    print(f"Total messages processed: {len(messages)}")

    categories = {}
    for r in results_log:
        cat = r['category']
        categories[cat] = categories.get(cat, 0) + 1

    print(f"\nBreakdown by category:")
    for category, count in categories.items():
        print(f"  {category:<30} {count} message(s)")

    emergencies = [r for r in results_log if r['urgency'] == 'high']
    print(f"\nHigh urgency items: {len(emergencies)}")
    print(f"\nAll messages logged. Zero manual sorting required.")
    print(f"{'=' * 60}")