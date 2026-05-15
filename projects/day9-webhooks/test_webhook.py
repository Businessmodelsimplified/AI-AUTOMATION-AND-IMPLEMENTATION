# test_webhooks.py
# Automated test script for all three webhook servers
# Run this to verify all three are working correctly

import requests
import json
from datetime import datetime

def print_result(test_name, response):
    """Pretty prints test results."""
    status = "✓ PASS" if response.status_code == 200 else "✗ FAIL"
    print(f"\n{status} — {test_name}")
    print(f"   Status: {response.status_code}")

    try:
        data = response.json()
        if "analysis" in data:
            analysis = data["analysis"]
            print(f"   Risk Level: {analysis.get('risk_level')}")
            print(f"   Gaps Found: {len(analysis.get('compliance_gaps', []))}")
        elif "followup_sequence" in data:
            print(f"   Customer: {data['customer']['name']}")
            print(f"   Day 2 preview: {data['followup_sequence']['day_2']['message'][:60]}...")
        elif "triage" in data:
            triage = data["triage"]
            print(f"   Category: {triage.get('category')}")
            print(f"   Urgency: {triage.get('urgency')}/5")
            print(f"   Churn Risk: {triage.get('churn_risk')}")
    except Exception as e:
        print(f"   Response: {response.text[:100]}")


print("\n" + "="*55)
print("WEBHOOK INTEGRATION TESTS")
print(f"Running at: {datetime.now().strftime('%H:%M:%S')}")
print("="*55)

# ── TEST 1: Pharma webhook health check
try:
    r = requests.get("http://localhost:5001/health", timeout=5)
    print_result("Pharma webhook health check", r)
except requests.ConnectionError:
    print("✗ FAIL — Pharma webhook not running on port 5001")
    print("  Run: python pharma_webhook.py")

# ── TEST 2: Pharma regulatory document
try:
    r = requests.post(
        "http://localhost:5001/webhook/regulatory",
        json={
            "event_id": f"TEST-{datetime.now().strftime('%H%M%S')}",
            "document_type": "Safety Alert",
            "issuing_body": "KPPB",
            "company_id": "test-pharma-001",
            "document_content": (
                "KPPB Safety Alert: All pharmaceutical companies must "
                "immediately review their pharmacovigilance systems. "
                "New WHO guidelines require adverse drug reaction "
                "reports to be submitted within 7 days of detection "
                "for serious events, reduced from the previous 15-day "
                "requirement. Companies must update SOP-PV-001 and "
                "train all relevant staff by 30 June 2026."
            )
        },
        timeout=30
    )
    print_result("Pharma regulatory analysis", r)
except requests.ConnectionError:
    print("✗ FAIL — Pharma webhook not running")

# ── TEST 3: Health order webhook health check
try:
    r = requests.get("http://localhost:5002/health", timeout=5)
    print_result("Health webhook health check", r)
except requests.ConnectionError:
    print("✗ FAIL — Health webhook not running on port 5002")
    print("  Run: python health_webhook.py")

# ── TEST 4: Health new order
try:
    r = requests.post(
        "http://localhost:5002/webhook/new-order",
        json={
            "order_id": f"ORD-TEST-{datetime.now().strftime('%H%M%S')}",
            "customer_name": "Amina Hassan",
            "customer_phone": "0733456789",
            "product_name": "Marine Collagen Peptides 600g",
            "health_goal": "Skin health and anti-aging",
            "delivery_location": "Kilimani, Nairobi",
            "order_total": 5200
        },
        timeout=30
    )
    print_result("Health new order follow-up", r)
except requests.ConnectionError:
    print("✗ FAIL — Health webhook not running")

# ── TEST 5: SaaS webhook health check
try:
    r = requests.get("http://localhost:5003/health", timeout=5)
    print_result("SaaS webhook health check", r)
except requests.ConnectionError:
    print("✗ FAIL — SaaS webhook not running on port 5003")
    print("  Run: python saas_webhook.py")

# ── TEST 6: SaaS support ticket
try:
    r = requests.post(
        "http://localhost:5003/webhook/support-ticket",
        json={
            "ticket_id": f"TKT-TEST-{datetime.now().strftime('%H%M%S')}",
            "subject": "Error 5001 on sample result approval",
            "body": (
                "Hi, I am getting Error 5001 every time I try to "
                "approve a batch of HPLC results. This started "
                "yesterday and I have 3 batches waiting. "
                "The lab director needs these results today."
            ),
            "customer_email": "qc@medlab.ke",
            "customer_name": "John Kamau",
            "customer_plan": "Professional",
            "customer_since": "2025-01-10",
            "monthly_value": 180
        },
        timeout=30
    )
    print_result("SaaS ticket triage", r)
except requests.ConnectionError:
    print("✗ FAIL — SaaS webhook not running")

print("\n" + "="*55)
print("TEST RUN COMPLETE")
print("="*55 + "\n")