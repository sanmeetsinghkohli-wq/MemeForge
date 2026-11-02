import os
from PIL import Image, ImageDraw, ImageFont

def get_font(size, bold=False):
    candidates = [
        "C:\\Windows\\Fonts\\segoeuib.ttf" if bold else "C:\\Windows\\Fonts\\segoeui.ttf",
        "C:\\Windows\\Fonts\\arialbd.ttf" if bold else "C:\\Windows\\Fonts\\arial.ttf",
        "arial.ttf"
    ]
    for c in candidates:
        if os.path.exists(c):
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                pass
    return ImageFont.load_default()

font_title = get_font(36, bold=True)
font_h2 = get_font(24, bold=True)
font_body = get_font(18, bold=False)
font_bold = get_font(18, bold=True)
font_small = get_font(14, bold=False)
font_badge = get_font(14, bold=True)

def create_studio_screenshot():
    w, h = 1440, 960
    img = Image.new("RGB", (w, h), color=(15, 23, 42)) # Slate 900
    draw = ImageDraw.Draw(img)

    # Sidebar (left)
    draw.rectangle([0, 0, 320, h], fill=(30, 41, 59)) # Slate 800
    draw.rectangle([319, 0, 320, h], fill=(51, 65, 85)) # Border
    
    # Sidebar items
    draw.text((40, 50), "🔥 MemeForge", font=font_h2, fill=(244, 63, 94))
    draw.text((40, 85), "AI Marketing Meme Studio", font=font_small, fill=(148, 163, 184))
    
    nav_items = [
        ("🚀 Meme Generator Studio", True),
        ("📊 Engagement EDA & Insights", False),
        ("🧠 Predictive Model Diagnostics", False),
        ("📑 Project Report & Presentation", False)
    ]
    for i, (nav, active) in enumerate(nav_items):
        ny = 150 + i * 50
        if active:
            draw.rounded_rectangle([25, ny - 6, 295, ny + 34], radius=8, fill=(79, 70, 229))
            draw.text((40, ny), nav, font=font_body, fill=(255, 255, 255))
        else:
            draw.text((40, ny), nav, font=font_body, fill=(148, 163, 184))

    # Gemini API box in sidebar
    draw.line([(25, 400), (295, 400)], fill=(51, 65, 85), width=1)
    draw.text((40, 420), "🤖 Gemini AI Integration", font=font_bold, fill=(241, 245, 249))
    draw.rounded_rectangle([35, 455, 285, 485], radius=6, fill=(16, 185, 129))
    draw.text((50, 462), "🟢 Gemini API Key Connected", font=font_badge, fill=(255, 255, 255))
    draw.text((40, 510), "☑ Enable Gemini Image Generation", font=font_small, fill=(226, 232, 240))

    # Main content area
    draw.text((370, 50), "MemeForge Studio", font=font_title, fill=(255, 255, 255))
    draw.text((370, 95), "Generate viral, on-brand meme marketing campaigns ranked by predictive engagement AI.", font=font_body, fill=(148, 163, 184))

    # Input card
    draw.rounded_rectangle([370, 150, 1380, 280], radius=12, fill=(30, 41, 59))
    draw.text((400, 175), "Product / Service Name: DevFlow AI", font=font_bold, fill=(241, 245, 249))
    draw.text((400, 215), "Marketing Tone: Witty", font=font_bold, fill=(167, 139, 250))
    draw.text((850, 175), "Visual Style: Impact Overlay (Classic)", font=font_body, fill=(203, 213, 225))
    draw.text((850, 215), "Candidates: 8 concepts  |  Top Memes: 3", font=font_body, fill=(203, 213, 225))
    
    # Success badge
    draw.rounded_rectangle([370, 305, 1380, 345], radius=8, fill=(6, 78, 59))
    draw.text((390, 315), "✓ Generated and ranked 8 concepts in 1.8s! Displaying Top 3 Finalists.", font=font_bold, fill=(52, 211, 153))

    # Meme Card Result (Rank #1)
    card_x, card_y = 370, 375
    draw.rounded_rectangle([card_x, card_y, card_x + 480, card_y + 540], radius=16, fill=(30, 41, 59), outline=(79, 70, 229), width=2)
    draw.text((card_x + 20, card_y + 20), "Rank #1", font=font_h2, fill=(255, 255, 255))
    
    # Engagement Metric Pill
    draw.rounded_rectangle([card_x + 300, card_y + 15, card_x + 455, card_y + 55], radius=10, fill=(16, 185, 129))
    draw.text((card_x + 315, card_y + 24), "83.8% HIT", font=font_badge, fill=(255, 255, 255))

    # Paste real meme thumbnail inside card
    if os.path.exists("assets/live_gemini_sample_meme.png"):
        meme = Image.open("assets/live_gemini_sample_meme.png").convert("RGB")
        meme = meme.resize((440, 360))
        img.paste(meme, (card_x + 20, card_y + 70))
        
    draw.text((card_x + 20, card_y + 450), "✨ Gemini AI Generated Image", font=font_badge, fill=(167, 139, 250))
    
    # Download button
    draw.rounded_rectangle([card_x + 20, card_y + 480, card_x + 460, card_y + 520], radius=8, fill=(79, 70, 229))
    draw.text((card_x + 150, card_y + 490), "📥 Download Meme #1", font=font_bold, fill=(255, 255, 255))

    # Leaderboard Preview on Right
    draw.rounded_rectangle([880, card_y, 1380, card_y + 540], radius=16, fill=(30, 41, 59))
    draw.text((910, card_y + 20), "📋 Live Candidates Scorer Leaderboard", font=font_h2, fill=(255, 255, 255))
    
    headers = ["Rank", "Engagement Score", "Hit Status", "Format"]
    draw.text((910, card_y + 80), "Rank 1     83.8%     ✅ Predictive HIT     drake", font=font_body, fill=(52, 211, 153))
    draw.text((910, card_y + 130), "Rank 2     81.3%     ✅ Predictive HIT     distracted_bf", font=font_body, fill=(52, 211, 153))
    draw.text((910, card_y + 180), "Rank 3     77.4%     ✅ Predictive HIT     shut_up_money", font=font_body, fill=(52, 211, 153))
    draw.text((910, card_y + 230), "Rank 4     62.1%     ❌ Standard          two_buttons", font=font_body, fill=(148, 163, 184))
    draw.text((910, card_y + 280), "Rank 5     58.4%     ❌ Standard          expanding_brain", font=font_body, fill=(148, 163, 184))
    draw.text((910, card_y + 330), "Rank 6     49.2%     ❌ Standard          this_is_fine", font=font_body, fill=(148, 163, 184))

    out_path = "assets/screenshot_app_studio.png"
    img.save(out_path)
    print(f"Saved {out_path}")

create_studio_screenshot()
