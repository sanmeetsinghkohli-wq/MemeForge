import os
import json
import random

DEFAULT_TEMPLATES = [
    {
        "template_id": "drake",
        "description": "Drake Hotline Bling reaction: disapproving top, approving bottom",
        "prompt_vibe": "Drake looking away with disgust in top panel, then pointing and approving in bottom panel",
        "default_top": "Paying $500 for traditional marketing",
        "default_bottom": "Using AI memes that go viral for free",
        "keywords": ["choice", "preference", "better", "upgrade", "reject", "approve"]
    },
    {
        "template_id": "distracted_bf",
        "description": "Distracted Boyfriend looking at another woman while his girlfriend is upset",
        "prompt_vibe": "A man looking back at another attractive woman while walking with his annoyed girlfriend",
        "default_top": "My boss expecting a serious ad campaign",
        "default_bottom": "Me posting relatable memes on the company account",
        "keywords": ["temptation", "distraction", "switch", "alternative", "new shiny thing"]
    },
    {
        "template_id": "two_buttons",
        "description": "Sweating guy choosing between two contradictory buttons",
        "prompt_vibe": "A cartoon man intensely sweating with a towel, hesitating over two red buttons",
        "default_top": "Write a 5-page marketing brief",
        "default_bottom": "Generate a MemeForge meme in 2 seconds",
        "keywords": ["dilemma", "hard choice", "indecision", "pressure", "confusion"]
    },
    {
        "template_id": "expanding_brain",
        "description": "Galaxy / expanding brain showing increasingly clever tiers of thinking",
        "prompt_vibe": "Multi-tier meme showing small brain to hyper-glowing enlightened cosmic brain",
        "default_top": "Using cold emails",
        "default_bottom": "Meme marketing your product directly into their feed",
        "keywords": ["evolution", "galaxy brain", "smart", "levels", "intelligence"]
    },
    {
        "template_id": "change_my_mind",
        "description": "Steven Crowder sitting at outdoor table with sign 'Change My Mind'",
        "prompt_vibe": "Man sitting behind a table with a coffee mug and banner in a college park",
        "default_top": "Memes drive higher ROI than billboard ads",
        "default_bottom": "Change my mind.",
        "keywords": ["unpopular opinion", "fact", "truth", "debate", "statement"]
    },
    {
        "template_id": "this_is_fine",
        "description": "Dog in room engulfed in flames sipping coffee saying 'This is fine'",
        "prompt_vibe": "Cartoon dog with hat sipping coffee sitting calmly in a room completely on fire",
        "default_top": "When your ad spend is burning through budget",
        "default_bottom": "This is totally fine.",
        "keywords": ["chaos", "disaster", "stress", "calm", "crisis", "startup"]
    },
    {
        "template_id": "woman_yelling_cat",
        "description": "Woman screaming and pointing finger, confused white cat sitting at dinner table",
        "prompt_vibe": "Angry woman screaming and pointing at a confused white cat at a restaurant table",
        "default_top": "Marketers explaining complex funnel strategies",
        "default_bottom": "Customers just wanting a good meme",
        "keywords": ["misunderstanding", "conflict", "overcomplicating", "argument"]
    },
    {
        "template_id": "shut_up_money",
        "description": "Fry from Futurama squinting aggressively holding up wads of cash",
        "prompt_vibe": "Animated character aggressively waving cash shouting take my money",
        "default_top": "When a tool solves the exact problem you had all week",
        "default_bottom": "Shut up and take my money!",
        "keywords": ["purchase", "buy", "deal", "must have", "take my money", "instant buy"]
    }
]

class ConceptGenerator:
    """Generates meme concepts with rule-based humor templates or an LLM API."""
    def __init__(self, api_key=None, provider="heuristic"):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("OPENAI_API_KEY")
        self.provider = provider

    def generate_concepts(self, product_name: str, tone: str = "witty", num_concepts: int = 8):
        """
        Produces N meme concept candidate dictionaries:
        [{'top_text': ..., 'bottom_text': ..., 'caption': ..., 'image_prompt': ..., 'template': ...}]
        """
        concepts = []
        templates_pool = list(DEFAULT_TEMPLATES)
        random.shuffle(templates_pool)

        # Tone modifiers
        tone_flavors = {
            "witty": ("Clever, subtle punchline", "clean humor"),
            "sarcastic": ("Ironic, dry tone", "poking fun at the status quo"),
            "relatable": ("Everyday struggle", "shared marketer/user pain point"),
            "hype": ("Exaggerated excitement", "game-changing energy"),
            "edgy": ("Self-deprecating, raw honesty", "unfiltered reality")
        }
        
        flavor_desc, humor_type = tone_flavors.get(tone.lower(), ("Relatable humor", "fun"))

        for i, tmpl in enumerate(templates_pool[:num_concepts]):
            # Craft tailored caption variations for product & tone
            t_id = tmpl["template_id"]
            if t_id == "drake":
                top = f"Doing manual work without {product_name}"
                bottom = f"Letting {product_name} do it all in 10 seconds"
            elif t_id == "distracted_bf":
                top = f"Traditional tools I've used for years"
                bottom = f"Me finding {product_name} today"
            elif t_id == "two_buttons":
                top = f"Spend hours troubleshooting"
                bottom = f"Just switch to {product_name}"
            elif t_id == "expanding_brain":
                top = f"Ignoring the problem"
                bottom = f"Upgrading directly to {product_name}"
            elif t_id == "change_my_mind":
                top = f"{product_name} is the best thing that happened this year"
                bottom = "Change my mind."
            elif t_id == "this_is_fine":
                top = f"Trying to survive another week without {product_name}"
                bottom = "Everything is totally fine."
            elif t_id == "woman_yelling_cat":
                top = f"My manager asking why everything got finished so fast"
                bottom = f"Me having {product_name} open in another tab"
            elif t_id == "shut_up_money":
                top = f"First 5 minutes using {product_name}"
                bottom = "Shut up and take my money!"
            else:
                top = f"Before {product_name}"
                bottom = f"After {product_name}"

            full_caption = f"{top} {bottom}".strip()
            image_prompt = f"Meme aesthetic: {tmpl['prompt_vibe']}, vibrant colors, digital art style, centered subject"

            concepts.append({
                "concept_id": f"c_{i+1}",
                "product": product_name,
                "tone": tone,
                "template_id": t_id,
                "top_text": top,
                "bottom_text": bottom,
                "caption": full_caption,
                "image_prompt": image_prompt,
                "template_description": tmpl["description"]
            })

        return concepts

if __name__ == "__main__":
    gen = ConceptGenerator()
    results = gen.generate_concepts("TaskMaster Pro", tone="sarcastic", num_concepts=3)
    print(f"Generated {len(results)} sample concepts:")
    for r in results:
        print(f"- [{r['template_id']}] Top: {r['top_text']} | Bottom: {r['bottom_text']}")
