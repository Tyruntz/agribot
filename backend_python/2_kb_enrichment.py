"""
KODE 2: Knowledge Base Enrichment
===================================
Memperkaya kolom Gejala di KB dengan sinonim/slang petani.
Jumlah baris TETAP 597 — yang berubah hanya ISI kolom Gejala.

Cara pakai:
    python 2_kb_enrichment.py

Output:
    - dataset_agribot_enriched.csv  (file KB yang sudah diperkaya)
    - sql_update_kb.sql             (query UPDATE untuk MySQL langsung)
    - enrichment_diff.txt           (perbandingan sebelum vs sesudah)
"""

import pandas as pd

# ── Konfigurasi Enrichment ────────────────────────────────────────────
# Format: 'Nama Penyakit (Komoditas)': ' kata_tambahan_1 kata_tambahan_2 ...'
# Awali dengan spasi agar tidak langsung menyambung ke teks sebelumnya.
# Tambahkan entri baru di sini jika ada penyakit lain yang perlu diperkaya.

KB_ENRICHMENT = {
    'Bercak Daun Cercospora (Bayam)':
        ' bayem bayam bercak cercospora daun bercak coklat keabu gosong kering '
        'jamur bercak daun bolong',

    'Busuk Akar Phytophthora (Cabai)':
        ' cabe cabai akar busuk busuk akar phytophthora benyek oyot membusuk '
        'berair layu mendadak akar membusuk batang coklat',

    'Busuk Lunak (Kubis)':
        ' kol kubis busuk lunak lonyot berlendir bacin bau busuk lendir '
        'daun kubis busuk',

    'Ulat Grayak (Bawang Merah)':
        ' bawang merah brambang ulat grayak daun berlubang krowok bolong '
        'dimakan ulat bawang merah daun putus ulat hijau',

    'Embun Tepung (Apel)':
        ' apel daun bedak putih tepung embun tepung bercak putih '
        'apel embun tepung daun apel',

    'Powdery Mildew (Embun Tepung) (Anggur)':
        ' anggur daun bedak putih tepung embun tepung burik '
        'anggur embun tepung',

    # Kurangi daya tarik Bawang Daun agar tidak bentrok dengan Bawang Merah
    'Ulat Grayak (Bawang Daun)':
        ' bawang daun ulat grayak',
}

# ── Path file ─────────────────────────────────────────────────────────
INPUT_CSV   = 'dataset_agribot_final.csv'   # ganti path jika perlu
OUTPUT_CSV  = 'dataset_agribot_enriched.csv'
OUTPUT_SQL  = 'sql_update_kb.sql'
OUTPUT_DIFF = 'enrichment_diff.txt'


def enrich_kb(df: pd.DataFrame, enrichment: dict) -> pd.DataFrame:
    """
    Tambahkan kata slang ke kolom Gejala untuk penyakit yang ditentukan.
    Deteksi nama kolom secara otomatis (case-insensitive).

    Args:
        df         : DataFrame KB asli
        enrichment : Dict {nama_penyakit: kata_tambahan}

    Returns:
        DataFrame yang sudah diperkaya (baris tidak bertambah)
    """
    # Deteksi nama kolom
    col_map   = {c.lower(): c for c in df.columns}
    col_sakit = col_map.get('penyakit', 'Penyakit')
    col_gejala= col_map.get('gejala',   'Gejala')

    df_out = df.copy()
    enriched_count = 0

    for penyakit_key, tambahan in enrichment.items():
        mask = df_out[col_sakit].str.lower() == penyakit_key.lower()
        if mask.any():
            df_out.loc[mask, col_gejala] = (
                df_out.loc[mask, col_gejala] + tambahan
            )
            n = mask.sum()
            enriched_count += n
            print(f"  ✅ '{penyakit_key}' — {n} baris diperkaya")
        else:
            print(f"  ⚠️  '{penyakit_key}' tidak ditemukan di KB")

    print(f"\nTotal baris diperkaya : {enriched_count}")
    print(f"Total baris KB        : {len(df_out)} (tidak berubah)")
    return df_out


def generate_sql_update(df_orig: pd.DataFrame,
                         df_enr:  pd.DataFrame,
                         enrichment: dict) -> str:
    """
    Generate query SQL UPDATE untuk memperbarui MySQL langsung.
    Hanya baris yang berubah yang di-UPDATE.
    """
    col_map   = {c.lower(): c for c in df_orig.columns}
    col_sakit = col_map.get('penyakit', 'Penyakit')
    col_gejala= col_map.get('gejala',   'Gejala')

    lines = [
        "-- ============================================================",
        "-- SQL UPDATE: Knowledge Base Enrichment AgriBot",
        "-- Jalankan di MySQL untuk memperbarui kolom gejala",
        "-- Tabel: knowledge_base | Kolom: gejala",
        "-- PENTING: Backup tabel terlebih dahulu sebelum menjalankan!",
        "-- ============================================================\n",
    ]

    for penyakit_key in enrichment.keys():
        mask = df_enr[col_sakit].str.lower() == penyakit_key.lower()
        rows = df_enr[mask]
        for _, row in rows.iterrows():
            gejala_baru = row[col_gejala].replace("'", "''")  # escape single quote
            lines.append(
                f"UPDATE knowledge_base\n"
                f"SET gejala = '{gejala_baru}'\n"
                f"WHERE penyakit = '{penyakit_key}';\n"
            )

    return '\n'.join(lines)


def generate_diff(df_orig: pd.DataFrame,
                  df_enr:  pd.DataFrame,
                  enrichment: dict) -> str:
    """
    Buat laporan perbandingan sebelum vs sesudah enrichment.
    """
    col_map   = {c.lower(): c for c in df_orig.columns}
    col_sakit = col_map.get('penyakit', 'Penyakit')
    col_gejala= col_map.get('gejala',   'Gejala')

    lines = ["=== ENRICHMENT DIFF REPORT ===\n"]
    for penyakit_key in enrichment.keys():
        mask_o = df_orig[col_sakit].str.lower() == penyakit_key.lower()
        mask_e = df_enr [col_sakit].str.lower() == penyakit_key.lower()
        if not mask_o.any():
            continue
        orig_sample = df_orig[mask_o].iloc[0][col_gejala]
        enr_sample  = df_enr [mask_e].iloc[0][col_gejala]
        n_tambah    = len(enr_sample) - len(orig_sample)
        lines += [
            f"Penyakit : {penyakit_key}",
            f"SEBELUM  : {orig_sample}",
            f"SESUDAH  : {enr_sample}",
            f"Karakter ditambahkan: +{n_tambah}",
            "-" * 80,
        ]
    return '\n'.join(lines)


if __name__ == '__main__':
    print("=== Knowledge Base Enrichment AgriBot ===\n")

    # Load
    df_orig = pd.read_csv(INPUT_CSV)
    print(f"KB dimuat: {len(df_orig)} baris, kolom: {df_orig.columns.tolist()}\n")

    # Enrichment
    print("Proses enrichment:")
    df_enriched = enrich_kb(df_orig, KB_ENRICHMENT)

    # Simpan CSV
    df_enriched.to_csv(OUTPUT_CSV, index=False)
    print(f"\n✅ CSV tersimpan: {OUTPUT_CSV}")

    # Buat SQL UPDATE
    sql = generate_sql_update(df_orig, df_enriched, KB_ENRICHMENT)
    with open(OUTPUT_SQL, 'w', encoding='utf-8') as f:
        f.write(sql)
    print(f"✅ SQL tersimpan: {OUTPUT_SQL}")

    # Buat diff report
    diff = generate_diff(df_orig, df_enriched, KB_ENRICHMENT)
    with open(OUTPUT_DIFF, 'w', encoding='utf-8') as f:
        f.write(diff)
    print(f"✅ Diff report: {OUTPUT_DIFF}")

    print("\nSelesai. Jumlah baris tidak berubah dari semula.")
