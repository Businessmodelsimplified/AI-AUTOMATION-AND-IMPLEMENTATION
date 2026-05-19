# prompt_tester.py
# Day 10 — AXIOM 60-Day AI Engineering Program
#
# PROMPT TESTING TOOL
# Tests different prompt versions against the same question
# Shows output quality differences side by side
#
# USE CASE: Before updating a client's chatbot system prompt,
# run the new prompt through 5 test questions and compare
# outputs against the current prompt. Only deploy if the
# new prompt scores better on all test cases.

import os
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def test_prompt(
    system_prompt,
    user_message,
    model="gpt-4o-mini",
    temperature=0.3,
    max_tokens=400,
    label="Prompt Version"
):
    """
    Tests a single prompt against a single question.
    Returns the response with timing and token data.
    """
    start_time = time.time()

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        max_tokens=max_tokens,
        temperature=temperature
    )

    elapsed = round(time.time() - start_time, 2)
    tokens_used = response.usage.total_tokens
    cost_usd = (tokens_used / 1000) * 0.00015

    return {
        "label": label,
        "response": response.choices[0].message.content,
        "tokens": tokens_used,
        "time_seconds": elapsed,
        "cost_usd": cost_usd,
        "cost_kes": cost_usd * 130
    }


def compare_prompts(prompt_versions, test_questions):
    """
    Runs all test questions against all prompt versions.
    Prints a side-by-side comparison.

    prompt_versions: list of (label, system_prompt, temperature)
    test_questions: list of question strings
    """
    print("\n" + "=" * 65)
    print("PROMPT COMPARISON TEST")
    print(f"Testing {len(prompt_versions)} prompt versions")
    print(f"Against {len(test_questions)} test questions")
    print("=" * 65)

    all_results = []

    for question_num, question in enumerate(test_questions, 1):
        print(f"\n{'─' * 65}")
        print(f"QUESTION {question_num}: {question[:70]}...")
        print(f"{'─' * 65}")

        for label, system_prompt, temperature in prompt_versions:
            print(f"\n▶ {label} (temp={temperature})")
            print(f"  Calling API...")

            result = test_prompt(
                system_prompt=system_prompt,
                user_message=question,
                temperature=temperature,
                label=label
            )

            print(f"  Time: {result['time_seconds']}s  "
                  f"Tokens: {result['tokens']}  "
                  f"Cost: KES {result['cost_kes']:.4f}")
            print(f"\n  Response:")
            print(f"  {result['response'][:300]}...")

            all_results.append({
                "question": question[:50],
                **result
            })

    # Summary table
    print(f"\n{'=' * 65}")
    print("COST SUMMARY")
    print(f"{'=' * 65}")
    print(f"{'Version':<25} {'Avg Tokens':<12} {'Total Cost (KES)'}")
    print(f"{'─' * 65}")

    from collections import defaultdict
    version_totals = defaultdict(list)
    for r in all_results:
        version_totals[r["label"]].append(r)

    for label, results in version_totals.items():
        avg_tokens = sum(r["tokens"] for r in results) / len(results)
        total_cost = sum(r["cost_kes"] for r in results)
        print(f"{label:<25} {avg_tokens:<12.0f} KES {total_cost:.4f}")

    print(f"{'=' * 65}\n")


# ── TEST YOUR THREE NICHE PROMPTS ─────────────────────────────

if __name__ == "__main__":

    # ── PHARMA PROMPT COMPARISON ──────────────────────────────
    print("\n" + "█" * 65)
    print("TESTING: PHARMACEUTICAL COMPLIANCE BOT")
    print("█" * 65)

    pharma_standard = """You are PharmAssist, a pharmaceutical
    compliance assistant for KPPB-regulated companies in Kenya.
    Answer compliance questions clearly."""

    pharma_chainofthought = """You are PharmAssist, a pharmaceutical
    compliance AI for KPPB-regulated companies in Kenya.

    For every question think through this process:
    Step 1 — What regulation applies?
    Step 2 — What exactly is required?
    Step 3 — What are the consequences of non-compliance?
    Step 4 — What specific actions are needed?

    Structure your response with clear headers.
    Cite regulatory references.
    Flag HIGH RISK items clearly."""

    pharma_questions = [
        "What documentation is required when a batch fails QC testing?",
        "How quickly must a product recall be reported to KPPB?"
    ]

    compare_prompts(
        prompt_versions=[
            ("Standard Prompt", pharma_standard, 0.3),
            ("Chain-of-Thought", pharma_chainofthought, 0.2)
        ],
        test_questions=pharma_questions
    )

    # ── HEALTH PROMPT COMPARISON ──────────────────────────────
    print("\n" + "█" * 65)
    print("TESTING: HEALTH & WELLNESS BOT (ZURI)")
    print("█" * 65)

    health_standard = """You are Zuri, a customer assistant
    for NutriCore Health supplements in Nairobi. Help customers
    with products and orders."""

    health_warm = """You are Zuri, the warm and knowledgeable
    AI assistant for NutriCore Health in Nairobi, Kenya.

    You genuinely care about customers' health goals.
    Use Swahili greetings naturally.
    Always recommend consulting a doctor for medical conditions.
    Keep responses under 120 words for simple questions.
    End with an offer to help further."""

    health_questions = [
        "I have been taking your protein for 2 weeks but not seeing results",
        "Is your collagen safe during pregnancy?"
    ]

    compare_prompts(
        prompt_versions=[
            ("Standard Prompt", health_standard, 0.7),
            ("Warm + Guardrails", health_warm, 0.7)
        ],
        test_questions=health_questions
    )

    # ── SAAS PROMPT COMPARISON ────────────────────────────────
    print("\n" + "█" * 65)
    print("TESTING: SAAS SUPPORT BOT (ATLAS)")
    print("█" * 65)

    saas_standard = """You are Atlas, a support assistant
    for LabTrack laboratory management software. Help users
    with their questions."""

    saas_structured = """You are Atlas, the AI support assistant
    for LabTrack laboratory management software.

    For technical how-to questions:
    - Use numbered steps
    - Bold navigation paths like **Menu → Submenu**
    - End with a helpful tip
    - Ask if the issue was resolved

    For error codes:
    - Explain what the error means in plain language
    - Give the fix in under 5 steps
    - Explain why it happened
    - Offer a prevention tip

    Keep all responses under 200 words."""

    saas_questions = [
        "Getting error 5001 when trying to approve results",
        "How do I add a new user to our account?"
    ]

    compare_prompts(
        prompt_versions=[
            ("Standard Prompt", saas_standard, 0.5),
            ("Structured Format", saas_structured, 0.3)
        ],
        test_questions=saas_questions
    )
    print("Script loaded successfully")