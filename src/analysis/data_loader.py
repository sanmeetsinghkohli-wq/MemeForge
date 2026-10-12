import os
import json
import numpy as np
import pandas as pd
from datetime import datetime

def load_reddit_data(filepath="db.json"):
    """Load and parse Reddit posts from db.json."""
    with open(filepath, "r", encoding="utf-8") as f:
        raw = json.load(f)
    
    posts = list(raw.get("_default", {}).values())
    df = pd.DataFrame(posts)
    
    # Clean and parse columns
    df = df.dropna(subset=["title", "ups"])
    df = df[df["title"].astype(str).str.strip() != ""]
    df["title"] = df["title"].astype(str)
    df["ups"] = pd.to_numeric(df["ups"], errors="coerce").fillna(0).astype(int)
    
    # Parse timestamp
    df["created_utc"] = pd.to_numeric(df["created_utc"], errors="coerce")
    df["datetime"] = pd.to_datetime(df["created_utc"], unit="s", errors="coerce")
    df["post_hour"] = df["datetime"].dt.hour.fillna(12).astype(int)
    df["post_dayofweek"] = df["datetime"].dt.dayofweek.fillna(0).astype(int)
    df["is_weekend"] = df["post_dayofweek"].isin([5, 6]).astype(int)
    
    # Feature engineering for titles
    df["title_char_length"] = df["title"].str.len()
    df["title_word_count"] = df["title"].apply(lambda t: len(t.split()))
    df["has_question"] = df["title"].str.contains(r"\?").astype(int)
    df["has_exclamation"] = df["title"].str.contains(r"!").astype(int)
    df["all_caps_ratio"] = df["title"].apply(
        lambda t: sum(1 for c in t if c.isupper()) / max(len(t), 1)
    )
    
    # Hit definition: Top 25% of scores
    threshold = df["ups"].quantile(0.75)
    df["is_hit"] = (df["ups"] >= threshold).astype(int)
    
    return df, threshold

def load_memotion_data(filepath="memotion_dataset_7k/labels.csv"):
    """Load Memotion dataset if available."""
    if not os.path.exists(filepath):
        return None
    try:
        df = pd.read_csv(filepath)
        df["caption"] = df["text_corrected"].fillna(df["text_ocr"]).fillna("").astype(str)
        return df
    except Exception as e:
        print(f"Warning loading memotion: {e}")
        return None

if __name__ == "__main__":
    df, thresh = load_reddit_data()
    print(f"Loaded {len(df)} Reddit posts. Hit threshold (top 25%): {thresh:.0f} upvotes")
    print(f"Hit balance: {df['is_hit'].value_counts().to_dict()}")
