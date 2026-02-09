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

print("🚀 Romantic Viral Bot Started")

# ==============================
# MOOD BACKGROUNDS
# ==============================
ROMANTIC_BG = [
    "https://images.unsplash.com/photo-1518199266791-5375a83190b7",
    "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee",
]

FLIRTY_BG = [
    "https://images.unsplash.com/photo-1492724441997-5dc865305da7",
    "https://images.unsplash.com/photo-1517841905240-472988babdf9",
]

BREAKUP_BG = [
    "https://images.unsplash.com/photo-1500534623283-312aade485b7",
]

# ==============================
# GENERATE SPICY QUOTE
# ==============================
def generate_text():
    prompt = """
    Create a SHORT romantic or flirty quote (max 14 words).
    Emotional, deep, slightly spicy, heart-touching, viral.
    Should make audience feel loved, connected, smiling.
    No violence, no hate, no sadness.
    """

    try:
        r = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=60,
        )
        text = r.choices[0].message.content.strip().strip('"')
        print("💬 Quote:", text)
        return text
    except:
        fallback = random.choice([
            "Are you WiFi? Because I feel connected instantly ❤️",
            "Your smile is my favorite notification 💌",
            "I fell for you… and never checked gravity 💫",
            "Love you softly, miss you loudly 💕",
            "You + Me = Forever sounds perfect 💍"
        ])
        print("💬 Fallback:", fallback)
        return fallback

# ==============================
# CAPTION
# ==============================
def generate_caption(quote):
    hashtags = [
        "#love", "#romantic", "#flirty", "#viral",
        "#couplegoals", "#explorepage", "#instalove",
        "#heart", "#relationship", "#smile", "#emotional"
    ]
    random.shuffle(hashtags)
    return f"{quote}\n\n{' '.join(hashtags[:8])}"

# ==============================
# PICK BACKGROUND BASED ON MOOD
# ==============================
def pick_background(quote):
    q = quote.lower()
    if "miss" in q or "alone" in q:
        url = random.choice(BREAKUP_BG)
    elif "kiss" in q or "smile" in q or "love" in q:
        url = random.choice(ROMANTIC_BG)
    else:
        url = random.choice(FLIRTY_BG)

    # Make sure direct JPG
    return url + "?auto=format&fit=crop&w=1080&q=80"

# ==============================
# CREATE BIG, CLEAR TEXT IMAGE
# ==============================
def create_quote_image(quote):
    bg_url = pick_background(quote)
    bg_data = requests.get(bg_url).content
    img = Image.open(BytesIO(bg_data)).convert("RGB")
    img = img.resize((1080, 1080))

    draw = ImageDraw.Draw(img)

    # Bigger font
    font_size = 95
    font = None
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
    ]
    for p in paths:
        if os.path.exists(p):
            font = ImageFont.truetype(p, font_size)
            break
    if font is None:
        font = ImageFont.load_default()

    # Wrap text
    words = quote.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        wbox = draw.textbbox((0, 0), test, font=font)
        if wbox[2] - wbox[0] <= 900:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)

    total_h = sum(draw.textbbox((0, 0), ln, font=font)[3] for ln in lines) + 20*(len(lines)-1)
    y = (1080 - total_h)//2

    for ln in lines:
        bbox = draw.textbbox((0, 0), ln, font=font)
        x = (1080 - (bbox[2]-bbox[0]))//2

        # Glow for readability
        for dx in range(-3,4):
            for dy in range(-3,4):
                draw.text((x+dx, y+dy), ln, font=font, fill=(0,0,0))

        draw.text((x, y), ln, font=font, fill=(255,255,255))
        y += (bbox[3]-bbox[1]) + 20

    bio = BytesIO()
    img.save(bio, format="JPEG", quality=95)
    bio.seek(0)
    return bio.read()

# ==============================
# UPLOAD TO IMGBB
# ==============================
def upload_to_imgbb(img_bytes):
    encoded = base64.b64encode(img_bytes)
    r = requests.post("https://api.imgbb.com/1/upload", data={
        "key": IMGBB_API_KEY,
        "image": encoded
    })
    data = r.json()
    if data.get("success"):
        print("🖼 Image hosted")
        return data["data"]["url"]
    print("❌ ImgBB error:", data)
    return None

# ==============================
# POST TO INSTAGRAM
# ==============================
def post_to_instagram(img_url, caption):
    url = f"https://graph.facebook.com/v19.0/{IG_ACCOUNT_ID}/media"
    r = requests.post(url, data={
        "image_url": img_url,
        "caption": caption,
        "access_token": ACCESS_TOKEN
    }).json()

    if "id" not in r:
        print("❌ Media error:", r)
        return

    creation_id = r["id"]
    requests.post(
        f"https://graph.facebook.com/v19.0/{IG_ACCOUNT_ID}/media_publish",
        data={"creation_id": creation_id, "access_token": ACCESS_TOKEN}
    )
    print("📤 Posted successfully!")

# ==============================
# LOOP
# ==============================
def run_bot():
    while True:
        quote = generate_text()
        caption = generate_caption(quote)
        img_bytes = create_quote_image(quote)
        img_url = upload_to_imgbb(img_bytes)

        if img_url:
            post_to_instagram(img_url, caption)

        print("⏳ Waiting 6 hours...\n")
        time.sleep(21600)

if __name__ == "__main__":
    run_bot()
