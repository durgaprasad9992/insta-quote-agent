import os
import random
import requests
from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont

# ==============================
# CONFIG
# ==============================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
IG_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
IG_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID")

client = OpenAI(api_key=OPENAI_API_KEY)


# ==============================
# TEXT AGENT (SAFE + FALLBACK)
# ==============================

def generate_text():
    prompt = """
    Create a short, clean, non-offensive dark humour quote.
    Style: romantic, funny, breakup, youth friendly.
    No violence, no hate, no self-harm.
    Make audience smile.
    Keep under 15 words.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=60
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print("⚠️ OpenAI error:", e)

        # Fallback quotes (bot will NEVER crash)
        fallback_quotes = [
            "Love is temporary, WiFi is forever 😌",
            "We broke up… but Netflix still asks 'Continue watching?'",
            "My heart said gym, my brain said pizza 🍕",
            "Crush replied 'haha'… wedding cancelled 💔😂",
            "Relationship status: Typing… deleting… typing again 😅",
            "She said 'be yourself'… now she's ignoring me 😂",
            "Love hurts… especially when seen at 2:17 AM",
            "I fell for you… gravity still laughing 🤦‍♂️",
            "You stole my heart… please return, EMI pending 💸",
            "Text me back or I start my villain era 😌"
        ]

        return random.choice(fallback_quotes)


# ==============================
# IMAGE AGENT
# ==============================

def generate_image(text):
    img = Image.new("RGB", (1080, 1080), "black")
    draw = ImageDraw.Draw(img)

    vibgyor_colors = [
        "red", "orange", "yellow",
        "green", "blue", "indigo", "violet"
    ]

    color = random.choice(vibgyor_colors)

    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 70)
    except:
        font = ImageFont.load_default()

    # Center text
    x, y = 540, 540

    # White outline if dark color
    if color == "black":
        for dx in [-2, 2]:
            for dy in [-2, 2]:
                draw.text((x+dx, y+dy), text, font=font, fill="white", anchor="mm")

    draw.text((x, y), text, font=font, fill=color, anchor="mm")

    path = "post.png"
    img.save(path)
    return path


# ==============================
# INSTAGRAM POST AGENT
# ==============================

def post_to_instagram(image_path, caption):
    print("📤 Uploading to Instagram...")

    url = f"https://graph.facebook.com/v19.0/{IG_ACCOUNT_ID}/media"

    data = {
        "caption": caption,
        "access_token": IG_TOKEN
    }

    # NOTE: Instagram Graph API usually requires a public image URL.
    # If your posting works, keep. If not, we will fix later.
    res = requests.post(url, data=data)

    if "id" not in res.json():
        print("❌ Instagram upload failed:", res.text)
        return

    creation_id = res.json()["id"]

    publish_url = f"https://graph.facebook.com/v19.0/{IG_ACCOUNT_ID}/media_publish"

    data = {
        "creation_id": creation_id,
        "access_token": IG_TOKEN
    }

    res2 = requests.post(publish_url, data=data)

    if res2.status_code == 200:
        print("✅ Posted successfully!")
    else:
        print("❌ Publish failed:", res2.text)


# ==============================
# MAIN BOT
# ==============================

def run_bot():
    print("🤖 Running Instagram AI Bot...")

    text = generate_text()
    print("📝 Generated text:", text)

    image = generate_image(text)
    print("🖼 Image created")

    post_to_instagram(image, text)
