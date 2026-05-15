# health_webhook.py
# Day 9 — AXIOM 60-Day AI Engineering Program
#
# WEBHOOK: Health & Wellness Order Intelligence System
#
# REAL CLIENT SCENARIO:
# NutriCore Health receives 40+ orders per week.
# Owner manually writes follow-up messages for each customer.
# Takes 3 hours weekly. Inconsistent quality. Often forgotten.
#
# WHAT THIS BUILDS:
# Instant AI-generated personalised follow-up sequence
# triggered the moment a new order is placed.
# Day 2 check-in, Day 7 progress check, Day 30 review request.
#
# COMMERCIAL VALUE: $1,500–$3,500 build + $150/month maintain

import os
import json
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)
processed_orders = set()


def generate_followup_sequence(
    customer_name, product_name, health_goal,
    delivery_location, order_total
):
    """
    Generates a personalised 3-message follow-up sequence
    for a new supplement customer.

    Real business value: personal-feeling messages at scale.
    A customer who bought whey protein for muscle building
    gets different messages than one who bought collagen
    for skin health. Same system. Zero extra work.
    """

    system_prompt = """You are the friendly customer success
    manager for NutriCore Health, a premium supplement brand
    in Nairobi, Kenya.

    Generate a 3-message WhatsApp follow-up sequence for a
    new customer. Each message must feel personal, warm, and
    genuinely helpful — not like a marketing template.

    Use Swahili greetings naturally.
    Reference their specific product and health goal.
    Include practical usage tips relevant to their product.
    Day 30 message should ask for a review naturally.

    Respond ONLY with valid JSON:
    {
        "day_2_message": "message text here",
        "day_7_message": "message text here",
        "day_30_message": "message text here",
        "usage_tip": "one specific tip for their product",
        "warning": "one thing to avoid with their product"
    }"""

    user_message = f"""Generate a follow-up sequence for:

    Customer Name: {customer_name}
    Product Purchased: {product_name}
    Their Health Goal: {health_goal}
    Location: {delivery_location}
    Order Total: KES {order_total}

    Make each message feel like it came from a real person
    who knows this customer and cares about their results."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=600,
            temperature=0.7
        )

        raw = response.choices[0].message.content
        sequence = json.loads(raw)
        return sequence, None

    except json.JSONDecodeError as e:
        return None, f"AI returned invalid JSON: {str(e)}"
    except Exception as e:
        return None, f"Generation failed: {str(e)}"


@app.route("/webhook/new-order", methods=["POST"])
def new_order_webhook():
    """
    Receives new order notifications from the NutriCore
    e-commerce platform (Shopify, WooCommerce, or custom).

    Expected JSON payload:
    {
        "order_id": "ORD-2026-1847",
        "customer_name": "James Ochieng",
        "customer_phone": "0712345678",
        "product_name": "Whey Protein Chocolate 2kg",
        "health_goal": "Muscle building",
        "delivery_location": "Westlands, Nairobi",
        "order_total": 6200,
        "order_date": "2026-05-14"
    }
    """

    # Get and validate payload
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

    # Extract fields safely
    order_id = payload.get("order_id", "unknown")
    customer_name = payload.get("customer_name", "Customer")
    customer_phone = payload.get("customer_phone", "")
    product_name = payload.get("product_name", "supplement")
    health_goal = payload.get("health_goal", "general health")
    delivery_location = payload.get("delivery_location", "Kenya")
    order_total = payload.get("order_total", 0)
    order_date = payload.get("order_date",
                             datetime.now().strftime("%Y-%m-%d"))

    print(f"\n{'='*50}")
    print(f"NEW ORDER — {datetime.now().strftime('%H:%M:%S')}")
    print(f"Order ID:  {order_id}")
    print(f"Customer:  {customer_name}")
    print(f"Product:   {product_name}")
    print(f"Goal:      {health_goal}")
    print(f"{'='*50}")

    # Prevent duplicate processing
    if order_id in processed_orders:
        return jsonify({
            "status": "already_processed",
            "order_id": order_id
        }), 200

    # Validate required fields
    if not customer_name or not product_name:
        return jsonify({
            "status": "error",
            "order_id": order_id,
            "message": "customer_name and product_name are required"
        }), 400

    # Generate personalised follow-up sequence
    print("Generating personalised follow-up sequence...")
    sequence, error = generate_followup_sequence(
        customer_name=customer_name,
        product_name=product_name,
        health_goal=health_goal,
        delivery_location=delivery_location,
        order_total=order_total
    )

    if error:
        return jsonify({
            "status": "error",
            "order_id": order_id,
            "message": error
        }), 500

    # Calculate scheduled send dates
    order_datetime = datetime.now()
    day_2_date = (order_datetime + timedelta(days=2)).strftime("%Y-%m-%d")
    day_7_date = (order_datetime + timedelta(days=7)).strftime("%Y-%m-%d")
    day_30_date = (order_datetime + timedelta(days=30)).strftime("%Y-%m-%d")

    processed_orders.add(order_id)

    response_data = {
        "status": "success",
        "order_id": order_id,
        "customer": {
            "name": customer_name,
            "phone": customer_phone,
            "location": delivery_location
        },
        "product": product_name,
        "followup_sequence": {
            "day_2": {
                "send_date": day_2_date,
                "message": sequence.get("day_2_message", ""),
                "channel": "WhatsApp"
            },
            "day_7": {
                "send_date": day_7_date,
                "message": sequence.get("day_7_message", ""),
                "channel": "WhatsApp"
            },
            "day_30": {
                "send_date": day_30_date,
                "message": sequence.get("day_30_message", ""),
                "channel": "WhatsApp"
            }
        },
        "product_guidance": {
            "usage_tip": sequence.get("usage_tip", ""),
            "warning": sequence.get("warning", "")
        },
        "processed_at": datetime.now().isoformat()
    }

    print(f"Follow-up sequence generated for {customer_name}")
    print(f"Scheduled: Day 2 ({day_2_date}), "
          f"Day 7 ({day_7_date}), Day 30 ({day_30_date})")

    return jsonify(response_data), 200


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "NutriCore Order Intelligence Webhook",
        "orders_processed": len(processed_orders),
        "timestamp": datetime.now().isoformat()
    }), 200


if __name__ == "__main__":
    print("\n" + "="*50)
    print("NUTRICORE ORDER INTELLIGENCE WEBHOOK")
    print("Day 9 — AXIOM AI Engineering Program")
    print("="*50)
    print("Endpoints:")
    print("  POST /webhook/new-order — process new orders")
    print("  GET  /health            — health check")
    print("="*50 + "\n")
    app.run(host="0.0.0.0", port=5002, debug=True)