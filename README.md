# AgriBot — AI Agricultural Consultation Platform

> Commissioned NLP chatbot for plant disease diagnosis — built for Indonesian farmers.

[![Live](https://img.shields.io/badge/Status-Live%20in%20Production-brightgreen?style=flat-square)](https://agribot-tani.site)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![PHP](https://img.shields.io/badge/PHP-8.x-777BB4?style=flat-square&logo=php&logoColor=white)](https://php.net)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000?style=flat-square&logo=flask)](https://flask.palletsprojects.com)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?style=flat-square&logo=mysql&logoColor=white)](https://mysql.com)

**🌐 Live demo: [agribot-tani.site](https://agribot-tani.site)**

---

## Overview

AgriBot is a production-grade NLP chatbot commissioned by a client in the agricultural sector. It helps Indonesian farmers identify plant diseases and pests by describing symptoms in natural language — including local dialect and farming slang.

The core challenge: Indonesian farmers don't describe symptoms in textbook language. They say *"oyot cabe benyek"* (cassava roots gone mushy) or *"brambang krowok dimakanin ulet"* (shallots with holes eaten by worms). AgriBot handles this through a 5-layer NLP pipeline that normalizes dialect before matching against a curated knowledge base — with automatic fallback to Gemini API for out-of-KB queries.

**Evaluation results:** 91.52% weighted F1-score on 30 out-of-sample farmer dialect/slang queries across 6 disease classes.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              Browser — PHP Frontend (konsultasi.php)        │
│         Chat UI · Marked.js rendering · Fetch API          │
└────────────────────────┬────────────────────────────────────┘
                         │ POST /api/chat
┌────────────────────────▼────────────────────────────────────┐
│              Python Flask API (backend_python/app.py)       │
│                                                             │
│  Layer 1: Slang Normalization (40+ farmer dialect words)    │
│  Layer 2: KB Enrichment (synonym injection per disease)     │
│  Layer 3: TF-IDF Bigram Vectorization                       │
│  Layer 4: Cosine Similarity Retrieval                       │
│  Layer 5: Commodity Boost / Penalty Scoring                 │
│                                                             │
│  if score ≥ 0.20 → Local TF-IDF answer                     │
│  if score < 0.20 → Gemini API fallback                      │
└──────────┬──────────────────────────┬───────────────────────┘
           │                          │
┌──────────▼──────────┐   ┌──────────▼──────────────────────┐
│  MySQL Database     │   │  Gemini API (gemini-2.5-flash)  │
│  knowledge_base     │   │  Edge case fallback             │
│  (penyakit, gejala, │   └─────────────────────────────────┘
│   solusi)           │
└─────────────────────┘
           │
┌──────────▼──────────────────────────────────────────────────┐
│  Admin Panel (admin.php)                                    │
│  Knowledge base CRUD · CSV batch import · Live search      │
│  Model metrics dashboard (F1: 91.52%, records count)       │
└─────────────────────────────────────────────────────────────┘
```

---

## The 5-Layer NLP Pipeline

### Layer 1 — Slang & Dialect Normalization
Converts 40+ Indonesian farming dialect words to standard vocabulary before any processing. Runs on raw user input **before** stopword removal.

```python
# Examples from SLANG_DICT:
"oyot"     → "akar akar busuk"          # Javanese for "root"
"benyek"   → "busuk berair membusuk"    # Javanese for "mushy/rotten"
"brambang" → "bawang merah"             # Javanese for "shallot"
"krowok"   → "berlubang bolong dimakan" # holed/eaten through
"lonyot"   → "busuk lunak berlendir"    # soft rot with slime
"bacin"    → "berbau busuk menyengat"   # foul smell
```

### Layer 2 — Knowledge Base Enrichment
Before building the TF-IDF matrix, each KB entry is enriched with additional synonyms and slang variants for its disease. This bridges the vocabulary gap between formal KB text and farmer dialect.

```python
KB_ENRICHMENT = {
    'Busuk Akar Phytophthora (Cabai)':
        ' cabe cabai akar busuk benyek oyot membusuk berair layu mendadak...',
    'Ulat Grayak (Bawang Merah)':
        ' bawang merah brambang ulat grayak krowok bolong dimakan...',
    # ... 6 diseases enriched
}
```

### Layer 3 — TF-IDF Bigram Vectorization
Uses `TfidfVectorizer(ngram_range=(1, 2), min_df=1)` — bigrams capture compound symptom patterns like "akar busuk", "daun kuning", "bercak coklat" that unigrams alone would miss.

### Layer 4 — Cosine Similarity Retrieval
Standard cosine similarity between the preprocessed query vector and the TF-IDF matrix of all KB entries.

### Layer 5 — Commodity Boost / Penalty
If a commodity is detected in the raw query, scores for matching diseases get a +0.30 boost; competing commodities get a -0.20 penalty. This resolves disambiguation problems like *"bawang merah"* vs *"bawang daun"*.

```python
BOOST_VALUE   = 0.30  # boost if commodity matches disease entry
PENALTY_VALUE = 0.20  # penalty for ambiguous similar commodities
THRESHOLD     = 0.20  # below this → Gemini API fallback
```

---

## Evaluation Results

Tested on 30 out-of-sample farmer dialect queries across 6 disease classes:

| Class | Precision | Recall | F1-Score |
|---|---|---|---|
| Bercak Daun Cercospora (Bayam) | 1.00 | 1.00 | 1.00 |
| Busuk Akar Phytophthora (Cabai) | 1.00 | 1.00 | 1.00 |
| Busuk Lunak (Kubis) | 1.00 | 1.00 | 1.00 |
| Ulat Grayak (Bawang Merah) | 1.00 | 1.00 | 1.00 |
| Powdery Mildew / Embun Tepung (Anggur) | 1.00 | 0.60 | 0.75 |
| Embun Tepung (Apel) | 0.75 | 1.00 | 0.86 |
| **Weighted Average** | **0.9667** | **0.9333** | **0.9152** |

> Threshold tuning analysis shows F1-score is maximized at threshold=0.20, with 28/30 queries answered locally by TF-IDF and 2 routed to Gemini fallback.

---

## Project Structure

```
agribot/
├── index.php                          # Landing page
├── konsultasi.php                     # Chat UI (Marked.js + Fetch API)
├── admin.php                          # Admin panel (login, CRUD, CSV import)
├── config.php                         # DB credentials (gitignored)
│
└── backend_python/
    ├── app.py                         # Flask API server (main entry point)
    ├── requirements.txt               # Python dependencies
    ├── .env.example                   # Environment variables template
    │
    ├── 1_preprocessing_pipeline.py    # Slang normalization + Sastrawi preprocessing
    ├── 2_kb_enrichment.py             # Knowledge base synonym enrichment
    ├── 3_tfidf_model_builder.py       # TF-IDF model build + commodity boost predictor
    ├── 4_stress_test_evaluator.py     # 30-query out-of-sample evaluation
    ├── 5_threshold_tuning.py          # Threshold optimization curve analysis
    │
    └── sql_update_kb.sql              # SQL UPDATE queries for KB enrichment
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | PHP 8.x · HTML/CSS · JavaScript · Marked.js |
| Chat API | Python 3.11 · Flask · Flask-CORS |
| NLP Engine | Scikit-learn (TF-IDF) · PySastrawi (stemming/stopword) |
| AI Fallback | Gemini API (`gemini-2.5-flash`) |
| Database | MySQL 8.0 |
| Deployment | Linux/SSH · Production domain |

---

## Local Development

### Prerequisites

- PHP 8.x + MySQL 8.0
- Python 3.11+
- Gemini API key

### Setup

```bash
git clone https://github.com/Tyruntz/agribot.git
cd agribot

# Install Python dependencies
pip install -r backend_python/requirements.txt

# Configure environment
cp backend_python/.env.example backend_python/.env
# Fill in: DB_HOST, DB_USER, DB_PASS, DB_NAME, GEMINI_API_KEY

# Set up MySQL database
mysql -u root -p < backend_python/sql_update_kb.sql
```

### Run

```bash
# Start Flask API (from backend_python/)
cd backend_python
python app.py
# → http://localhost:5000

# Serve PHP frontend (from project root)
php -S localhost:8000
# → http://localhost:8000
```

### Admin Panel

```
http://localhost:8000/admin.php
```

Login with credentials set in `config.php` (`ADMIN_USER` / `ADMIN_PASS`).

---

## Admin Panel Features

- **Knowledge base CRUD** — add, view, delete disease entries
- **CSV batch import** — bulk upload with format `Penyakit, Gejala, Solusi`
- **Live search** — client-side filter across all KB entries
- **Model metrics dashboard** — total records, unique disease count, F1-score display
- **Hybrid engine status** — shows TF-IDF + Gemini online status
- **Responsive** — works on mobile (hamburger menu, drawer sidebar)

---

## Environment Variables

```env
DB_HOST=localhost
DB_USER=root
DB_PASS=your_password
DB_NAME=db_pertanian
GEMINI_API_KEY=your_gemini_api_key
```

---

## Running the Evaluation Suite

```bash
cd backend_python

# Build TF-IDF model from enriched KB
python 3_tfidf_model_builder.py

# Run 30-query stress test (outputs CSV + confusion matrix PNG)
python 4_stress_test_evaluator.py

# Run threshold tuning analysis (outputs tuning curve PNG)
python 5_threshold_tuning.py
```

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

> Built as a paid freelance project for the agricultural sector, 2025.
> Part of [Engelbertus Prayoga's](https://github.com/Tyruntz) freelance AI & web development work.
> Open for similar commissions — reach out via [GitHub Issues](https://github.com/Tyruntz/agribot/issues).
