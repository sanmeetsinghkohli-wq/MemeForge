import os
import time
from src.generator.concept_generator import ConceptGenerator
from src.predictor.engagement_model import EngagementPredictor
from src.generator.image_service import get_meme_background, get_template_image
from src.overlay.meme_renderer import create_meme

class MemeForgePipeline:
    def __init__(self):
        self.concept_gen = ConceptGenerator()
        self.predictor = EngagementPredictor()
        self.predictor.load()

    def run(
        self,
        product_name: str,
        tone: str = "witty",
        num_candidates: int = 8,
        top_k: int = 3,
        style: str = "classic",
        use_gemini_image: bool = True,
        gemini_api_key: str = None
    ):
        """
        End-to-End Pipeline:
        1. Generate N meme concepts (captions + prompts)
        2. Score & Rank all captions with the Engagement Predictor
        3. Filter Top-K highest engagement memes
        4. Render final memes with PIL text overlay (optionally AI generated background)
        """
        start_time = time.time()
        
        # Step 1: LLM/Heuristic concept generation
        concepts = self.concept_gen.generate_concepts(
            product_name=product_name,
            tone=tone,
            num_concepts=num_candidates
        )
        
        # Step 2: Predictive ranking
        scored_concepts = self.predictor.predict_engagement(concepts)
        
        # Step 3: Top K selection
        top_memes = scored_concepts[:top_k]
        
        # Step 4: Render final images
        rendered_results = []
        os.makedirs("assets/generated", exist_ok=True)
        
        for rank, item in enumerate(top_memes, 1):
            t_id = item.get("template_id", "drake")
            prompt = item.get("image_prompt", f"{product_name} funny marketing meme background")
            
            # Fetch background (via Gemini Image API or curated template fallback)
            bg_img, was_ai = get_meme_background(
                template_id=t_id,
                prompt=prompt,
                use_gemini=use_gemini_image,
                api_key=gemini_api_key
            )
            
            output_filename = f"assets/generated/meme_rank{rank}_{int(time.time())}.png"
            final_img = create_meme(
                image_input=bg_img,
                top_text=item.get("top_text", ""),
                bottom_text=item.get("bottom_text", ""),
                output_path=output_filename,
                style=style
            )
            
            score = item.get("engagement_score", item.get("score", 65.0))
            hit_prob = item.get("hit_probability", item.get("probability", 0.65))
            pred_hit = item.get("predicted_hit", True)
            
            rendered_results.append({
                "rank": rank,
                "score": score,
                "hit_prob": hit_prob,
                "predicted_hit": pred_hit,
                "top_text": item.get("top_text", ""),
                "bottom_text": item.get("bottom_text", ""),
                "template": t_id,
                "image_path": output_filename,
                "pil_image": final_img,
                "is_ai_generated": was_ai,
                "image_prompt": prompt
            })
            
        elapsed = round(time.time() - start_time, 2)
        return {
            "all_scored": scored_concepts,
            "top_memes": rendered_results,
            "elapsed_seconds": elapsed
        }

if __name__ == "__main__":
    pipeline = MemeForgePipeline()
    res = pipeline.run("MemeForge AI", tone="witty", num_candidates=6, top_k=3, use_gemini_image=False)
    print(f"Pipeline executed in {res['elapsed_seconds']}s")
    for m in res["top_memes"]:
        print(f"Rank {m['rank']} (Score: {m['score']}%, AI BG: {m['is_ai_generated']}): {m['top_text']} | {m['bottom_text']}")
