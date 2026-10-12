import os
import json
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Set visual aesthetic
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
os.makedirs("assets/charts", exist_ok=True)

def run_eda(filepath="db.json"):
    print("Loading Reddit meme dataset...")
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    posts = list(data.get("_default", {}).values())
    df = pd.DataFrame(posts)
    
    df["ups"] = pd.to_numeric(df["ups"], errors="coerce").fillna(0).astype(int)
    df["title"] = df["title"].astype(str)
    df["created_utc"] = pd.to_numeric(df["created_utc"], errors="coerce")
    df["datetime"] = pd.to_datetime(df["created_utc"], unit="s", errors="coerce")
    df["post_hour"] = df["datetime"].dt.hour
    df["post_day"] = df["datetime"].dt.day_name()
    
    # Text length & word counts
    df["char_len"] = df["title"].str.len()
    df["word_count"] = df["title"].apply(lambda x: len(x.split()))
    
    # 75th percentile engagement label
    thresh = df["ups"].quantile(0.75)
    df["hit"] = (df["ups"] >= thresh).astype(int)
    
    print(f"Total posts: {len(df)}")
    print(f"Upvotes min: {df['ups'].min()}, median: {df['ups'].median()}, 75th percentile: {thresh}, max: {df['ups'].max()}")
    
    # 1. Score distribution plot
    plt.figure(figsize=(10, 5))
    sns.histplot(df["ups"], bins=50, kde=True, color="#4F46E5")
    plt.axvline(thresh, color="red", linestyle="--", label=f"Hit Threshold (Top 25% = {int(thresh):,} upvotes)")
    plt.title("Distribution of Reddit Meme Scores (Upvotes)", fontsize=14, fontweight="bold")
    plt.xlabel("Upvotes", fontsize=12)
    plt.ylabel("Post Count", fontsize=12)
    plt.legend()
    plt.tight_layout()
    plt.savefig("assets/charts/01_score_distribution.png", dpi=200)
    plt.close()
    
    # 2. Posting Hour vs Engagement
    hour_stats = df.groupby("post_hour")["ups"].agg(["median", "mean", "count"]).reset_index()
    plt.figure(figsize=(11, 5))
    sns.barplot(data=hour_stats, x="post_hour", y="median", palette="crest")
    plt.title("Median Meme Engagement by Posting Hour (UTC)", fontsize=14, fontweight="bold")
    plt.xlabel("Hour of Day (UTC)", fontsize=12)
    plt.ylabel("Median Upvotes", fontsize=12)
    plt.tight_layout()
    plt.savefig("assets/charts/02_hour_vs_engagement.png", dpi=200)
    plt.close()

    # 3. Caption Length vs Hit Probability
    df["word_bin"] = pd.cut(df["word_count"], bins=[0, 3, 6, 10, 20, 100], labels=["1-3 words", "4-6 words", "7-10 words", "11-20 words", "20+ words"])
    hit_by_len = df.groupby("word_bin", observed=False)["hit"].mean().reset_index()
    
    plt.figure(figsize=(9, 5))
    bars = sns.barplot(data=hit_by_len, x="word_bin", y="hit", palette="magma")
    plt.axhline(0.25, color="gray", linestyle=":", label="Average baseline (25%)")
    plt.title("Hit Rate by Caption Length", fontsize=14, fontweight="bold")
    plt.xlabel("Caption Word Count", fontsize=12)
    plt.ylabel("Probability of Becoming a Hit (Top 25%)", fontsize=12)
    plt.ylim(0, max(0.4, hit_by_len["hit"].max() + 0.05))
    plt.legend()
    plt.tight_layout()
    plt.savefig("assets/charts/03_caption_length_vs_hit.png", dpi=200)
    plt.close()
    
    # Summary metrics JSON for the Streamlit dashboard
    summary = {
        "total_posts": int(len(df)),
        "median_score": float(df["ups"].median()),
        "hit_threshold": float(thresh),
        "peak_hour_utc": int(hour_stats.sort_values(by="median", ascending=False).iloc[0]["post_hour"]),
        "best_length_bucket": str(hit_by_len.sort_values(by="hit", ascending=False).iloc[0]["word_bin"]),
        "hit_rate_best_bucket": float(hit_by_len.sort_values(by="hit", ascending=False).iloc[0]["hit"])
    }
    
    with open("assets/charts/eda_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
        
    print("EDA Complete! Generated charts in assets/charts/ and summary JSON saved.")
    return summary

if __name__ == "__main__":
    run_eda()
