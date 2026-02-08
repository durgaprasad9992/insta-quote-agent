import requests
from config import IG_ACCESS_TOKEN, IG_USER_ID

def post_to_instagram(image_url, caption):

    # Create media
    url = f"https://graph.facebook.com/v18.0/{IG_USER_ID}/media"
    payload = {
        "image_url": image_url,
        "caption": caption,
        "access_token": IG_ACCESS_TOKEN
    }
    r = requests.post(url, data=payload).json()
    creation_id = r.get("id")

    if not creation_id:
        print("Media creation failed:", r)
        return

    # Publish
    url = f"https://graph.facebook.com/v18.0/{IG_USER_ID}/media_publish"
    payload = {
        "creation_id": creation_id,
        "access_token": IG_ACCESS_TOKEN
    }
    r = requests.post(url, data=payload).json()
    print("Posted:", r)
