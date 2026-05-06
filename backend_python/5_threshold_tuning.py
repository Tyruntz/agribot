"""
KODE 5: Threshold Tuning & Kurva Evaluasi
==========================================
Menganalisis pengaruh nilai threshold Cosine Similarity terhadap
precision, recall, dan F1-Score retriever lokal.
Menghasilkan kurva tuning sebagai justifikasi empiris pemilihan threshold.

Cara pakai:
    python 5_threshold_tuning.py

Output:
    - threshold_tuning_results.csv   (data numerik per threshold)
    - threshold_tuning_curve.png     (kurva visual)
    - threshold_recommendation.txt   (rekomendasi threshold optimal)
"""

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_similarity
from tfidf_model_builder import build_model, detect_commodity, apply_boost_penalty
from preprocessing_pipeline import preprocess_text

# ── Konfigurasi ───────────────────────────────────────────────────────
STRESS_TEST_FILE = 'data-stress-test.txt'
KB_ENRICHED_CSV  = 'dataset_agribot_enriched.csv'
OUTPUT_CSV       = 'threshold_tuning_results.csv'
OUTPUT_IMG       = 'threshold_tuning_curve.png'
OUTPUT_TXT       = 'threshold_recommendation.txt'

THRESHOLDS       = np.arange(0.05, 0.95, 0.05)
CURRENT_THRESHOLD = 0.20

CLASSES_ORDER = [
    'Bercak Daun Cercospora (Bayam)',
    'Busuk Akar Phytophthora (Cabai)',
    'Busuk Lunak (Kubis)',
    'Ulat Grayak (Bawang Merah)',
    'Powdery Mildew (Embun Tepung) (Anggur)',
    'Embun Tepung (Apel)',
]


def get_kb_label(target, komoditas, kb_labels):
    for k in kb_labels:
        if target.lower() in k.lower() and komoditas.lower() in k.lower():
            return k
    for k in kb_labels:
        if target.lower() in k.lower():
            return k
    return target


def evaluate_threshold(threshold, stress_df, df_kb, vectorizer,
                        tfidf_matrix, col_penyakit):
    """
    Hitung metrik untuk satu nilai threshold.
    Semua 30 query diasumsikan "in-KB" (ada jawabannya di KB).
    """
    kb_labels = df_kb[col_penyakit].unique().tolist()
    tp_local = fp_local = fn_local = 0

    for _, row in stress_df.iterrows():
        q_clean   = preprocess_text(row['Query_User'], use_slang=True)
        q_vec     = vectorizer.transform([q_clean])
        scores    = cosine_similarity(q_vec, tfidf_matrix).flatten()
        scores    = apply_boost_penalty(scores, row['Query_User'], df_kb, col_penyakit)

        best_idx  = scores.argmax()
        score     = scores[best_idx]
        pred      = df_kb.iloc[best_idx][col_penyakit].lower()
        target    = row['Target_Penyakit'].lower()
        komod     = row['Komoditas'].lower()
        correct   = target in pred and komod in pred

        if score >= threshold:
            if correct:
                tp_local += 1    # dijawab lokal & benar
            else:
                fp_local += 1    # dijawab lokal & salah
        else:
            fn_local += 1        # fallback ke Gemini (padahal ada di KB)

    prec   = tp_local / (tp_local + fp_local) if (tp_local + fp_local) > 0 else 0
    rec    = tp_local / (tp_local + fn_local)  if (tp_local + fn_local) > 0 else 0
    f1     = 2*prec*rec / (prec+rec) if (prec+rec) > 0 else 0
    answered = tp_local + fp_local

    return {
        'threshold'       : round(float(threshold), 2),
        'tp_local'        : tp_local,
        'fp_local'        : fp_local,
        'fn_local'        : fn_local,
        'answered_locally': answered,
        'fallback_count'  : fn_local,
        'precision'       : round(prec, 4),
        'recall'          : round(rec, 4),
        'f1'              : round(f1,   4),
    }


def plot_tuning_curve(thr_df: pd.DataFrame):
    """Plot kurva Precision-Recall-F1 vs Threshold."""
    fig, ax1 = plt.subplots(figsize=(10, 6))

    ax1.plot(thr_df['threshold'], thr_df['precision'], 'b-o',
             markersize=5, label='Precision Lokal', linewidth=2)
    ax1.plot(thr_df['threshold'], thr_df['recall'],   'g-s',
             markersize=5, label='Recall Lokal',    linewidth=2)
    ax1.plot(thr_df['threshold'], thr_df['f1'],       'r-^',
             markersize=5, label='F1-Score',         linewidth=2)
    ax1.set_xlabel('Nilai Threshold Cosine Similarity', fontsize=12)
    ax1.set_ylabel('Skor Metrik', fontsize=12)
    ax1.set_ylim(0, 1.05)

    ax2 = ax1.twinx()
    ax2.bar(thr_df['threshold'], thr_df['answered_locally'],
            width=0.03, alpha=0.2, color='steelblue',
            label='Dijawab Lokal (n)')
    ax2.set_ylabel('Jumlah Query Dijawab Lokal', fontsize=11,
                   color='steelblue')
    ax2.tick_params(axis='y', labelcolor='steelblue')

    # Garis threshold saat ini
    ax1.axvline(x=CURRENT_THRESHOLD, color='purple', linestyle='--',
                linewidth=2, label=f'Threshold Saat Ini ({CURRENT_THRESHOLD})')

    # Anotasi F1 max
    best = thr_df.loc[thr_df['f1'].idxmax()]
    ax1.annotate(
        f"F1 max = {best['f1']:.2f}\n@ thr={best['threshold']:.2f}",
        xy=(best['threshold'], best['f1']),
        xytext=(best['threshold']+0.08, best['f1']-0.12),
        arrowprops=dict(arrowstyle='->', color='red'),
        fontsize=9, color='red'
    )

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2,
               loc='upper right', fontsize=9)

    ax1.set_title('Kurva Tuning Threshold Cosine Similarity\n'
                  'AgriBot Hybrid TF-IDF + Gemini Fallback',
                  fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUTPUT_IMG, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✅ Kurva tuning tersimpan: {OUTPUT_IMG}")


if __name__ == '__main__':
    print("=== Threshold Tuning AgriBot ===\n")

    df_kb, vectorizer, tfidf_matrix, col_sakit = build_model(
        csv_path=KB_ENRICHED_CSV,
        save_path='agribot_model.pkl'
    )

    stress_df = pd.read_csv(STRESS_TEST_FILE)
    results   = []

    print(f"Mengevaluasi {len(THRESHOLDS)} nilai threshold...\n")
    for thr in THRESHOLDS:
        res = evaluate_threshold(thr, stress_df, df_kb, vectorizer,
                                 tfidf_matrix, col_sakit)
        results.append(res)
        print(f"  thr={thr:.2f} | P={res['precision']:.2f} "
              f"R={res['recall']:.2f} F1={res['f1']:.2f} "
              f"answered={res['answered_locally']}")

    thr_df = pd.DataFrame(results)
    thr_df.to_csv(OUTPUT_CSV, index=False)
    print(f"\n✅ Data tuning tersimpan: {OUTPUT_CSV}")

    plot_tuning_curve(thr_df)

    # Rekomendasi
    best       = thr_df.loc[thr_df['f1'].idxmax()]
    curr_row   = thr_df[thr_df['threshold'] == CURRENT_THRESHOLD].iloc[0]
    rec_lines  = [
        "=== REKOMENDASI THRESHOLD ===",
        f"Threshold optimal (F1 max) : {best['threshold']}",
        f"  F1={best['f1']:.4f} | Precision={best['precision']:.4f} | Recall={best['recall']:.4f}",
        f"  Query dijawab lokal: {best['answered_locally']}/30",
        "",
        f"Threshold saat ini         : {CURRENT_THRESHOLD}",
        f"  F1={curr_row['f1']:.4f} | Precision={curr_row['precision']:.4f} | Recall={curr_row['recall']:.4f}",
        f"  Query dijawab lokal: {curr_row['answered_locally']}/30",
    ]
    rec_text = '\n'.join(rec_lines)
    print(f"\n{rec_text}")
    with open(OUTPUT_TXT, 'w') as f:
        f.write(rec_text)
    print(f"\n✅ Rekomendasi tersimpan: {OUTPUT_TXT}")
