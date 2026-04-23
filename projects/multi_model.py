# multi_model.py
# Day 3 — AXIOM 60-Day AI Engineering Program
# Multi-Model AI Comparison Tool
# Calls OpenAI, Anthropic and Gemini from one script
# Real use: recommend the right model to clients

import os
import time
from dotenv import load_dotenv

# -------------------------------------------------------
# SECTION 1 — CONFIGURATION
# All settings in one place at the top.
# This is how senior engineers structure scripts —
# nothing is buried deep in functions.
# -------------------------------------------------------

load_dotenv(dotenv_path=r"C:\Users\pc\ai-engineering\.env")

# API Keys — loaded from .env, never hardcoded
OPENAI_KEY    = os.getenv("OPENAI_API_KEY")
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")
GEMINI_KEY    = os.getenv("GEMINI_API_KEY")

# Model names — defined once at the top
# When better models release, you change it here only
OPENAI_MODEL    = "gpt-4o-mini"
ANTHROPIC_MODEL = "claude-3-5-haiku-20241022"
GEMINI_MODEL    = "gemini-2.0-flash"

# Shared settings for all models
MAX_TOKENS  = 500
TEMPERATURE = 0.7


# -------------------------------------------------------
# SECTION 2 — SAFETY CHECKS
# Verify all three keys exist before running anything.
# This catches configuration errors immediately with
# clear messages — not confusing crashes later.
# -------------------------------------------------------

def check_keys():
    missing = []
    if not OPENAI_KEY:
        missing.append("OPENAI_API_KEY")
    if not ANTHROPIC_KEY:
        missing.append("ANTHROPIC_API_KEY")
    if not GEMINI_KEY:
        missing.append("GEMINI_API_KEY")
    if missing:
        print(f"ERROR: Missing keys in .env: {', '.join(missing)}")
        print("Add them to your .env file and try again.")
        exit()
    print("All API keys loaded successfully.\n")


# -------------------------------------------------------
# SECTION 3 — THREE MODEL FUNCTIONS
# Each function calls one AI model.
# They all take the same inputs and return the same
# output format so they are interchangeable.
# This pattern is called a consistent interface —
# you can swap models without changing any other code.
# -------------------------------------------------------

def call_openai(system_prompt, user_message):
    """
    Calls OpenAI GPT model.
    Returns: dict with response text, tokens used, time taken
    """
    from openai import OpenAI

    client = OpenAI(api_key=OPENAI_KEY)
    start_time = time.time()

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_message}
            ],
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE
        )
        elapsed = round(time.time() - start_time, 2)
        return {
            "model":    OPENAI_MODEL,
            "response": response.choices[0].message.content,
            "tokens":   response.usage.total_tokens,
            "time":     elapsed,
            "error":    None
        }

    except Exception as e:
        # Catch any error and return it cleanly
        # The rest of the script keeps running
        return {
            "model":    OPENAI_MODEL,
            "response": None,
            "tokens":   0,
            "time":     0,
            "error":    str(e)
        }


def call_anthropic(system_prompt, user_message):
    """
    Calls Anthropic Claude model.
    Note: Anthropic separates system from messages differently
    to OpenAI — system is a top-level parameter, not a message.
    """
    import anthropic

    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    start_time = time.time()

    try:
        response = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=MAX_TOKENS,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )
        elapsed = round(time.time() - start_time, 2)
        return {
            "model":    ANTHROPIC_MODEL,
            "response": response.content[0].text,
            "tokens":   response.usage.input_tokens + response.usage.output_tokens,
            "time":     elapsed,
            "error":    None
        }

    except Exception as e:
        return {
            "model":    ANTHROPIC_MODEL,
            "response": None,
            "tokens":   0,
            "time":     0,
            "error":    str(e)
        }


def call_gemini(system_prompt, user_message):
    """
    Calls Google Gemini model.
    Note: Gemini combines system prompt and user message
    differently — system is set via model configuration.
    """
    import google.generativeai as genai

    genai.configure(api_key=GEMINI_KEY)
    start_time = time.time()

    try:
        model = genai.GenerativeModel(
            model_name=GEMINI_MODEL,
            system_instruction=system_prompt
        )
        response = model.generate_content(
            user_message,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=MAX_TOKENS,
                temperature=TEMPERATURE
            )
        )
        elapsed = round(time.time() - start_time, 2)
        return {
            "model":    GEMINI_MODEL,
            "response": response.text,
            "tokens":   response.usage_metadata.total_token_count,
            "time":     elapsed,
            "error":    None
        }

    except Exception as e:
        return {
            "model":    GEMINI_MODEL,
            "response": None,
            "tokens":   0,
            "time":     0,
            "error":    str(e)
        }


# -------------------------------------------------------
# SECTION 4 — DISPLAY FUNCTION
# Formats results cleanly for the terminal.
# In a real client project this output goes to a
# dashboard, Google Sheet, or comparison report.
# -------------------------------------------------------

def display_result(result):
    print(f"\n{'=' * 55}")
    print(f"MODEL: {result['model']}")
    print(f"{'=' * 55}")

    if result["error"]:
        print(f"ERROR: {result['error']}")
    else:
        print(f"Time:   {result['time']} seconds")
        print(f"Tokens: {result['tokens']}")
        print(f"\nResponse:")
        print(f"{'-' * 55}")
        print(result["response"])

    print(f"{'=' * 55}")


# -------------------------------------------------------
# SECTION 5 — MAIN EXECUTION
# This is where you define your system prompt and
# question then run all three models and compare.
# -------------------------------------------------------

if __name__ == "__main__":

    check_keys()

    print("=" * 55)
    print("AXIOM — Multi-Model AI Comparison Tool")
    print("Day 3 — OpenAI vs Anthropic vs Gemini")
    print("=" * 55)

    # -------------------------------------------------------
    # YOUR SYSTEM PROMPT
    # This is the AI's identity for this session.
    # For this test we are using your exact niche.
    # -------------------------------------------------------
    system = """You are an expert AI automation consultant
    specializing in pharmaceutical and health companies
    in East Africa. You give concise, measurable advice
    focused on real business outcomes."""

    # -------------------------------------------------------
    # YOUR QUESTION
    # Same question sent to all three models.
    # This lets you compare quality fairly.
    # -------------------------------------------------------
    question = """A pharmaceutical distribution company in
    Nairobi has 30 staff and spends 15 hours per week on
    manual regulatory document review. Describe the exact
    AI system you would build to automate this, including
    the specific tools and estimated time savings."""

    print(f"\nQuestion sent to all three models:")
    print(f"{'-' * 55}")
    print(question.strip())
    print(f"{'-' * 55}")
    print("\nCalling all three APIs...\n")

    # Call all three models
    print("Calling OpenAI...")
    openai_result    = call_openai(system, question)

    print("Calling Anthropic...")
    anthropic_result = call_anthropic(system, question)

    print("Calling Gemini...")
    gemini_result    = call_gemini(system, question)

    # Display all three results
    display_result(openai_result)
    display_result(anthropic_result)
    display_result(gemini_result)

    # -------------------------------------------------------
    # COMPARISON SUMMARY
    # This is what you show a client when recommending
    # which model to use for their project.
    # -------------------------------------------------------
    print("\n" + "=" * 55)
    print("COMPARISON SUMMARY")
    print("=" * 55)
    for result in [openai_result, anthropic_result, gemini_result]:
        if not result["error"]:
            print(f"{result['model']:<35} {result['time']}s   {result['tokens']} tokens")
    print("=" * 55)