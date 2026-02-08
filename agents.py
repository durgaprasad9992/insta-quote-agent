from openai import OpenAI
from config import OPENAI_API_KEY
import random

client = OpenAI(api_key=OPENAI_API_KEY)

def ask_gpt(prompt):
    r = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,
    )
    return r.choices[0].message.content.strip()


def generate_idea():
    prompt = """
Generate 5 wholesome Instagram quote ideas.
Themes: romantic warmth, healing breakup, cute humour, youth relatable, smile-inducing.
Avoid sadness, hate, violence, self-harm.
Return only one short idea.
"""
    return ask_gpt(prompt)


def write_quote(idea):
    prompt = f"""
Write a short Instagram quote from idea:

{idea}

Rules:
- Gentle dark aesthetic but positive
- Smile-inducing
- Youth friendly
- Max 18 words
- Clean language
- May include 0–1 emoji randomly
Avoid sadness, hate, violence, negativity.
"""
    return ask_gpt(prompt)


def optimize_style(quote):
    prompt = f"""
Rewrite for Instagram readability:
- Better rhythm
- Emotional warmth
- Max 2 lines
Quote:
{quote}
"""
    return ask_gpt(prompt)


def generate_caption(quote):
    prompt = f"""
Write Instagram caption for:

{quote}

Style:
- Warm, minimal
- Add 5–7 hashtags
- No cringe or spam
- Youth friendly
"""
    return ask_gpt(prompt)
