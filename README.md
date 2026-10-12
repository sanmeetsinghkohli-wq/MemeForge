# MemeForge: An AI Marketing Meme Studio
### Analysis, Prediction, and Generation

MemeForge is an end-to-end system that produces data-driven, engagement-ranked marketing memes tailored to a specified product and tone.

---

## 🏗️ Architecture

```
User Input (Product + Tone)
        │
        ▼
[Concept Generator] ──> N candidate concepts (Captions + Image Prompts)
        │
        ▼
[Engagement Predictor] (TF-IDF + Metadata Features Classifier)
        │
        ▼
[Ranking & Filtering] ──> Select Top K Highest Engagement Concepts
        │
        ▼
[Meme Overlay Engine] (PIL Dynamic Typography & Template Alignment)
        │
        ▼
[Streamlit Gallery] ──> Ranked Display, Diagnostics, & Downloads
```

---

## 🚀 Quickstart

### 1. Requirements & Dependencies
Ensure your Python environment is set up:
```bash
pip install -r requirements.txt
```

### 2. Run Exploratory Data Analysis & Generate Visualizations
To recalculate metrics and generate charts from `db.json`:
```bash
python src/analysis/run_eda.py
```

### 3. Train / Retrain Engagement Predictor
```bash
python src/predictor/engagement_model.py
```
This trains a TF-IDF + metadata feature Logistic Regression classifier on the top-25% hit threshold and outputs model metrics (`ROC-AUC`, `F1`, `Precision`, `Recall`) to `models/engagement_model.pkl`.

### 4. Launch the Streamlit Web Application
```bash
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 📊 Modules Overview

- **`src/analysis/`**:
  - `data_loader.py`: Cleans raw Reddit posts (`db.json`) and loads `memotion_dataset_7k`.
  - `run_eda.py`: Computes engagement statistics across posting hours and caption lengths.
- **`src/predictor/`**:
  - `engagement_model.py`: Feature extraction and binary classifier predicting hit probability.
- **`src/generator/`**:
  - `concept_generator.py`: Generates top/bottom caption pairs and diffusion-ready image prompts.
  - `image_service.py`: Background template and image asset manager.
- **`src/overlay/`**:
  - `meme_renderer.py`: PIL-based text renderer with outline, drop-shadow, and modern header options.
- **`src/pipeline.py`**:
  - End-to-end orchestrator connecting generator, scorer, and renderer.
- **`app.py`**:
  - Multi-tab interactive Streamlit dashboard.
