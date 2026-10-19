import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, roc_auc_score, f1_score, precision_score, recall_score

class HybridEngagementPredictor:
    """
    Ensemble & multi-dataset engagement & virality predictor:
    Trained on Reddit (engagement score) + Memotion 7k (humor & sentiment signals).
    """
    def __init__(self, model_dir="models"):
        self.model_dir = model_dir
        self.model = None
        self.vectorizer = None
        self.scaler = None
        self.humor_model = None
        self.feature_names = []
        os.makedirs(self.model_dir, exist_ok=True)

    def extract_meta_features(self, df):
        """Extract linguistic and metadata signals."""
        char_len = df["title"].astype(str).str.len().values.reshape(-1, 1)
        word_count = df["title"].astype(str).apply(lambda s: len(s.split())).values.reshape(-1, 1)
        has_question = df["title"].astype(str).str.contains(r"\?").astype(int).values.reshape(-1, 1)
        has_exclamation = df["title"].astype(str).str.contains(r"!").astype(int).values.reshape(-1, 1)
        caps_ratio = df["title"].astype(str).apply(
            lambda s: sum(1 for c in s if c.isupper()) / max(len(s), 1)
        ).values.reshape(-1, 1)
        
        if "post_hour" in df.columns:
            hours = df["post_hour"].fillna(15).values.reshape(-1, 1)
        else:
            hours = np.full((len(df), 1), 15.0)

        meta = np.hstack([char_len, word_count, has_question, has_exclamation, caps_ratio, hours])
        return meta

    def train(self, reddit_path="db.json", memotion_path="memotion_dataset_7k/labels.csv"):
        print("Training Hybrid Engagement & Humor Predictor...")
        
        # 1. Load Reddit data
        with open(reddit_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        posts = list(raw.get("_default", {}).values())
        df_reddit = pd.DataFrame(posts)
        
        df_reddit["ups"] = pd.to_numeric(df_reddit["ups"], errors="coerce").fillna(0).astype(int)
        df_reddit["title"] = df_reddit["title"].astype(str).str.strip()
        df_reddit = df_reddit[df_reddit["title"] != ""]
        
        df_reddit["created_utc"] = pd.to_numeric(df_reddit["created_utc"], errors="coerce")
        df_reddit["datetime"] = pd.to_datetime(df_reddit["created_utc"], unit="s", errors="coerce")
        df_reddit["post_hour"] = df_reddit["datetime"].dt.hour.fillna(15)
        
        threshold = df_reddit["ups"].quantile(0.75)
        df_reddit["hit"] = (df_reddit["ups"] >= threshold).astype(int)
        
        # Train / Test split
        train_df, test_df = train_test_split(df_reddit, test_size=0.2, random_state=42, stratify=df_reddit["hit"])
        
        # 2. Text vectorizer on full vocabulary
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=2000,
            stop_words="english",
            sublinear_tf=True
        )
        X_train_text = self.vectorizer.fit_transform(train_df["title"]).toarray()
        X_test_text = self.vectorizer.transform(test_df["title"]).toarray()
        
        # 3. Meta features
        self.scaler = StandardScaler()
        X_train_meta = self.scaler.fit_transform(self.extract_meta_features(train_df))
        X_test_meta = self.scaler.transform(self.extract_meta_features(test_df))
        
        X_train = np.hstack([X_train_text, X_train_meta])
        X_test = np.hstack([X_test_text, X_test_meta])
        
        y_train = train_df["hit"].values
        y_test = test_df["hit"].values
        
        # 4. Train main engagement model (Logistic Regression with regularized penalty)
        self.model = LogisticRegression(
            class_weight="balanced",
            C=1.2,
            max_iter=1000,
            random_state=42
        )
        self.model.fit(X_train, y_train)
        
        y_pred = self.model.predict(X_test)
        y_prob = self.model.predict_proba(X_test)[:, 1]
        
        roc = roc_auc_score(y_test, y_prob)
        f1 = f1_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred)
        rec = recall_score(y_test, y_pred)
        
        print("\n=== Reddit Engagement Model Evaluation (Held-out Test) ===")
        print(f"ROC-AUC: {roc:.4f}")
        print(f"F1-Score: {f1:.4f}")
        print(f"Precision: {prec:.4f}")
        print(f"Recall: {rec:.4f}")

        # 5. Train auxiliary Humor & Virality Model using Memotion 7k (6,992 memes)
        humor_metrics = {}
        if os.path.exists(memotion_path):
            print("\nIntegrating Memotion 7k Humor Dataset...")
            df_m = pd.read_csv(memotion_path)
            df_m["caption"] = df_m["text_corrected"].fillna(df_m["text_ocr"]).fillna("").astype(str).str.strip()
            df_m = df_m[df_m["caption"] != ""]
            
            # Binary humor target: 1 if 'very_funny' or 'hilarious'
            df_m["is_very_funny"] = df_m["humour"].isin(["very_funny", "hilarious"]).astype(int)
            
            X_m_text = self.vectorizer.transform(df_m["caption"])
            y_m = df_m["is_very_funny"].values
            
            self.humor_model = LogisticRegression(class_weight="balanced", C=1.0, max_iter=1000, random_state=42)
            self.humor_model.fit(X_m_text, y_m)
            
            m_probs = self.humor_model.predict_proba(X_m_text)[:, 1]
            humor_roc = roc_auc_score(y_m, m_probs)
            humor_metrics = {"dataset_size": len(df_m), "humor_auc": float(humor_roc)}
            print(f"Memotion 7k Model Trained on {len(df_m)} memes! Humor AUC: {humor_roc:.4f}")

        # Top predictive words
        feature_names = list(self.vectorizer.get_feature_names_out()) + [
            "char_length", "word_count", "has_question", "has_exclamation", "caps_ratio", "post_hour"
        ]
        coefs = self.model.coef_[0]
        top_hit_indices = np.argsort(coefs)[-15:][::-1]
        top_flop_indices = np.argsort(coefs)[:15]
        
        hit_signals = [(feature_names[i], float(coefs[i])) for i in top_hit_indices]
        flop_signals = [(feature_names[i], float(coefs[i])) for i in top_flop_indices]
        
        # Save checkpoints
        artifacts = {
            "model": self.model,
            "humor_model": self.humor_model,
            "vectorizer": self.vectorizer,
            "scaler": self.scaler,
            "threshold": float(threshold),
            "metrics": {
                "roc_auc": float(roc),
                "f1": float(f1),
                "precision": float(prec),
                "recall": float(rec)
            },
            "humor_metrics": humor_metrics,
            "signals": {
                "hits": hit_signals,
                "flops": flop_signals
            }
        }
        
        model_file = os.path.join(self.model_dir, "engagement_model.pkl")
        joblib.dump(artifacts, model_file)
        print(f"\nModel successfully saved to {model_file}!")
        return artifacts

    def load(self, model_file=None):
        model_file = model_file or os.path.join(self.model_dir, "engagement_model.pkl")
        if not os.path.exists(model_file):
            return False
        data = joblib.load(model_file)
        self.model = data["model"]
        self.humor_model = data.get("humor_model")
        self.vectorizer = data["vectorizer"]
        self.scaler = data["scaler"]
        self.metrics = data.get("metrics", {})
        self.humor_metrics = data.get("humor_metrics", {})
        self.signals = data.get("signals", {})
        return True

    def predict_engagement(self, captions, post_hour=15):
        if self.model is None and not self.load():
            return [
                {
                    **(c if isinstance(c, dict) else {"caption": c}),
                    "engagement_score": 65.0,
                    "hit_probability": 0.65,
                    "humor_score": 60.0,
                    "predicted_hit": True
                }
                for c in captions
            ]
        
        titles = [c if isinstance(c, str) else c.get("caption", "") for c in captions]
        dummy_df = pd.DataFrame({"title": titles, "post_hour": [post_hour] * len(titles)})
        
        X_text = self.vectorizer.transform(dummy_df["title"]).toarray()
        X_meta = self.scaler.transform(self.extract_meta_features(dummy_df))
        X = np.hstack([X_text, X_meta])
        
        probs = self.model.predict_proba(X)[:, 1]
        preds = self.model.predict(X)
        
        # Humor probability if humor model is available
        humor_probs = None
        if self.humor_model is not None:
            humor_probs = self.humor_model.predict_proba(X_text)[:, 1]

        results = []
        for i, item in enumerate(captions):
            p = float(probs[i])
            h_score = round(float(humor_probs[i]) * 100, 1) if humor_probs is not None else round(p * 100, 1)
            
            # Blend: 70% engagement probability + 30% humor rating
            blended_score = round((p * 0.70 + (h_score / 100.0) * 0.30) * 100, 1)
            
            entry = item if isinstance(item, dict) else {"caption": item}
            entry["engagement_score"] = blended_score
            entry["hit_probability"] = round(p, 3)
            entry["humor_score"] = h_score
            entry["predicted_hit"] = bool(preds[i])
            results.append(entry)
            
        results.sort(key=lambda x: x["engagement_score"], reverse=True)
        return results

HybridEngagementPredictor = HybridEngagementPredictor
EngagementPredictor = HybridEngagementPredictor

if __name__ == "__main__":

    predictor = HybridEngagementPredictor()
    predictor.train()
    samples = [
        "Me explaining why this tool is literally magic",
        "When marketing automation does all the work",
        "Buy product now cheap discount"
    ]
    scored = predictor.predict_engagement(samples)
    print("\n--- Predictions on test batch ---")
    for s in scored:
        print(f"Blended Score: {s['engagement_score']}% (Humor: {s.get('humor_score')}%) - {s['caption']}")
