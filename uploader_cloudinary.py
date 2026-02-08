import cloudinary
import cloudinary.uploader
from config import *

cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET
)

def upload_image(path):
    r = cloudinary.uploader.upload(path)
    return r["secure_url"]
