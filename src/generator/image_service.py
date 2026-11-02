import os
import glob
import random
import io
import base64
import requests
from PIL import Image, ImageDraw, ImageFont

TEMPLATES_DIR = "assets/templates"
AI_CACHE_DIR = "assets/ai_generated_cache"
os.makedirs(TEMPLATES_DIR, exist_ok=True)
os.makedirs(AI_CACHE_DIR, exist_ok=True)

DEFAULT_GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")

def generate_default_templates():
    """Generates vibrant, clean meme background canvas templates if none exist."""
    palettes = {
        "drake": ((245, 158, 11), (251, 191, 36)),
        "distracted_bf": ((59, 130, 246), (96, 165, 250)),
        "two_buttons": ((239, 68, 68), (248, 113, 113)),
        "expanding_brain": ((147, 51, 234), (192, 132, 252)),
        "change_my_mind": ((16, 185, 129), (52, 211, 153)),
        "this_is_fine": ((249, 115, 22), (251, 146, 60)),
        "woman_yelling_cat": ((236, 72, 153), (244, 114, 182)),
        "shut_up_money": ((34, 197, 94), (74, 222, 128)),
        "superhero_choice": ((37, 99, 235), (96, 165, 250)),
        "mind_blown": ((217, 70, 239), (244, 114, 182)),
        "giga_chad": ((234, 179, 8), (250, 204, 21)),
        "sleep_peacefully": ((99, 102, 241), (129, 140, 248))
    }
    
    for name, (c1, c2) in palettes.items():
        filepath = os.path.join(TEMPLATES_DIR, f"{name}.png")
        if not os.path.exists(filepath):
            img = Image.new("RGB", (700, 700), color=c1)
            draw = ImageDraw.Draw(img)
            draw.rectangle([20, 20, 680, 680], outline=(255, 255, 255, 180), width=4)
            draw.rectangle([100, 100, 600, 600], outline=c2, width=2)
            img.save(filepath)

def generate_gemini_image(prompt: str, api_key: str = None, timeout: int = 12):
    """
    Attempts to generate an image via Google Gemini / Imagen multimodal API.
    Returns: PIL Image if successful, None if rate-limited (HTTP 429) or error.
    """
    key = api_key or DEFAULT_GEMINI_KEY
    if not key:
        return None

    models = [
        "gemini-2.5-flash-image",
        "gemini-3.1-flash-lite-image",
        "gemini-3.1-flash-image"
    ]

    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"Generate a high quality visual background for a meme without any text: {prompt}"
                }]
            }],
            "generationConfig": {
                "responseModalities": ["IMAGE"]
            }
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
                # Quota exceeded on free tier; fall through
                continue
        except Exception:
            continue

    return None

def generate_neural_diffusion_image(prompt: str, timeout: int = 15):
    """
    Fast, reliable AI image generation fallback:
    Creates vibrant, photorealistic 650x650 meme artwork directly from the visual prompt.
    """
    try:
        clean_prompt = prompt.replace("\n", " ").strip()
        encoded = requests.utils.quote(clean_prompt[:300])
        seed = random.randint(1000, 999999)
        url = f"https://image.pollinations.ai/prompt/{encoded}?width=650&height=650&nologo=true&private=true&seed={seed}"
        
        res = requests.get(url, timeout=timeout)
        if res.status_code == 200 and len(res.content) > 10000:
            img = Image.open(io.BytesIO(res.content)).convert("RGB")
            # Automatically crop any subtle bottom branding strip so the meme background is 100% clean
            w, h = img.size
            clean_bg = img.crop((0, 0, w, h - 35)).resize((w, h), Image.Resampling.LANCZOS)
            return clean_bg
    except Exception as e:
        pass
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
    Unified AI Visual Engine:
    1. If use_gemini is True, first attempts Google Gemini Multimodal Image Generation.
    2. If Gemini API is rate-limited (429 free tier), automatically uses Neural AI Diffusion.
    3. If offline, falls back gracefully to curated meme templates.
    Returns: (PIL.Image, is_ai_generated: bool)
    """
    if use_gemini and prompt:
        # 1. Try Google Gemini Image API
        ai_img = generate_gemini_image(prompt, api_key=api_key)
        if ai_img is not None:
            return ai_img, True

        # 2. Seamless Neural AI Diffusion Engine
        diff_img = generate_neural_diffusion_image(prompt)
        if diff_img is not None:
            return diff_img, True

    # 3. Curated template fallback
    return get_template_image(template_id), False

if __name__ == "__main__":
    generate_default_templates()
    img, is_ai = get_meme_background("drake", "funny enthusiastic robot holding coffee mug celebrating success", use_gemini=True)
    print(f"Background generated! AI Image: {is_ai}, dimensions: {img.size}")
