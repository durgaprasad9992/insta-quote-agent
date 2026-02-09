import os
import time
import random
import requests
import base64
from openai import OpenAI

# ==============================
# ENV VARIABLES
# ==============================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
IG_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
IMGBB_API_KEY = os.getenv("IMGBB_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

print("🚀 Instagram AI Bot Started...")
print("IG:", IG_ACCOUNT_ID)
print("TOKEN:", "Loaded" if ACCESS_TOKEN else "Missing")

# ==============================
# FALLBACK QUOTES
# ==============================
FALLBACK_QUOTES = [
    "You stole my heart… please return, EMI pending 💸",
    "Life is short. Make your WiFi strong 📶",
    "Success is simple — wake up, work, repeat 🔁",
    "Dream big. Start small. Act now 🚀",
    "Money can't buy happiness… but it buys pizza 🍕",
    "Coffee first. Everything else later ☕",
]

# ==============================
# GENERATE QUOTE
# ==============================
def generate_text():
    prompt = "Create a short funny romantic/comedy/breakup quote under 12 words. Safe, positive, smile-inducing."

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
        print("📝 Using fallback:", fallback)
        return fallback

# ==============================
# GENERATE CAPTION
# ==============================
def generate_caption(quote):
    hashtags = [
        "#viral", "#trending", "#funny", "#love", "#quotes",
        "#explorepage", "#instagood", "#life", "#smile",
        "#romance", "#comedy", "#motivation"
    ]
    random.shuffle(hashtags)
    caption = f"{quote}\n\n{' '.join(hashtags[:8])}"
    print("📢 Caption created")
    return caption

# ==============================
# GENERATE IMAGE → Upload to ImgBB
# ==============================
def generate_image():
    try:
        # Download random image
        img_url = f"https://picsum.photos/1080?random={random.randint(1,999999)}"
        img_data = requests.get(img_url).content

        # Encode base64
        encoded = base64.b64encode(img_data)

        # Upload to ImgBB
        upload_url = "https://api.imgbb.com/1/upload"
        payload = {
            "key": IMGBB_API_KEY,
            "image": encoded
        }

        r = requests.post(upload_url, data=payload)
        data = r.json()

        if data.get("success"):
            final_url = data["data"]["url"]
            print("🖼 Image uploaded:", final_url)
            return final_url
        else:
            print("❌ ImgBB upload failed:", data)
            return None

    except Exception as e:
        print("❌ Image error:", e)
        return None

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
# MAIN LOOP
# ==============================
def run_bot():
    print("🚀 Bot running...")

    while True:
        try:
            quote = generate_text()
            caption = generate_caption(quote)
            image_url = generate_image()

            if image_url:
                print("📤 Uploading to Instagram...")
                post_to_instagram(image_url, caption)

        except Exception as e:
            print("❌ Bot error:", e)

        print("⏳ Waiting 6 hours...\n")
        time.sleep(21600)

# ==============================
# START
# ==============================
if __name__ == "__main__":
    run_bot()
