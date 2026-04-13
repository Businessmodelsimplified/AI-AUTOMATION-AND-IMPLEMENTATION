import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path=r"C:\Users\pc\ai-engineering\.env")
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("ERROR: No API key found in .env file")
    print("Check that .env exists at C:\\Users\\pc\\ai-engineering\\.env")
    exit()

client = OpenAI(api_key=api_key)

def ask_ai(user_message, system_prompt=None):
    messages = []
    if system_prompt:
        messages.append({
            "role": "system",
            "content": system_prompt
        })
    messages.append({
        "role": "user",
        "content": user_message
    })
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=600,
        temperature=0.7
    )
    return response.choices[0].message.content

if __name__ == "__main__":

    system = """You are an expert AI automation consultant 
    specializing in pharmaceutical and health companies in 
    East Africa. You speak concisely and always connect AI 
    capabilities to specific business outcomes with 
    measurable results."""

    question = """What are the top 3 AI automation 
    opportunities for a pharmaceutical distribution company 
    in Nairobi with 30 staff? For each opportunity include 
    the estimated hours saved per week and the tools 
    required to build it."""

    print("=" * 55)
    print("AXIOM AI ENGINEERING — Day 2 First Script")
    print("=" * 55)
    print("Sending request to OpenAI...\n")

    answer = ask_ai(question, system)

    print("AI Response:")
    print("-" * 55)
    print(answer)
    print("-" * 55)
    print("\nSuccess — your Python script is calling live AI.")
    print("Model used: gpt-4o-mini")