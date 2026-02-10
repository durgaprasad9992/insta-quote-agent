import os
import random
import time
import base64
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

client = OpenAI(api_key=OPENAI_API_KEY)

# =========================
# Pick dynamic vibrant background
# =========================
def pick_background(quote, width=1080, height=1080):
    import urllib.parse

    mood = "flirty"
    q = quote.lower()
    if any(word in q for word in ["ki]()
