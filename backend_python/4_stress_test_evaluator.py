"""
KODE 4: Stress Test Evaluator
==============================
Menjalankan evaluasi stress test pada 30 kueri out-of-sample
dan menghasilkan laporan lengkap: confusion matrix, per-class metrics,
routing analysis, dan file hasil CSV.

Cara pakai:
    python 4_stress_test_evaluator.py

Output:
    - stress_test_results.csv       (detail 30 kueri + status prediksi)
    - stress_test_report.txt        (ringkasan metrik)
    - confusion_matrix_stress.png   (gambar confusion matrix)
    - perclass_metrics.png          (grafik per-kelas)
"""

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import (
    confusion_matrix, classification_report,
    precision_recall_fscore_support, accuracy_score
)
from tfidf_model_builder import build_model, predict, THRESHOLD

# ── Konfigurasi ───────────────────────────────────────────────────────
STRESS_TEST_FILE = 'data-stress-test.txt'    # file kueri uji
KB_ENRICHED_CSV  = 'dataset_agribot_enriched.csv'
OUTPUT_CSV       = 'stress_test_results.csv'
OUTPUT_REPORT    = 'stress_test_report.txt'
OUTPUT_CM_IMG    = 'confusion_matrix_stress.png'
OUTPUT_BAR_IMG   = 'perclass_metrics.png'

CLASSES_ORDER = [
    'Bercak Daun Cercospora (Bayam)',
    'Busuk Akar Phytophthora (Cabai)',
    'Busuk Lunak (Kubis)',
    'Ulat Grayak (Bawang Merah)',
    'Powdery Mildew (Embun Tepung) (Anggur)',
    'Embun Tepung (Apel)',
]
SHORT_LABELS = [
    'Cercospora\n(Bayam)', 'Busuk Akar\nPhytophthora\n(Cabai)',
    'Busuk Lunak\n(Kubis)', 'Ulat Grayak\n(Bwg Merah)',
    'Embun Tepung\n(Anggur)', 'Embun Tepung\n(Apel)',
]


def get_kb_label(target_penyakit: str, komoditas: str,
                 kb_labels: list) -> str:
    """Cari label KB yang paling cocok untuk pasangan target+komoditas."""
    for k in kb_labels:
        if (target_penyakit.lower() in k.lower()
                and komoditas.lower() in k.lower()):
            return k
    for k in kb_labels:
        if target_penyakit.lower() in k.lower():
            return k
    return target_penyakit


def run_stress_test(df_kb, vectorizer, tfidf_matrix, col_penyakit):
    """Jalankan 30 kueri stress test dan kumpulkan hasil."""
    stress_df  = pd.read_csv(STRESS_TEST_FILE)
    kb_labels  = df_kb[col_penyakit].unique().tolist()
    results    = []

    print(f"Menjalankan stress test: {len(stress_df)} kueri...\n")

    for _, row in stress_df.iterrows():
        result   = predict(row['Query_User'], df_kb, vectorizer,
                           tfidf_matrix, col_penyakit)
        label_kb = get_kb_label(row['Target_Penyakit'],
                                row['Komoditas'], kb_labels)

        target  = row['Target_Penyakit'].lower()
        komod   = row['Komoditas'].lower()
        pred_l  = result['pred_label'].lower()
        correct = target in pred_l and komod in pred_l

        results.append({
            'ID'             : row['ID'],
            'Query_User'     : row['Query_User'],
            'Query_Bersih'   : result['query_clean'],
            'Target_Penyakit': row['Target_Penyakit'],
            'Komoditas'      : row['Komoditas'],
            'Label_KB'       : label_kb,
            'Pred_Label'     : result['pred_label'],
            'Cosine_Score'   : round(result['score'], 4),
            'Komoditas_Det'  : result['komoditas'],
            'Jalur'          : 'Lokal TF-IDF' if result['is_local'] else 'Gemini Fallback',
            'Status'         : 'Benar' if correct else 'Salah',
        })

    return pd.DataFrame(results)


def plot_confusion_matrix(res_df: pd.DataFrame):
    """Plot confusion matrix stress test."""
    cm = confusion_matrix(res_df['Label_KB'], res_df['Pred_Label'],
                          labels=CLASSES_ORDER)
    total  = len(res_df)
    benar  = (res_df['Status'] == 'Benar').sum()
    akurasi = benar / total * 100

    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(cm, interpolation='nearest', cmap='Blues')
    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    ax.set_xticks(range(len(CLASSES_ORDER)))
    ax.set_yticks(range(len(CLASSES_ORDER)))
    ax.set_xticklabels(SHORT_LABELS, fontsize=8.5)
    ax.set_yticklabels(SHORT_LABELS, fontsize=8.5)
    ax.set_xlabel('Prediksi Sistem', fontsize=12, fontweight='bold')
    ax.set_ylabel('Label Aktual (Ground-Truth)', fontsize=12, fontweight='bold')
    ax.set_title(
        f'Confusion Matrix — Stress Testing ({total} Kueri Dialek/Slang Petani)\n'
        f'{len(CLASSES_ORDER)} Kelas Penyakit × {len(CLASSES_ORDER)} Kelas Penyakit',
        fontsize=12, fontweight='bold'
    )

    thresh = cm.max() / 2
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, str(cm[i, j]), ha='center', va='center',
                    fontsize=14, fontweight='bold',
                    color='white' if cm[i, j] > thresh else 'black')

    ax.text(1.02, 0.5,
            f'Total Query: {total}\nBenar: {benar}\nSalah: {total-benar}\n'
            f'Akurasi: {akurasi:.1f}%',
            transform=ax.transAxes, fontsize=10, va='center',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

    plt.tight_layout()
    plt.savefig(OUTPUT_CM_IMG, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✅ Confusion matrix tersimpan: {OUTPUT_CM_IMG}")


def plot_perclass_metrics(res_df: pd.DataFrame):
    """Plot bar chart per-kelas precision/recall/F1."""
    p, r, f, s = precision_recall_fscore_support(
        res_df['Label_KB'], res_df['Pred_Label'],
        labels=CLASSES_ORDER, zero_division=0
    )

    x  = np.arange(len(CLASSES_ORDER))
    w  = 0.25
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(x - w,   p, w, label='Precision', color='steelblue',  alpha=0.85)
    ax.bar(x,       r, w, label='Recall',    color='darkorange', alpha=0.85)
    ax.bar(x + w,   f, w, label='F1-Score',  color='seagreen',   alpha=0.85)

    ax.set_xticks(x)
    ax.set_xticklabels(SHORT_LABELS, fontsize=8)
    ax.set_ylabel('Skor', fontsize=12)
    ax.set_ylim(0, 1.15)
    ax.legend(fontsize=10)
    ax.set_title('Metrik Per-Kelas Stress Testing (Out-of-Sample)',
                 fontsize=13, fontweight='bold')
    ax.axhline(y=1.0, color='gray', linestyle='--', alpha=0.4, linewidth=1)

    for i in range(len(CLASSES_ORDER)):
        ax.text(x[i]-w,   p[i]+0.03, f'{p[i]:.2f}', ha='center', fontsize=8)
        ax.text(x[i],     r[i]+0.03, f'{r[i]:.2f}', ha='center', fontsize=8)
        ax.text(x[i]+w,   f[i]+0.03, f'{f[i]:.2f}', ha='center', fontsize=8)

    plt.tight_layout()
    plt.savefig(OUTPUT_BAR_IMG, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✅ Per-class metrics tersimpan: {OUTPUT_BAR_IMG}")


def generate_report(res_df: pd.DataFrame) -> str:
    """Buat laporan teks ringkasan hasil stress test."""
    total   = len(res_df)
    benar   = (res_df['Status'] == 'Benar').sum()
    salah   = total - benar
    akurasi = benar / total * 100

    local_count   = (res_df['Jalur'] == 'Lokal TF-IDF').sum()
    fallback_count = (res_df['Jalur'] == 'Gemini Fallback').sum()

    p, r, f, s = precision_recall_fscore_support(
        res_df['Label_KB'], res_df['Pred_Label'],
        labels=CLASSES_ORDER, zero_division=0
    )

    lines = [
        "=" * 60,
        "LAPORAN STRESS TEST AGRIBOT",
        "=" * 60,
        f"Total kueri uji  : {total}",
        f"Prediksi benar   : {benar}",
        f"Prediksi salah   : {salah}",
        f"Akurasi overall  : {akurasi:.1f}%",
        f"Dijawab lokal    : {local_count}",
        f"Fallback Gemini  : {fallback_count}",
        "",
        "-" * 60,
        "METRIK PER-KELAS",
        "-" * 60,
        f"{'Kelas':45s} | P    | R    | F1   | n",
    ]
    for i, cls in enumerate(CLASSES_ORDER):
        lines.append(
            f"{cls:45s} | {p[i]:.2f} | {r[i]:.2f} | {f[i]:.2f} | {s[i]}"
        )

    lines += [
        "",
        "-" * 60,
        "DETAIL MISKLASIFIKASI",
        "-" * 60,
    ]
    salah_df = res_df[res_df['Status'] == 'Salah']
    for _, row in salah_df.iterrows():
        lines += [
            f"No {row['ID']:2d} | {row['Target_Penyakit']} ({row['Komoditas']})",
            f"       Prediksi: {row['Pred_Label']}",
            f"       Skor    : {row['Cosine_Score']}",
            f"       Query   : {row['Query_User'][:60]}...",
            "",
        ]

    return '\n'.join(lines)


if __name__ == '__main__':
    print("=== Stress Test Evaluator AgriBot ===\n")

    # Build model
    df_kb, vectorizer, tfidf_matrix, col_sakit = build_model(
        csv_path=KB_ENRICHED_CSV,
        save_path='agribot_model.pkl'
    )

    # Jalankan stress test
    res_df = run_stress_test(df_kb, vectorizer, tfidf_matrix, col_sakit)

    # Simpan CSV
    res_df.to_csv(OUTPUT_CSV, index=False)
    print(f"✅ Hasil CSV tersimpan: {OUTPUT_CSV}\n")

    # Plot
    plot_confusion_matrix(res_df)
    plot_perclass_metrics(res_df)

    # Report
    report = generate_report(res_df)
    print(report)
    with open(OUTPUT_REPORT, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n✅ Laporan tersimpan: {OUTPUT_REPORT}")
