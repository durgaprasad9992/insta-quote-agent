import os
import random
import requests
from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont

# Load OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# Instagram config
IG_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
IG_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID")

# ---------- TEXT AGENT ----------
def generate_text():
    prompt = """
    Create a short, clean, non-offensive dark humour quote.
    Style: romantic, funny, breakup, youth friendly.
    No violence, no hate, no self-harm.
    Make audience smile.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=60
    )

    return response.choices[0].message.content.strip()


# ---------- IMAGE AGENT ----------
def generate_image(text):
    img = Image.new("RGB", (1080, 1080), "black")
    draw = ImageDraw.Draw(img)

    colors = [
        "red", "orange", "yellow", "green",
        "blue", "indigo", "violet", "white"
    ]

    color = random.choice(colors)

    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 70)
    except:
        font = ImageFont.load_default()

    # Outline if black text
    if color == "black":
        draw.text((540, 540), text, font=font, fill="white", anchor="mm")
    else:
        draw.text((540, 540), text, font=font, fill=color, anchor="mm")

    path = "post.png"
    img.save(path)
    return path


# ---------- INSTAGRAM AGENT ----------
def post_to_instagram(image_path, caption):
    # Step 1 — Upload image container
    url = f"https://graph.facebook.com/v19.0/{IG_ACCOUNT_ID}/media"

    with open(image_path, "rb") as img:
        files = {"image_url": img}
        data = {
            "caption": caption,
            "access_token": IG_TOKEN
        }
        res = requests.post(url, data=data)

    creation_id = res.json().get("id")

    # Step 2 — Publish
    publish_url = f"https://graph.facebook.com/v19.0/{IG_ACCOUNT_ID}/media_publish"
    data = {
        "creation_id": creation_id,
        "access_token": IG_TOKEN
    }
    requests.post(publish_url, data=data)


# ---------- MAIN BOT FUNCTION ----------
def run_bot():
    print("🤖 Running bot...")

    text = generate_text()
    print("Generated text:", text)

    image = generate_image(text)
    print("Image created")

    post_to_instagram(image, text)
    print("Posted to Instagram successfully ✅")
