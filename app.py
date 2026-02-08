from agents import *
from safety import is_safe
from image_gen import create_post
from uploader_cloudinary import upload_image
from instagram_api import post_to_instagram


def run_pipeline():

    idea = generate_idea()
    quote = write_quote(idea)

    if not is_safe(quote):
        print("Unsafe quote skipped")
        return

    quote = optimize_style(quote)
    caption = generate_caption(quote)

    image_path = create_post(quote)
    image_url = upload_image(image_path)

    post_to_instagram(image_url, caption)

    print("Posted successfully")
