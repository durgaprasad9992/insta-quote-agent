import os
import random
import time
import base64
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from openai import OpenAI
from dotenv import load_dotenv

# =========================
# Load environment
# =========================
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
IG_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
IMGBB_API_KEY = os.getenv("IMGBB_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# =========================
# Backgrounds
# =========================
BACKGROUNDS = {
    "romantic": [
        "https://images.unsplash.com/photo-1518199266791-5375a83190b7",
        "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee"
    ],
    "flirty": [
        "https://images.unsplash.com/photo-1496307042754-b4aa456c4a2d",
        "https://images.unsplash.com/photo-1517841905240-472988babdf9"
    ],
    "heartbreak": [
        "https://images.unsplash.com/photo-1500534623283-312aade485b7"
    ],
    "humor": [
        "https://images.unsplash.com/photo-1501004318641-b39e6451bec6"
    ]
}

# =========================
# Generate poetic quote
# =========================
def generate_poetic_quote(mood=None):
    mood_text = f"mood: {mood}" if mood else ""
    prompt = f"""
    Write a single poetic, romantic/flirty sentence (max 25 words)
    that feels freshly written, emotional, human-like, viral, and slightly witty.
    {mood_text}
    """
    try:
        r = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":prompt}],
            max_tokens=50
        )
        quote = r.choices[0].message.content.strip().strip('"')
        return quote
    except:
        return "I never planned on loving you… yet here I am, smiling like an idiot."

# =========================
# Pick background
# =========================
def pick_background(quote):
    q = quote.lower()
    if any(word in q for word in ["kiss","love","heart"]):
        return random.choice(BACKGROUNDS["romantic"])
    if any(word in q for word in ["smile","laugh","funny"]):
        return random.choice(BACKGROUNDS["humor"])
    if any(word in q for word in ["miss","alone","lost"]):
        return random.choice(BACKGROUNDS["heartbreak"])
    return random.choice(BACKGROUNDS["flirty"])

# =========================
# Create image
# =========================
def create_quote_image(quote, filename="quote.jpg"):
    bg_url = pick_background(quote)
    response = requests.get(bg_url + "?w=1080&h=1080&fit=crop")
    img = Image.open(BytesIO(response.content)).convert("RGB")
    img = img.resize((1080,1080))

    # Blur + overlay
    img = img.filter(ImageFilter.GaussianBlur(1))
    overlay = Image.new("RGBA", img.size, (0,0,0,120))
    img = Image.alpha_composite(img.convert("RGBA"), overlay)

    draw = ImageDraw.Draw(img)

    # ---------- FONT ----------
    font_path = os.path.join("fonts", "Montserrat-Bold.ttf")
    font_size = 80
    try:
        font = ImageFont.truetype(font_path, font_size)
    except OSError:
        print("⚠️ Bundled font not found, using default PIL font")
        font = ImageFont.load_default()

    import textwrap
    wrapped = textwrap.fill(quote, width=18)
    bbox = draw.multiline_textbbox((0,0), wrapped, font=font, align="center")
    x = (1080 - (bbox[2]-bbox[0])) // 2
    y = (1080 - (bbox[3]-bbox[1])) // 2

    # Shadow
    draw.multiline_text((x+3, y+3), wrapped, font=font, fill=(0,0,0), align="center")
    # Main text
    draw.multiline_text((x, y), wrapped, font=font, fill=(255,255,255), align="center")

    # Convert to RGB before saving JPEG
    img = img.convert("RGB")
    img.save(filename, quality=95)
    return filename

# =========================
# Generate caption
# =========================
def generate_caption(quote):
    hooks = [
        "Tag someone who makes your heart race 💌",
        "Send this to the one who makes you smile ❤️",
        "If this made you blush, share it 💫",
        "Love like this deserves to be shared 💕",
    ]
    hashtags = [
        "#love","#romantic","#flirty","#viral","#heart",
        "#relationship","#explorepage","#instagood","#foryou","#trending"
    ]
    return f"{quote}\n\n{random.choice(hooks)}\n\n{' '.join(hashtags[:8])}"

# =========================
# Upload to ImgBB
# =========================
def upload_to_imgbb(filename):
    with open(filename,"rb") as f:
        img_bytes = f.read()
    encoded = base64.b64encode(img_bytes)
    r = requests.post("https://api.imgbb.com/1/upload", data={"key": IMGBB_API_KEY,"image":encoded})
    data = r.json()
    if data.get("success"):
        return data["data"]["url"]
    print("❌ ImgBB failed:", data)
    return None

# =========================
# Post to Instagram
# =========================
def post_to_instagram(img_url, caption):
    if not IG_ACCOUNT_ID or not ACCESS_TOKEN:
        print("❌ Missing Instagram credentials")
        return
    try:
        r = requests.post(
            f"https://graph.facebook.com/v19.0/{IG_ACCOUNT_ID}/media",
            data={"image_url": img_url,"caption":caption,"access_token":ACCESS_TOKEN}
        ).json()
        if "id" not in r:
            print("❌ Media creation failed:", r)
            return
        creation_id = r["id"]
        requests.post(
            f"https://graph.facebook.com/v19.0/{IG_ACCOUNT_ID}/media_publish",
            data={"creation_id": creation_id,"access_token":ACCESS_TOKEN}
        )
        print("📤 Posted successfully!")
        return creation_id
    except Exception as e:
        print("❌ Instagram error:", e)
        return None

# =========================
# Auto-reply comments
# =========================
def auto_reply_comments(post_id):
    try:
        comments_url = f"https://graph.facebook.com/v19.0/{post_id}/comments?access_token={ACCESS_TOKEN}"
        r = requests.get(comments_url).json()
        for c in r.get("data", []):
            text = c.get("text","")
            comment_id = c.get("id")
            reply_prompt = f"Reply flirtatiously or romantically to this comment: {text}"
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role":"user","content":reply_prompt}],
                max_tokens=30
            )
            reply_text = response.choices[0].message.content.strip()
            requests.post(
                f"https://graph.facebook.com/v19.0/{comment_id}/comments",
                data={"message":reply_text,"access_token":ACCESS_TOKEN}
            )
        print("💬 Auto-replied to comments")
    except Exception as e:
        print("⚠️ Comment AI error:", e)

# =========================
# Scheduler
# =========================
POST_INTERVALS = [4,6,8] # hours between posts

def run_bot():
    while True:
        mood = random.choice(["romantic","flirty","heartbreak","humor"])
        quote = generate_poetic_quote(mood=mood)
        filename = create_quote_image(quote)
        caption = generate_caption(quote)
        img_url = upload_to_imgbb(filename)
        if img_url:
            post_id = post_to_instagram(img_url, caption)
            if post_id:
                auto_reply_comments(post_id)
        wait_hours = random.choice(POST_INTERVALS)
        print(f"⏳ Next post in {wait_hours} hours...\n")
        time.sleep(wait_hours*3600)
