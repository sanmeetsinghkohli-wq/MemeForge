import os
import time
from src.generator.concept_generator import ConceptGenerator
from src.predictor.engagement_model import EngagementPredictor
from src.generator.image_service import get_template_image
from src.overlay.meme_renderer import create_meme

class MemeForgePipeline:
    def __init__(self):
        self.concept_gen = ConceptGenerator()
        self.predictor = EngagementPredictor()
        self.predictor.load()

    def run(self, product_name: str, tone: str = "witty", num_candidates: int = 8, top_k: int = 3, style: str = "classic"):
        """
        End-to-End Pipeline:
        1. Generate N meme concepts (captions + prompts)
        2. Score & Rank all captions with the Engagement Predictor
        3. Filter Top-K highest engagement memes
        4. Render final memes with PIL text overlay
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
            bg_img = get_template_image(t_id)
            
            output_filename = f"assets/generated/meme_rank{rank}_{int(time.time())}.png"
            final_img = create_meme(
                image_input=bg_img,
                top_text=item.get("top_text", ""),
                bottom_text=item.get("bottom_text", ""),
                output_path=output_filename,
                style=style
            )
            
            rendered_results.append({
                "rank": rank,
                "score": item["engagement_score"],
                "hit_prob": item["hit_probability"],
                "predicted_hit": item["predicted_hit"],
                "top_text": item["top_text"],
                "bottom_text": item["bottom_text"],
                "template": t_id,
                "image_path": output_filename,
                "pil_image": final_img
            })
            
        elapsed = round(time.time() - start_time, 2)
        return {
            "all_scored": scored_concepts,
            "top_memes": rendered_results,
            "elapsed_seconds": elapsed
        }

if __name__ == "__main__":
    pipeline = MemeForgePipeline()
    res = pipeline.run("MemeForge AI", tone="witty", num_candidates=6, top_k=3)
    print(f"Pipeline executed in {res['elapsed_seconds']}s")
    for m in res["top_memes"]:
        print(f"Rank {m['rank']} (Score: {m['score']}%): {m['top_text']} | {m['bottom_text']}")
