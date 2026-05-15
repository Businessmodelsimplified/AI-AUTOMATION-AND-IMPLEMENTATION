# saas_webhook.py
# Day 9 — AXIOM 60-Day AI Engineering Program
#
# WEBHOOK: SaaS Support Ticket Intelligence System
#
# REAL CLIENT SCENARIO:
# LabTrack SaaS receives 200+ support tickets weekly.
# Support team spends mornings manually triaging tickets.
# High-value customers at churn risk go undetected.
# Engineers find out about critical bugs too late.
#
# WHAT THIS BUILDS:
# Instant AI triage on every incoming ticket.
# Correct routing to the right team member automatically.
# Churn risk detection for high-value accounts.
# Draft reply ready before human even opens the ticket.
#
# COMMERCIAL VALUE: $2,000–$5,000 build + $200/month maintain

import os
import json
from datetime import datetime
from flask import Flask, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)
processed_tickets = set()

# Routing rules — who handles what
ROUTING_RULES = {
    "billing": {
        "assignee": "billing@labtrack.co.ke",
        "slack_channel": "#billing-support",
        "sla_hours": 4
    },
    "bug_report": {
        "assignee": "engineering@labtrack.co.ke",
        "slack_channel": "#bugs",
        "sla_hours": 2
    },
    "feature_request": {
        "assignee": "product@labtrack.co.ke",
        "slack_channel": "#product",
        "sla_hours": 48
    },
    "how_to": {
        "assignee": "support@labtrack.co.ke",
        "slack_channel": "#support",
        "sla_hours": 8
    },
    "data_issue": {
        "assignee": "engineering@labtrack.co.ke",
        "slack_channel": "#data-emergency",
        "sla_hours": 1
    },
    "account": {
        "assignee": "support@labtrack.co.ke",
        "slack_channel": "#support",
        "sla_hours": 4
    },
    "cancellation": {
        "assignee": "success@labtrack.co.ke",
        "slack_channel": "#churn-risk",
        "sla_hours": 1
    }
}


def analyse_support_ticket(
    ticket_subject, ticket_body, customer_plan,
    customer_since, monthly_value
):
    """
    Analyses a support ticket and returns:
    - Category and subcategory
    - Urgency level (1-5)
    - Churn risk assessment
    - Draft reply ready to send
    - Internal note for the support agent
    """

    system_prompt = """You are an expert SaaS customer success
    analyst specialising in laboratory management software.

    Analyse support tickets and return a structured JSON triage
    report. Be accurate — incorrect routing wastes team time.
    Be empathetic in draft replies — customers are often frustrated.

    Churn risk is HIGH if: customer mentions cancellation, competitor,
    or expresses strong dissatisfaction. MEDIUM if they are stuck on
    a critical workflow. LOW for standard how-to questions.

    Respond ONLY with valid JSON:
    {
        "category": "billing|bug_report|feature_request|how_to|data_issue|account|cancellation",
        "subcategory": "specific description",
        "urgency": 1-5,
        "urgency_reason": "why this urgency level",
        "churn_risk": "HIGH|MEDIUM|LOW",
        "churn_risk_reason": "why this risk level",
        "sentiment": "frustrated|neutral|positive|confused",
        "draft_reply": "ready-to-send reply text",
        "internal_note": "note for the support agent only",
        "suggested_action": "specific action beyond the reply",
        "estimated_resolution_time": "X minutes/hours"
    }"""

    user_message = f"""Triage this support ticket:

    Subject: {ticket_subject}

    Message:
    {ticket_body}

    Customer Details:
    - Plan: {customer_plan}
    - Customer since: {customer_since}
    - Monthly value: ${monthly_value}

    Generate the complete triage report."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=700,
            temperature=0.3
        )

        raw = response.choices[0].message.content
        triage = json.loads(raw)
        return triage, None

    except json.JSONDecodeError as e:
        return None, f"AI returned invalid JSON: {str(e)}"
    except Exception as e:
        return None, f"Triage failed: {str(e)}"


@app.route("/webhook/support-ticket", methods=["POST"])
def support_ticket_webhook():
    """
    Receives new support tickets from the LabTrack platform.

    Expected JSON payload:
    {
        "ticket_id": "TKT-2026-8842",
        "subject": "Cannot export monthly QC report",
        "body": "Hi, I have been trying to export...",
        "customer_email": "lab@hospital.ke",
        "customer_name": "Dr. Wanjiku",
        "customer_plan": "Professional",
        "customer_since": "2024-03-15",
        "monthly_value": 180,
        "submitted_at": "2026-05-14T06:30:00Z"
    }
    """

    try:
        payload = request.get_json()
        if not payload:
            return jsonify({
                "status": "error",
                "message": "No JSON payload"
            }), 400
    except Exception:
        return jsonify({
            "status": "error",
            "message": "Invalid JSON"
        }), 400

    # Extract all fields safely
    ticket_id = payload.get("ticket_id", "unknown")
    subject = payload.get("subject", "No subject")
    body = payload.get("body", "")
    customer_email = payload.get("customer_email", "")
    customer_name = payload.get("customer_name", "Customer")
    customer_plan = payload.get("customer_plan", "Starter")
    customer_since = payload.get("customer_since", "unknown")
    monthly_value = payload.get("monthly_value", 0)
    submitted_at = payload.get("submitted_at",
                               datetime.now().isoformat())

    print(f"\n{'='*50}")
    print(f"NEW TICKET — {datetime.now().strftime('%H:%M:%S')}")
    print(f"Ticket ID: {ticket_id}")
    print(f"Subject:   {subject}")
    print(f"Customer:  {customer_name} ({customer_plan})")
    print(f"Value:     ${monthly_value}/month")
    print(f"{'='*50}")

    # Duplicate prevention
    if ticket_id in processed_tickets:
        return jsonify({
            "status": "already_processed",
            "ticket_id": ticket_id
        }), 200

    # Validate required fields
    if not subject or not body:
        return jsonify({
            "status": "error",
            "ticket_id": ticket_id,
            "message": "subject and body are required"
        }), 400

    # Run AI triage
    print("Running AI ticket triage...")
    triage, error = analyse_support_ticket(
        ticket_subject=subject,
        ticket_body=body,
        customer_plan=customer_plan,
        customer_since=customer_since,
        monthly_value=monthly_value
    )

    if error:
        return jsonify({
            "status": "error",
            "ticket_id": ticket_id,
            "message": error
        }), 500

    # Get routing information
    category = triage.get("category", "how_to")
    routing = ROUTING_RULES.get(category, ROUTING_RULES["how_to"])

    processed_tickets.add(ticket_id)

    # Flag high churn risk prominently
    churn_risk = triage.get("churn_risk", "LOW")
    urgency = triage.get("urgency", 3)

    # Override routing for cancellation and high-value churn risk
    if (churn_risk == "HIGH" or
            category == "cancellation" or
            (monthly_value >= 150 and urgency >= 4)):
        routing = ROUTING_RULES["cancellation"]
        print(f"⚠️  HIGH CHURN RISK — routing to customer success")

    response_data = {
        "status": "success",
        "ticket_id": ticket_id,
        "processed_at": datetime.now().isoformat(),
        "customer": {
            "name": customer_name,
            "email": customer_email,
            "plan": customer_plan,
            "monthly_value": monthly_value,
            "customer_since": customer_since
        },
        "triage": {
            "category": triage.get("category"),
            "subcategory": triage.get("subcategory"),
            "urgency": urgency,
            "urgency_reason": triage.get("urgency_reason"),
            "churn_risk": churn_risk,
            "churn_risk_reason": triage.get("churn_risk_reason"),
            "sentiment": triage.get("sentiment"),
            "estimated_resolution_time": triage.get(
                "estimated_resolution_time"
            )
        },
        "routing": {
            "assigned_to": routing["assignee"],
            "slack_channel": routing["slack_channel"],
            "sla_deadline": f"Respond within {routing['sla_hours']} hours"
        },
        "ai_response": {
            "draft_reply": triage.get("draft_reply"),
            "internal_note": triage.get("internal_note"),
            "suggested_action": triage.get("suggested_action")
        }
    }

    print(f"Category:   {triage.get('category')}")
    print(f"Urgency:    {urgency}/5")
    print(f"Churn Risk: {churn_risk}")
    print(f"Routed to:  {routing['assignee']}")

    return jsonify(response_data), 200


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "LabTrack Support Intelligence Webhook",
        "tickets_processed": len(processed_tickets),
        "timestamp": datetime.now().isoformat()
    }), 200


if __name__ == "__main__":
    print("\n" + "="*50)
    print("LABTRACK SUPPORT INTELLIGENCE WEBHOOK")
    print("Day 9 — AXIOM AI Engineering Program")
    print("="*50)
    print("Endpoints:")
    print("  POST /webhook/support-ticket — process tickets")
    print("  GET  /health                 — health check")
    print("="*50 + "\n")
    app.run(host="0.0.0.0", port=5003, debug=True)