"""
KODE 3: TF-IDF Model Builder + Commodity Boost Predictor
=========================================================
Membangun model TF-IDF dari KB yang sudah diperkaya,
lalu menyediakan fungsi predict dengan commodity boost & penalti.

Cara pakai:
    python 3_tfidf_model_builder.py

    Atau import ke script lain:
        from tfidf_model_builder import build_model, predict
"""

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import pickle
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from preprocessing_pipeline import preprocess_text, normalize_slang

# ── Konfigurasi Commodity Boost ──────────────────────────────────────
# Format: 'nama_komoditas_baku': ['kata_kunci_di_query']
COMMODITY_KEYWORDS = {
    'bayam'       : ['bayam', 'bayem'],
    'cabai'       : ['cabai', 'cabe'],
    'kubis'       : ['kubis', 'kol'],
    'bawang merah': ['bawang merah', 'brambang'],
    'anggur'      : ['anggur'],
    'apel'        : ['apel'],
}

# Jika komoditas A terdeteksi, turunkan skor komoditas-komoditas ini
COMMODITY_PENALTY = {
    'bawang merah': ['bawang daun', 'bawang putih'],
}

BOOST_VALUE   = 0.30   # nilai yang ditambahkan ke skor jika komoditas cocok
PENALTY_VALUE = 0.20   # nilai yang dikurangi dari skor komoditas yang ambigu
THRESHOLD     = 0.20   # batas minimum skor untuk dijawab lokal vs fallback Gemini


# ── Fungsi Utama ──────────────────────────────────────────────────────

def detect_commodity(raw_query: str) -> str | None:
    """
    Deteksi komoditas dari query mentah (SEBELUM preprocessing).
    Menggunakan raw query agar slang komoditas ('cabe', 'brambang') bisa terdeteksi.

    Returns:
        Nama komoditas baku jika terdeteksi, None jika tidak ada.
    """
    raw_lower = raw_query.lower()
    # Cek frasa dua kata lebih dulu (lebih spesifik)
    if 'bawang merah' in raw_lower or 'brambang' in raw_lower:
        return 'bawang merah'
    for commodity, keywords in COMMODITY_KEYWORDS.items():
        for kw in keywords:
            if kw in raw_lower:
                return commodity
    return None


def apply_boost_penalty(scores: np.ndarray,
                         raw_query: str,
                         df_kb: pd.DataFrame,
                         col_penyakit: str = 'Penyakit') -> np.ndarray:
    """
    Layer 5: Terapkan commodity boost dan penalti pada array skor cosine.

    Args:
        scores      : Array skor cosine dari sklearn
        raw_query   : Query mentah pengguna (belum dipreprocess)
        df_kb       : DataFrame knowledge base
        col_penyakit: Nama kolom penyakit di df_kb

    Returns:
        Array skor yang sudah dimodifikasi
    """
    detected = detect_commodity(raw_query)
    if not detected:
        return scores

    scores = scores.copy()
    for i, row in df_kb.iterrows():
        pl = row[col_penyakit].lower()
        if detected in pl:
            scores[i] = min(scores[i] + BOOST_VALUE, 1.0)
        if detected in COMMODITY_PENALTY:
            for penalti_komod in COMMODITY_PENALTY[detected]:
                if penalti_komod in pl:
                    scores[i] = max(scores[i] - PENALTY_VALUE, 0.0)
    return scores


def build_model(csv_path: str = 'dataset_agribot_enriched.csv',
                save_path: str = 'agribot_model.pkl') -> tuple:
    """
    Bangun model TF-IDF dari CSV knowledge base yang sudah diperkaya.

    Args:
        csv_path  : Path ke CSV KB enriched
        save_path : Path untuk menyimpan model (pickle)

    Returns:
        (df_kb, vectorizer, tfidf_matrix) — siap dipakai untuk prediksi
    """
    print(f"Memuat KB dari: {csv_path}")
    df = pd.read_csv(csv_path)

    # Deteksi nama kolom
    col_map   = {c.lower(): c for c in df.columns}
    col_sakit = col_map.get('penyakit', 'Penyakit')
    col_gejala= col_map.get('gejala',   'Gejala')

    print(f"KB dimuat: {len(df)} baris")

    # Preprocessing KB (tanpa slang — KB sudah baku + enrichment)
    df['gejala_bersih'] = df[col_gejala].apply(
        lambda x: preprocess_text(str(x), use_slang=False)
    )

    # TF-IDF Bigram (Layer 3)
    vectorizer   = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
    tfidf_matrix = vectorizer.fit_transform(df['gejala_bersih'])

    print(f"Model TF-IDF dibangun: {tfidf_matrix.shape[0]} dokumen, "
          f"{tfidf_matrix.shape[1]} fitur (unigram+bigram)")

    # Simpan model
    with open(save_path, 'wb') as f:
        pickle.dump({
            'df_kb'       : df,
            'vectorizer'  : vectorizer,
            'tfidf_matrix': tfidf_matrix,
            'col_penyakit': col_sakit,
            'col_gejala'  : col_gejala,
        }, f)
    print(f"Model disimpan ke: {save_path}")

    return df, vectorizer, tfidf_matrix, col_sakit


def load_model(model_path: str = 'agribot_model.pkl') -> tuple:
    """
    Load model TF-IDF yang sudah disimpan sebelumnya.

    Returns:
        (df_kb, vectorizer, tfidf_matrix, col_penyakit)
    """
    with open(model_path, 'rb') as f:
        m = pickle.load(f)
    return m['df_kb'], m['vectorizer'], m['tfidf_matrix'], m['col_penyakit']


def predict(raw_query: str,
            df_kb: pd.DataFrame,
            vectorizer: TfidfVectorizer,
            tfidf_matrix,
            col_penyakit: str = 'Penyakit') -> dict:
    """
    Prediksi penyakit dari query mentah pengguna.
    Menerapkan semua 5 lapisan optimasi.

    Args:
        raw_query    : Query mentah dari pengguna (slang/dialek diterima)
        df_kb        : DataFrame KB
        vectorizer   : TF-IDF vectorizer yang sudah di-fit
        tfidf_matrix : Sparse matrix TF-IDF KB
        col_penyakit : Nama kolom penyakit

    Returns:
        Dict dengan kunci:
            - pred_label  : Nama penyakit yang diprediksi
            - score       : Skor Cosine Similarity (setelah boost/penalti)
            - query_clean : Teks query setelah preprocessing
            - komoditas   : Komoditas yang terdeteksi (bisa None)
            - is_local    : True jika skor >= THRESHOLD, False jika perlu fallback
    """
    # Layer 1+2: Normalisasi slang + preprocessing
    query_clean = preprocess_text(raw_query, use_slang=True)

    # Layer 3+4: TF-IDF + Cosine Similarity
    query_vec = vectorizer.transform([query_clean])
    scores    = cosine_similarity(query_vec, tfidf_matrix).flatten()

    # Layer 5: Commodity boost + penalti
    scores = apply_boost_penalty(scores, raw_query, df_kb, col_penyakit)

    best_idx   = scores.argmax()
    best_score = scores[best_idx]
    pred_label = df_kb.iloc[best_idx][col_penyakit]
    komoditas  = detect_commodity(raw_query)

    return {
        'pred_label' : pred_label,
        'score'      : float(best_score),
        'query_clean': query_clean,
        'komoditas'  : komoditas,
        'is_local'   : best_score >= THRESHOLD,
    }


if __name__ == '__main__':
    print("=== TF-IDF Model Builder AgriBot ===\n")

    # Build model
    df_kb, vectorizer, tfidf_matrix, col_sakit = build_model(
        csv_path='dataset_agribot_enriched.csv',
        save_path='agribot_model.pkl'
    )

    # Test prediksi
    test_queries = [
        "oyot cabe kulo benyek parah tlg",
        "min daun bayem bercak gosong kyk kebakar",
        "brambang krowok bolong dimakanin ulet",
        "kol lonyot bau bacin gmn ngatasinnya",
        "anggur daunnya kyk ketumpahan bedak putih",
        "apel godhonge kena tepung putih trus rontok",
    ]

    print("\n=== Test Prediksi ===\n")
    for q in test_queries:
        result = predict(q, df_kb, vectorizer, tfidf_matrix, col_sakit)
        status = "✅ LOKAL" if result['is_local'] else "⚡ FALLBACK GEMINI"
        print(f"Query  : {q}")
        print(f"Bersih : {result['query_clean']}")
        print(f"Pred   : {result['pred_label']}")
        print(f"Skor   : {result['score']:.4f} | {status}")
        print(f"Komod  : {result['komoditas']}\n")
