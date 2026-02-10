import os
import random
import time
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from openai import OpenAI
from dotenv import load_dotenv

# =========================
# Load environment
# =========================
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
IG_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

client = OpenAI(api_key=OPENAI_API_KEY)

# =========================
# Graph API version
# =========================
GRAPH_API_VERSION = "v24.0"
BASE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

# =========================
# Pick dynamic vibrant background
# =========================
def pick_background(quote, width=1080, height=1080):
    import urllib.parse

    mood = "flirty"
    q = quote.lower()
    if any(word in q for word in ["kiss","love","heart"]):
        mood = "romantic"
    elif any(word in q for word in ["smile","laugh","funny"]):
        mood = "humor"
    elif any(word in q for word in ["miss","alone","lost"]):
        mood = "heartbreak"

    query_map = {
        "romantic": "sunset love hearts flowers",
        "flirty": "playful smile flirt colors",
        "heartbreak": "rain night lonely soft",
        "humor": "funny bright playful"
    }
    search_query = urllib.parse.quote(query_map[mood])

    # Unsplash random image
    unsplash_url = f"https://source.unsplash.com/{width}x{height}/?{search_query}"
    return unsplash_url

# =========================
# Generate poetic/flirty quote
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
# Create image with quote
# =========================
def create_quote_image(quote, filename="quote.jpg"):
    bg_url = pick_background(quote)
    response = requests.get(bg_url)
    img = Image.open(BytesIO(response.content)).convert("RGB")
    img = img.resize((1080,1080))
    img = img.filter(ImageFilter.GaussianBlur(1))

    # Vibrance
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(random.uniform(1.1,1.5))

    draw = ImageDraw.Draw(img)

    # Font
    font_path = os.path.join("fonts","Montserrat-Bold.ttf")
    font_size = 80
    try:
        font = ImageFont.truetype(font_path, font_size)
    except OSError:
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

    img = img.convert("RGB")
    img.save(filename, quality=95)
    return filename

# =========================
# Upload to Cloudinary
# =========================
def upload_to_cloudinary(file_path):
    url = f"https://api.cloudinary.com/v1_1/{CLOUDINARY_CLOUD_NAME}/image/upload"
    with open(file_path, "rb") as f:
        files = {"file": f}
        data = {"upload_preset": "ml_default"}
        r = requests.post(url, files=files, data=data)
    res = r.json()
    return res.get("secure_url")

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
# Post to Instagram
# =========================
def post_to_instagram(img_url, caption):
    if not IG_ACCOUNT_ID or not ACCESS_TOKEN:
        print("❌ Missing Instagram credentials")
        return
    try:
        r = requests.post(
            f"{BASE_URL}/{IG_ACCOUNT_ID}/media",
            data={"image_url": img_url,"caption":caption,"access_token":ACCESS_TOKEN}
        ).json()
        if "id" not in r:
            print("❌ Media creation failed:", r)
            return
        creation_id = r["id"]
        requests.post(
            f"{BASE_URL}/{IG_ACCOUNT_ID}/media_publish",
            data={"creation_id": creation_id,"access_token":ACCESS_TOKEN}
        )
        print("📤 Posted successfully!")
        return creation_id
    except Exception as e:
        print("❌ Instagram error:", e)
        return None

# =========================
# Auto reply comments
# =========================
def auto_reply_comments(post_id):
    try:
        comments_url = f"{BASE_URL}/{post_id}/comments?access_token={ACCESS_TOKEN}"
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
                f"{BASE_URL}/{comment_id}/comments",
                data={"message":reply_text,"access_token":ACCESS_TOKEN}
            )
        print("💬 Auto-replied to comments")
    except Exception as e:
        print("⚠️ Comment AI error:", e)

# =========================
# Scheduler
# =========================
POST_INTERVALS = [4,6,8] # hours

def run_bot():
    while True:
        mood = random.choice(["romantic","flirty","heartbreak","humor"])
        quote = generate_poetic_quote(mood=mood)
        filename = create_quote_image(quote)
        img_url = upload_to_cloudinary(filename)
        caption = generate_caption(quote)
        post_id = post_to_instagram(img_url, caption)
        if post_id:
            auto_reply_comments(post_id)
        wait_hours = random.choice(POST_INTERVALS)
        print(f"⏳ Next post in {wait_hours} hours...\n")
        time.sleep(wait_hours*3600)
