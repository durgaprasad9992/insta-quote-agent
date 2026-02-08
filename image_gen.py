from PIL import Image, ImageDraw, ImageFont
import random, textwrap

WIDTH, HEIGHT = 1080, 1080

VIBGYOR = [
    (148,0,211),(75,0,130),(0,0,255),(0,255,0),
    (255,255,0),(255,127,0),(255,0,0),(0,0,0)
]

def create_post(text, output="post.png"):

    img = Image.new("RGB", (WIDTH, HEIGHT), (0,0,0))
    draw = ImageDraw.Draw(img)

    font = ImageFont.truetype("fonts/Montserrat-Bold.ttf", 90)
    color = random.choice(VIBGYOR)

    wrapped = "\n".join(textwrap.wrap(text, width=14))

    w, h = draw.multiline_textsize(wrapped, font=font)
    x, y = (WIDTH-w)/2, (HEIGHT-h)/2

    if color == (0,0,0):
        for dx in [-2,-1,0,1,2]:
            for dy in [-2,-1,0,1,2]:
                draw.multiline_text((x+dx,y+dy), wrapped, font=font, fill=(255,255,255))

    draw.multiline_text((x,y), wrapped, font=font, fill=color, align="center")
    img.save(output)
    return output
