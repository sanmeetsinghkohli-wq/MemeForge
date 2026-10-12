import os
import textwrap
from PIL import Image, ImageDraw, ImageFont

def get_font(font_size=40):
    """Try to load Impact, Arial, or fallback to default."""
    candidates = [
        "impact.ttf",
        "Impact.ttf",
        "C:\\Windows\\Fonts\\impact.ttf",
        "C:\\Windows\\Fonts\\arialbd.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
        "arial.ttf",
    ]
    for font_path in candidates:
        try:
            return ImageFont.truetype(font_path, font_size)
        except Exception:
            continue
    return ImageFont.load_default()

def draw_text_with_outline(draw, text, position, font, text_color="white", outline_color="black", outline_width=3):
    """Draw text with a strong meme-style stroke/outline."""
    x, y = position
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), text, font=font, fill=outline_color)
    draw.text((x, y), text, font=font, fill=text_color)

def create_meme(
    image_input,
    top_text="",
    bottom_text="",
    output_path=None,
    style="classic", # 'classic' (impact top/bottom), 'modern' (white top header)
    font_size=48
):
    """
    Renders meme text over an image.
    image_input: Image path or PIL.Image object.
    """
    if isinstance(image_input, str):
        img = Image.open(image_input).convert("RGBA")
    else:
        img = image_input.convert("RGBA")
        
    width, height = img.size
    
    if style == "modern":
        # Twitter/Instagram meme style: clean white header card on top
        font = get_font(max(24, int(width / 24)))
        wrapped_text = "\n".join(textwrap.wrap(top_text or bottom_text, width=max(20, int(width / 22))))
        
        # Calculate text bounding box
        dummy_img = Image.new("RGBA", (1, 1))
        dummy_draw = ImageDraw.Draw(dummy_img)
        bbox = dummy_draw.textbbox((0, 0), wrapped_text, font=font)
        text_height = bbox[3] - bbox[1] + 40
        
        # New canvas with header
        canvas = Image.new("RGBA", (width, height + text_height), (255, 255, 255, 255))
        draw = ImageDraw.Draw(canvas)
        draw.text((25, 20), wrapped_text, fill=(20, 20, 20, 255), font=font)
        canvas.paste(img, (0, text_height))
        result = canvas.convert("RGB")
    else:
        # Classic Impact meme style (all-caps with thick black border)
        result = img.convert("RGB")
        draw = ImageDraw.Draw(result)
        
        dynamic_size = max(28, int(width / 16))
        font = get_font(dynamic_size)
        
        def render_block(text, y_pos_anchor):
            if not text:
                return
            text = text.upper()
            wrapped_lines = textwrap.wrap(text, width=max(14, int(width / (dynamic_size * 0.65))))
            
            line_heights = []
            line_widths = []
            for line in wrapped_lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                line_widths.append(bbox[2] - bbox[0])
                line_heights.append(bbox[3] - bbox[1] + 8)
                
            total_h = sum(line_heights)
            
            if y_pos_anchor == "top":
                curr_y = 20
            else: # bottom
                curr_y = height - total_h - 25
                
            for line, lw, lh in zip(wrapped_lines, line_widths, line_heights):
                x = (width - lw) // 2
                draw_text_with_outline(draw, line, (x, curr_y), font, outline_width=max(2, int(dynamic_size / 14)))
                curr_y += lh

        render_block(top_text, "top")
        render_block(bottom_text, "bottom")

    if output_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        result.save(output_path, quality=95)
        
    return result

if __name__ == "__main__":
    test_img = Image.new("RGB", (600, 600), color=(73, 109, 137))
    out = create_meme(test_img, top_text="WHEN THE CODE FINALLY COMPILES", bottom_text="ON THE FIRST TRY", output_path="assets/sample_test.png")
    print("Meme overlay test generated successfully at assets/sample_test.png")
