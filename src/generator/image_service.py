import os
import glob
import random
import io
import base64
import requests
from PIL import Image, ImageDraw, ImageFont

TEMPLATES_DIR = "assets/templates"
os.makedirs(TEMPLATES_DIR, exist_ok=True)

DEFAULT_GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")

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
            img = Image.new("RGB", (700, 700), color=c1)
            draw = ImageDraw.Draw(img)
            draw.rectangle([20, 20, 680, 680], outline=(255, 255, 255, 180), width=4)
            draw.rectangle([100, 100, 600, 600], outline=c2, width=2)
            img.save(filepath)

def generate_gemini_image(prompt: str, api_key: str = None, timeout: int = 15):
    """
    Attempts to generate an image using Google Generative Language (Gemini/Imagen) API.
    Returns: PIL Image if successful, None otherwise.
    """
    key = api_key or DEFAULT_GEMINI_KEY
    if not key:
        return None

    # Supported image models to try in sequence
    models_to_try = [
        "gemini-2.5-flash-image",
        "gemini-3.1-flash-lite-image",
        "gemini-3.1-flash-image",
        "gemini-3-pro-image"
    ]

    for model in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"Generate a high-quality, vivid visual background suitable for a viral meme. Subject: {prompt}. Do not include text."
                }]
            }]
        }
        
        try:
            res = requests.post(url, json=payload, timeout=timeout)
            if res.status_code == 200:
                data = res.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    for part in parts:
                        if "inlineData" in part:
                            b64_data = part["inlineData"].get("data")
                            if b64_data:
                                img_bytes = base64.b64decode(b64_data)
                                return Image.open(io.BytesIO(img_bytes)).convert("RGB")
            elif res.status_code == 429:
                # Quota exceeded or rate limited on current model tier
                continue
        except Exception as e:
            continue

    return None

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

def get_meme_background(template_id: str, prompt: str = "", use_gemini: bool = True, api_key: str = None):
    """
    Unified background getter:
    1. If use_gemini is True and prompt is provided, attempts to generate via Gemini Image API.
    2. Gracefully falls back to curated meme template if API is rate-limited or fails.
    """
    if use_gemini and prompt:
        ai_img = generate_gemini_image(prompt, api_key=api_key)
        if ai_img is not None:
            return ai_img, True # (image, was_ai_generated)

    # Curated template fallback
    return get_template_image(template_id), False

if __name__ == "__main__":
    generate_default_templates()
    img, is_ai = get_meme_background("drake", "A happy programmer celebrating clean code", use_gemini=False)
    print(f"Background loaded successfully. AI generated: {is_ai}, size: {img.size}")
