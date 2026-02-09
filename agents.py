import os
import time
import random
import requests
import base64
from datetime import datetime
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from openai import OpenAI

# ==============================
# ENV
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
    "You stole my heart… EMI still pending 💸",
    "Love you… but WiFi stronger 📶",
    "Single, but snacks committed 🍫",
    "Typing… deleting… loving you anyway ❤️",
    "Breakup done. Self-love started 🌱",
]

# ==============================
# VIBGYOR COLORS
# ==============================
VIBGYOR = [
    (148, 0, 211),   # Violet
    (75, 0, 130),    # Indigo
    (0, 0, 255),     # Blue
    (0, 255, 0),     # Green
    (255, 255, 0),   # Yellow
    (255, 127, 0),   # Orange
    (255, 0, 0),     # Red
]

# ==============================
# GENERATE QUOTE
# ==============================
def generate_text():
    prompt = (
        "Create a short (max 12 words) funny, romantic/comedy/breakup quote. "
        "Safe, positive, smile-inducing, no violence, no hate, no self-harm."
    )
    try:
        r = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=40,
        )
        text = r.choices[0].message.content.strip().strip('"')
        print("📝 Quote:", text)
        return text
    except Exception as e:
        print("⚠️ OpenAI error:", e)
        q = random.choice(FALLBACK_QUOTES)
        print("📝 Using fallback:", q)
        return q

# ==============================
# CAPTION + SMART HASHTAGS
# ==============================
def generate_caption(quote):
    core = [
        "#love", "#funny", "#quotes", "#smile",
        "#explorepage", "#instagood", "#romance", "#comedy",
        "#trending", "#viral", "#dailyquote", "#positivevibes"
    ]
    niche = random.sample(core, 8)
    caption = f"{quote}\n\n{' '.join(niche)}"
    print("📢 Caption ready")
    return caption

# ==============================
# CREATE BLACK IMAGE WITH VIBGYOR TEXT
# ==============================
def create_quote_image(quote):
    W, H = 1080, 1080
    img = Image.new("RGB", (W, H), (0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Try common fonts; fallback to default
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    font = None
    for p in font_paths:
        if os.path.exists(p):
            font = ImageFont.truetype(p, 72)
            break
    if font is None:
        font = ImageFont.load_default()

    # Wrap text
    words = quote.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        wbox = draw.textbbox((0, 0), test, font=font)
        if wbox[2] - wbox[0] <= W - 160:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)

    total_h = sum(draw.textbbox((0, 0), ln, font=font)[3] for ln in lines) + (len(lines)-1)*20
    y = (H - total_h) // 2

    for i, ln in enumerate(lines):
        color = VIBGYOR[i % len(VIBGYOR)]
        bbox = draw.textbbox((0, 0), ln, font=font)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2

        # White outline if text color is black (rare, but rule kept)
        outline = (255, 255, 255) if color == (0, 0, 0) else None
        if outline:
            for dx in (-2, -1, 1, 2):
                for dy in (-2, -1, 1, 2):
                    draw.text((x+dx, y+dy), ln, font=font, fill=outline)

        draw.text((x, y), ln, font=font, fill=color)
        y += (bbox[3] - bbox[1]) + 20

    # Save to bytes
    bio = BytesIO()
    img.save(bio, format="JPEG", quality=95)
    bio.seek(0)
    return bio.read()

# ==============================
# UPLOAD IMAGE TO IMGBB
# ==============================
def upload_to_imgbb(image_bytes):
    try:
        encoded = base64.b64encode(image_bytes)
        url = "https://api.imgbb.com/1/upload"
        payload = {"key": IMGBB_API_KEY, "image": encoded}
        r = requests.post(url, data=payload, timeout=30)
        data = r.json()
        if data.get("success"):
            final_url = data["data"]["url"]
            print("🖼 Image hosted:", final_url)
            return final_url
        else:
            print("❌ ImgBB failed:", data)
            return None
    except Exception as e:
        print("❌ ImgBB error:", e)
        return None

# ==============================
# POST TO INSTAGRAM
# ==============================
def post_to_instagram(image_url, caption):
    if not IG_ACCOUNT_ID or not ACCESS_TOKEN:
        print("❌ Missing Instagram credentials")
        return False
    try:
        # Create container
        url = f"https://graph.facebook.com/v19.0/{IG_ACCOUNT_ID}/media"
        payload = {
            "image_url": image_url,
            "caption": caption,
            "access_token": ACCESS_TOKEN
        }
        r = requests.post(url, data=payload, timeout=30)
        data = r.json()
        if "id" not in data:
            print("❌ Media creation failed:", data)
            return False

        creation_id = data["id"]
        print("✅ Media container created")

        # Publish
        pub = f"https://graph.facebook.com/v19.0/{IG_ACCOUNT_ID}/media_publish"
        r = requests.post(pub, data={
            "creation_id": creation_id,
            "access_token": ACCESS_TOKEN
        }, timeout=30)
        print("📤 Publish:", r.json())
        return True
    except Exception as e:
        print("❌ Instagram error:", e)
        return False

# ==============================
# SMART POSTING WINDOW
# ==============================
def sleep_until_next_slot():
    # Best engagement hours (local server time): 9, 13, 18, 21
    best_hours = [9, 13, 18, 21]
    now = datetime.now()
    next_hour = None
    for h in best_hours:
        if now.hour < h:
            next_hour = h
            break
    if next_hour is None:
        # Tomorrow 9 AM
        target = now.replace(day=now.day, hour=9, minute=0, second=0, microsecond=0) + \
                 (datetime(now.year, now.month, now.day, 0, 0) - datetime(now.year, now.month, now.day, 0, 0))
        # simple 12h fallback if date math tricky in container
        wait = 12 * 3600
    else:
        target = now.replace(hour=next_hour, minute=0, second=0, microsecond=0)
        wait = max(0, int((target - now).total_seconds()))
    print(f"⏳ Sleeping {wait//60} minutes until next smart slot...")
    time.sleep(wait if wait > 0 else 60)

# ==============================
# MAIN LOOP
# ==============================
def run_bot():
    print("🚀 Bot running (VIRAL v2)...")

    while True:
        try:
            quote = generate_text()
            caption = generate_caption(quote)

            # Create styled image
            img_bytes = create_quote_image(quote)
            img_url = upload_to_imgbb(img_bytes)

            if img_url:
                print("📤 Uploading to Instagram...")
                ok = post_to_instagram(img_url, caption)
                if not ok:
                    print("⚠️ Post failed, will retry next slot.")
            else:
                print("⚠️ Image hosting failed, skipping this round.")

        except Exception as e:
            print("❌ Bot error:", e)

        sleep_until_next_slot()

# ==============================
# START
# ==============================
if __name__ == "__main__":
    run_bot()
