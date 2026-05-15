# pharma_webhook.py
# Day 9 — AXIOM 60-Day AI Engineering Program
#
# WEBHOOK: Pharmaceutical Regulatory Document Processor
#
# REAL CLIENT SCENARIO:
# A pharmaceutical company receives regulatory notifications
# from KPPB (Kenya Pharmacy and Poisons Board).
# Each notification must be compared against existing SOPs
# to identify compliance gaps.
#
# HOW IT WORKS:
# 1. External system sends POST request to /webhook/regulatory
# 2. This endpoint receives the JSON payload
# 3. AI analyses the regulatory content
# 4. Returns structured gap analysis in under 2 minutes
#
# COMMERCIAL VALUE: $3,000–$8,000 build + $200/month maintain

import os
import json
import hashlib
import hmac
from datetime import datetime
from flask import Flask, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv

# ── CONFIGURATION ─────────────────────────────────────────────
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

# In production this is a secret shared with the sending service
# Used to verify the webhook came from a trusted source
WEBHOOK_SECRET = "pharma-webhook-secret-2026"

# Track processed events to prevent duplicate processing
processed_events = set()


# ── HELPER: Verify webhook authenticity ───────────────────────
def verify_signature(payload, signature_header):
    """
    Verifies that the webhook came from a trusted source.
    In production this is mandatory — skip it and anyone
    can send fake regulatory alerts to your system.

    How it works:
    - Sender hashes the payload with a shared secret
    - They include the hash in a header
    - You hash the payload with the same secret
    - If the hashes match — the payload is authentic
    """
    if not signature_header:
        return False

    expected = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected, signature_header)


# ── HELPER: Analyse regulatory document with AI ───────────────
def analyse_regulatory_document(document_content, document_type, issuing_body):
    """
    Takes regulatory document content and produces a structured
    compliance gap analysis using AI.

    Parameters:
        document_content — the text of the regulatory document
        document_type    — type e.g. "GMP Update", "Safety Alert"
        issuing_body     — e.g. "KPPB", "WHO", "EAC"

    Returns:
        Structured JSON with gaps, actions, and risk levels
    """

    system_prompt = """You are a senior pharmaceutical regulatory
    affairs specialist with 15 years of experience in East Africa,
    specialising in KPPB compliance and WHO-GMP standards.

    When given a regulatory document, you produce a structured
    compliance gap analysis in JSON format. You identify:
    1. What has changed from previous requirements
    2. Which SOPs are likely affected
    3. The risk level if the gap is not addressed
    4. Specific action items with realistic timelines

    Always respond with valid JSON only. No preamble. No markdown.
    Use this exact structure:
    {
        "document_summary": "2-3 sentence summary",
        "regulatory_body": "issuing organization",
        "effective_date": "date if mentioned or unknown",
        "risk_level": "HIGH/MEDIUM/LOW",
        "affected_areas": ["list", "of", "affected", "areas"],
        "compliance_gaps": [
            {
                "gap": "description of the gap",
                "affected_sop": "likely SOP reference",
                "risk": "HIGH/MEDIUM/LOW",
                "action_required": "specific action",
                "timeline": "recommended timeline"
            }
        ],
        "immediate_actions": ["action 1", "action 2"],
        "estimated_effort_hours": 0
    }"""

    user_message = f"""Analyse this regulatory document and
    identify compliance gaps:

    Document Type: {document_type}
    Issuing Body: {issuing_body}

    Content:
    {document_content}

    Produce the compliance gap analysis JSON."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=1000,
            temperature=0.2  # Low temp for consistent compliance analysis
        )

        raw_response = response.choices[0].message.content
        analysis = json.loads(raw_response)
        return analysis, None

    except json.JSONDecodeError as e:
        return None, f"AI returned invalid JSON: {str(e)}"
    except Exception as e:
        return None, f"AI analysis failed: {str(e)}"


# ── MAIN WEBHOOK ENDPOINT ─────────────────────────────────────
@app.route("/webhook/regulatory", methods=["POST"])
def regulatory_webhook():
    """
    Main webhook endpoint for regulatory document notifications.

    Accepts POST requests with JSON payload containing:
    - event_id: unique identifier for this event
    - document_type: type of regulatory document
    - issuing_body: who issued it (KPPB, WHO, EAC)
    - document_content: the actual regulatory text
    - company_id: identifier for the pharmaceutical company

    Returns JSON with the complete gap analysis.

    IMPORTANT: Returns 200 immediately if event already processed
    This prevents duplicate processing when the sender retries.
    """

    # ── STEP 1: Return 200 quickly to prevent timeout ─────────
    # We validate the request immediately but do NOT wait
    # for AI processing before acknowledging receipt.
    # In production: queue the job, return 200, process async.
    # For learning: we process synchronously for simplicity.

    # ── STEP 2: Get the raw payload ───────────────────────────
    raw_payload = request.get_data()
    signature = request.headers.get("X-Webhook-Signature", "")

    # ── STEP 3: Parse the JSON body ───────────────────────────
    try:
        payload = request.get_json()
        if not payload:
            return jsonify({
                "status": "error",
                "message": "No JSON payload received"
            }), 400
    except Exception:
        return jsonify({
            "status": "error",
            "message": "Invalid JSON format"
        }), 400

    # ── STEP 4: Extract required fields with safe defaults ────
    # NEVER use payload["key"] on external data — use .get()
    # External data can be missing, malformed, or unexpected
    event_id = payload.get("event_id", "unknown")
    document_type = payload.get("document_type", "Regulatory Update")
    issuing_body = payload.get("issuing_body", "KPPB")
    document_content = payload.get("document_content", "")
    company_id = payload.get("company_id", "unknown")

    print(f"\n{'='*50}")
    print(f"WEBHOOK RECEIVED — {datetime.now().strftime('%H:%M:%S')}")
    print(f"Event ID:      {event_id}")
    print(f"Document Type: {document_type}")
    print(f"Issuing Body:  {issuing_body}")
    print(f"Company ID:    {company_id}")
    print(f"{'='*50}")

    # ── STEP 5: Prevent duplicate processing ──────────────────
    if event_id in processed_events:
        print(f"Duplicate event {event_id} — skipping")
        return jsonify({
            "status": "already_processed",
            "event_id": event_id,
            "message": "This event was already processed"
        }), 200

    # ── STEP 6: Validate document content ────────────────────
    if not document_content:
        return jsonify({
            "status": "error",
            "event_id": event_id,
            "message": "document_content is required"
        }), 400

    if len(document_content) < 50:
        return jsonify({
            "status": "error",
            "event_id": event_id,
            "message": "document_content too short to analyse"
        }), 400

    # ── STEP 7: Run AI analysis ───────────────────────────────
    print("Running AI compliance gap analysis...")
    analysis, error = analyse_regulatory_document(
        document_content=document_content,
        document_type=document_type,
        issuing_body=issuing_body
    )

    if error:
        print(f"Analysis failed: {error}")
        return jsonify({
            "status": "error",
            "event_id": event_id,
            "message": error
        }), 500

    # ── STEP 8: Mark as processed ─────────────────────────────
    processed_events.add(event_id)

    # ── STEP 9: Build and return the complete response ────────
    response_data = {
        "status": "success",
        "event_id": event_id,
        "company_id": company_id,
        "processed_at": datetime.now().isoformat(),
        "document_type": document_type,
        "issuing_body": issuing_body,
        "analysis": analysis,
        "next_steps": {
            "review_deadline": "Within 48 hours of receipt",
            "assign_to": "Regulatory Affairs Manager",
            "log_reference": f"REG-{datetime.now().strftime('%Y%m%d')}-{event_id[:6]}"
        }
    }

    print(f"Analysis complete. Risk level: {analysis.get('risk_level','UNKNOWN')}")
    print(f"Gaps identified: {len(analysis.get('compliance_gaps', []))}")

    return jsonify(response_data), 200


# ── HEALTH CHECK ENDPOINT ─────────────────────────────────────
@app.route("/health", methods=["GET"])
def health_check():
    """
    Simple endpoint to verify the webhook server is running.
    External monitoring services ping this every minute.
    If it returns anything other than 200 — alert is triggered.
    """
    return jsonify({
        "status": "healthy",
        "service": "PharmaCompliance Webhook",
        "timestamp": datetime.now().isoformat(),
        "events_processed": len(processed_events)
    }), 200


# ── STATUS ENDPOINT ───────────────────────────────────────────
@app.route("/status", methods=["GET"])
def status():
    """Shows processing statistics for the monitoring dashboard."""
    return jsonify({
        "service": "Pharma Regulatory Webhook",
        "status": "running",
        "events_processed_this_session": len(processed_events),
        "processed_event_ids": list(processed_events)
    }), 200


if __name__ == "__main__":
    print("\n" + "="*50)
    print("PHARMA REGULATORY WEBHOOK SERVER")
    print("Day 9 — AXIOM AI Engineering Program")
    print("="*50)
    print("Endpoints:")
    print("  POST /webhook/regulatory  — receive regulatory docs")
    print("  GET  /health              — health check")
    print("  GET  /status              — processing stats")
    print("="*50 + "\n")

    # debug=True shows detailed errors during development
    # NEVER use debug=True in production
    app.run(
        host="0.0.0.0",
        port=5001,
        debug=True
    )