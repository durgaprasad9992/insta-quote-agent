import os
import time
import random
import requests
from openai import OpenAI

# ==============================
# ENV VARIABLES
# ==============================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
IG_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

client = OpenAI(api_key=OPENAI_API_KEY)

# ==============================
# FALLBACK QUOTES (if OpenAI quota exceeded)
# ==============================
FALLBACK_QUOTES = [
    "You stole my heart… please return, EMI pending 💸",
    "Life is short. Make your WiFi strong 📶",
    "Success is simple — wake up, work, repeat 🔁",
    "Dream big. Start small. Act now 🚀",
    "Money can't buy happiness… but it buys pizza 🍕"
]

# ==============================
# GENERATE VIRAL TEXT
# ==============================
def generate_text():
    prompt = "Create a short, funny, viral Instagram quote (max 12 words)."

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=40,
        )
        text = response.choices[0].message.content.strip()
        print("📝 Quote:", text)
        return text

    except Exception as e:
        print("⚠️ OpenAI error:", e)
        fallback = random.choice(FALLBACK_QUOTES)
        print("📝 Using fallback quote:", fallback)
        return fallback


# ==============================
# GENERATE CAPTION + HASHTAGS
# ==============================
def generate_caption(quote):
    hashtags = [
        "#viral", "#trending", "#motivation", "#success",
        "#mindset", "#quotes", "#explore", "#instagood",
        "#life", "#growth", "#reels", "#ai"
    ]
    random.shuffle(hashtags)
    caption = f"{quote}\n\n{' '.join(hashtags[:8])}"
    print("📢 Caption created")
    return caption


# ==============================
# GET RANDOM IMAGE (FREE SOURCE)
# ==============================
def generate_image():
    # Free random high-quality image
    image_url = f"https://picsum.photos/1080?random={random.randint(1,999999)}"
    print("🖼 Image ready:", image_url)
    return image_url


# ==============================
# POST TO INSTAGRAM
# ==============================
def post_to_instagram(image_url, caption):
    if not IG_ACCOUNT_ID or not ACCESS_TOKEN:
        print("❌ Missing Instagram credentials")
        return

    try:
        # Step 1 — Create media container
        url = f"https://graph.facebook.com/v19.0/{IG_ACCOUNT_ID}/media"
        payload = {
            "image_url": image_url,
            "caption": caption,
            "access_token": ACCESS_TOKEN
        }

        r = requests.post(url, data=payload)
        data = r.json()

        if "id" not in data:
            print("❌ Media creation failed:", data)
            return

        creation_id = data["id"]
        print("✅ Media container created")

        # Step 2 — Publish
        publish_url = f"https://graph.facebook.com/v19.0/{IG_ACCOUNT_ID}/media_publish"
        payload = {
            "creation_id": creation_id,
            "access_token": ACCESS_TOKEN
        }

        r = requests.post(publish_url, data=payload)
        print("📤 Publish response:", r.json())

    except Exception as e:
        print("❌ Instagram error:", e)


# ==============================
# MAIN BOT LOOP
# ==============================
def run_bot():
    print("🚀 Bot started")

    while True:
        try:
            quote = generate_text()
            caption = generate_caption(quote)
            image_url = generate_image()

            print("📤 Uploading to Instagram...")
            post_to_instagram(image_url, caption)

        except Exception as e:
            print("❌ Bot error:", e)

        print("⏳ Waiting 6 hours for next post...\n")
        time.sleep(21600)  # 6 hours


# ==============================
# START BOT
# ==============================
if __name__ == "__main__":
    run_bot()
