import os
import glob
import random
from PIL import Image, ImageDraw, ImageFont

TEMPLATES_DIR = "assets/templates"
os.makedirs(TEMPLATES_DIR, exist_ok=True)

def generate_default_templates():
    """Generates vibrant, clean meme background canvas templates if none exist."""
    palettes = {
        "drake": ((245, 158, 11), (251, 191, 36)),       # Warm gold
        "distracted_bf": ((59, 130, 246), (96, 165, 250)),# Blue gradient
        "two_buttons": ((239, 68, 68), (248, 113, 113)),  # Red/coral
        "expanding_brain": ((147, 51, 234), (192, 132, 252)), # Cosmic purple
        "change_my_mind": ((16, 185, 129), (52, 211, 153)),  # Emerald
        "this_is_fine": ((249, 115, 22), (251, 146, 60)),    # Orange fire
        "woman_yelling_cat": ((236, 72, 153), (244, 114, 182)), # Pink/magenta
        "shut_up_money": ((34, 197, 94), (74, 222, 128))     # Green cash
    }
    
    for name, (c1, c2) in palettes.items():
        filepath = os.path.join(TEMPLATES_DIR, f"{name}.png")
        if not os.path.exists(filepath):
            # Create a 700x700 stylized background
            img = Image.new("RGB", (700, 700), color=c1)
            draw = ImageDraw.Draw(img)
            # Add decorative visual frame & vignette
            draw.rectangle([20, 20, 680, 680], outline=(255, 255, 255, 180), width=4)
            # Inner badge
            draw.rectangle([100, 100, 600, 600], outline=c2, width=2)
            img.save(filepath)

def get_template_image(template_id: str):
    """Returns a PIL image for the requested template or a random fallback."""
    generate_default_templates()
    path = os.path.join(TEMPLATES_DIR, f"{template_id}.png")
    if os.path.exists(path):
        return Image.open(path)
    
    # Try finding an image from memes/memes/
    meme_files = glob.glob("memes/memes/*.jpg") + glob.glob("memes/memes/*.png")
    if meme_files:
        chosen = random.choice(meme_files)
        try:
            return Image.open(chosen)
        except Exception:
            pass
            
    # Fallback solid
    return Image.new("RGB", (700, 700), color=(40, 50, 70))

if __name__ == "__main__":
    generate_default_templates()
    print("Meme background templates initialized!")
