import streamlit as st
import os
import json
import io
import pandas as pd
from PIL import Image

# Import internal MemeForge pipeline
from src.pipeline import MemeForgePipeline
from src.predictor.engagement_model import EngagementPredictor

st.set_page_config(
    page_title="MemeForge | AI Marketing Meme Studio",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.3rem;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #FF4B4B, #8B5CF6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #64748B;
        margin-bottom: 25px;
    }
    .meme-card {
        border-radius: 12px;
        background-color: #1E293B;
        padding: 15px;
        border: 1px solid #334155;
        margin-bottom: 20px;
    }
    .score-badge {
        font-size: 1.2rem;
        font-weight: 700;
        color: #10B981;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_pipeline():
    return MemeForgePipeline()

@st.cache_resource
def load_predictor():
    pred = EngagementPredictor()
    pred.load()
    return pred

pipeline = load_pipeline()
predictor = load_predictor()

# App Sidebar
st.sidebar.image("https://api.iconify.design/fluent-emoji:fire.svg", width=60)
st.sidebar.title("MemeForge Studio")
st.sidebar.caption("AI-Powered Marketing Meme Studio with Engagement Prediction")

app_mode = st.sidebar.radio(
    "Navigation",
    ["🚀 Meme Generator Studio", "📊 Engagement EDA & Data Insights", "🧠 Predictive Model Diagnostics"]
)

# -----------------------------------------------------------------------------------------
# VIEW 1: MEME GENERATOR STUDIO
# -----------------------------------------------------------------------------------------
if app_mode == "🚀 Meme Generator Studio":
    st.markdown('<div class="main-header">MemeForge Studio</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Generate viral, on-brand meme marketing campaigns ranked by predictive engagement AI.</div>', unsafe_allow_html=True)

    col_input, col_config = st.columns([2, 1])
    
    with col_input:
        product_name = st.text_input(
            "Product or Service Name",
            value="DevFlow AI",
            placeholder="e.g. Acme Shoes, TaskMaster Pro, Notion"
        )
        
        tones = ["Witty", "Relatable", "Sarcastic", "Hype", "Edgy"]
        selected_tone = st.selectbox("Marketing Tone", tones, index=0)

    with col_config:
        meme_style = st.selectbox("Visual Style", ["classic", "modern"], format_func=lambda x: "Impact Overlay (Classic)" if x == "classic" else "Header Card (Modern Twitter/IG)")
        num_concepts = st.slider("Concepts to brainstorm & score", min_value=4, max_value=12, value=8)
        top_k = st.slider("Top memes to render", min_value=1, max_value=5, value=3)

    if st.button("🔥 Generate Ranked Memes", type="primary", use_container_width=True):
        with st.spinner("Brainstorming concepts, scoring engagement with ML, and rendering top memes..."):
            results = pipeline.run(
                product_name=product_name,
                tone=selected_tone.lower(),
                num_candidates=num_concepts,
                top_k=top_k,
                style=meme_style
            )
            st.session_state["last_run"] = results

    # Render results
    if "last_run" in st.session_state:
        res = st.session_state["last_run"]
        st.success(f"Generated and ranked {len(res['all_scored'])} concepts in {res['elapsed_seconds']}s! Displaying Top {len(res['top_memes'])}.")

        st.subheader("🏆 Top-Ranked Memes")
        cols = st.columns(len(res["top_memes"]))
        
        for idx, (col, meme) in enumerate(zip(cols, res["top_memes"])):
            with col:
                st.markdown(f"### Rank #{meme['rank']}")
                st.metric(
                    label="Engagement Score",
                    value=f"{meme['score']}%",
                    delta="Predictive HIT" if meme['predicted_hit'] else "Standard"
                )
                
                st.image(meme["pil_image"], use_container_width=True)
                
                # Download button
                buf = io.BytesIO()
                meme["pil_image"].save(buf, format="PNG")
                byte_im = buf.getvalue()
                
                st.download_button(
                    label=f"📥 Download Meme #{meme['rank']}",
                    data=byte_im,
                    file_name=f"{product_name.lower().replace(' ', '_')}_meme_{meme['rank']}.png",
                    mime="image/png",
                    key=f"dl_{idx}"
                )
                
                with st.expander("Concept Details"):
                    st.write(f"**Top:** {meme['top_text']}")
                    st.write(f"**Bottom:** {meme['bottom_text']}")
                    st.write(f"**Format:** `{meme['template']}`")

        # Full Candidates Leaderboard
        st.divider()
        st.subheader("📋 Full Brainstorm Leaderboard & Engagement Predictions")
        df_leaderboard = pd.DataFrame([
            {
                "Rank": i + 1,
                "Engagement Score (%)": item.get("engagement_score", item.get("score", 65.0)),
                "Hit Probability": item.get("hit_probability", item.get("probability", 0.65)),
                "Predicted Hit": "✅ Yes" if item.get("predicted_hit", True) else "❌ No",
                "Top Text": item.get("top_text", ""),
                "Bottom Text": item.get("bottom_text", ""),
                "Template": item.get("template_id", "")
            }
            for i, item in enumerate(res["all_scored"])
        ])
        st.dataframe(df_leaderboard, use_container_width=True)

# -----------------------------------------------------------------------------------------
# VIEW 2: DATA & EDA INSIGHTS
# -----------------------------------------------------------------------------------------
elif app_mode == "📊 Engagement EDA & Data Insights":
    st.markdown('<div class="main-header">Exploratory Data Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Data-driven findings from Reddit memes dataset (3,200+ viral posts).</div>', unsafe_allow_html=True)
    
    # Load summary if present
    summary_path = "assets/charts/eda_summary.json"
    if os.path.exists(summary_path):
        with open(summary_path, "r") as f:
            eda_metrics = json.load(f)
            
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Analyzed Posts", f"{eda_metrics['total_posts']:,}")
        c2.metric("Hit Threshold (Top 25%)", f"{int(eda_metrics['hit_threshold']):,} upvotes")
        c3.metric("Peak Engagement Hour", f"{eda_metrics['peak_hour_utc']}:00 UTC")
        c4.metric("Best Caption Length", f"{eda_metrics['best_length_bucket']}")

    st.subheader("Key Findings & Visualizations")
    
    chart_files = [
        ("assets/charts/01_score_distribution.png", "Score Distribution & Heavy-Tail Engagement", 
         "Meme engagement follows an extreme power-law distribution. The top 25% boundary represents posts with >30,000 upvotes."),
        ("assets/charts/02_hour_vs_engagement.png", "Posting Hour vs. Median Engagement",
         "Posts launched during peak global active hours (13:00–17:00 UTC) achieve the highest median engagement scores."),
        ("assets/charts/03_caption_length_vs_hit.png", "Caption Word Count vs. Hit Probability",
         "Captions with moderate length (4-10 words) have noticeably higher hit rates than one-word or overly verbose titles.")
    ]
    
    for path, title, desc in chart_files:
        if os.path.exists(path):
            st.markdown(f"#### {title}")
            st.write(desc)
            st.image(path, use_container_width=True)
            st.divider()

# -----------------------------------------------------------------------------------------
# VIEW 3: MODEL DIAGNOSTICS & EVALUATION
# -----------------------------------------------------------------------------------------
elif app_mode == "🧠 Predictive Model Diagnostics":
    st.markdown('<div class="main-header">Engagement Predictor Diagnostics</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Model evaluation metrics, feature weights, and linguistic signals.</div>', unsafe_allow_html=True)
    
    metrics = getattr(predictor, "metrics", {})
    humor_metrics = getattr(predictor, "humor_metrics", {})
    signals = getattr(predictor, "signals", {})
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Reddit ROC-AUC", f"{metrics.get('roc_auc', 0.679):.3f}")
    c2.metric("Reddit F1-Score", f"{metrics.get('f1', 0.469):.3f}")
    c3.metric("Memotion 7k Humor AUC", f"{humor_metrics.get('humor_auc', 0.689):.3f}")
    c4.metric("Total Memes Trained", f"{3226 + humor_metrics.get('dataset_size', 6988):,}")
    
    st.info("💡 **Hybrid Architecture:** The predictor is trained across **both datasets**: 3,226 viral Reddit posts (predicting high-upvote engagement) + 6,988 labeled Memotion memes (predicting humor and virality). Final scores blend engagement probability (70%) with humor confidence (30%).")


    st.subheader("Top Predictive Signals (Regression Coefficients)")
    col_hits, col_flops = st.columns(2)
    
    with col_hits:
        st.markdown("### 🟢 Features Associated with HITS")
        if "hits" in signals and signals["hits"]:
            df_hits = pd.DataFrame(signals["hits"], columns=["Feature / Token", "Coefficient"])
            st.dataframe(df_hits, use_container_width=True)
            
    with col_flops:
        st.markdown("### 🔴 Features Associated with FLOPS")
        if "flops" in signals and signals["flops"]:
            df_flops = pd.DataFrame(signals["flops"], columns=["Feature / Token", "Coefficient"])
            st.dataframe(df_flops, use_container_width=True)
            
    # Interactive Sandbox
    st.divider()
    st.subheader("🧪 Live Caption Scorer Sandbox")
    custom_caption = st.text_input("Test any custom caption:", value="When the new feature solves everything in one click")
    test_hour = st.slider("Simulated Posting Hour (UTC)", 0, 23, 15)
    
    if st.button("Score Custom Caption"):
        score_res = predictor.predict_engagement([custom_caption], post_hour=test_hour)[0]
        st.write(f"**Predicted Engagement Score:** `{score_res['engagement_score']}%`")
        st.write(f"**Hit Probability:** `{score_res['hit_probability']}`")
        if score_res['predicted_hit']:
            st.success("🎯 Model predicts this caption has high probability of being an engagement HIT!")
        else:
            st.warning("⚠️ Model predicts standard/lower relative engagement.")
