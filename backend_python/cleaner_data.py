import pandas as pd

print("🚀 Memulai proses Data Transformation...")

# 1. Baca file Excel dari Wian (pastikan nama file sesuai)
# Kalau Wian ngasihnya CSV, ganti jadi pd.read_csv('data_mentah.csv', sep=';') atau ','
df = pd.read_excel('data_mentah.xlsx')

# 2. Buat DataFrame baru untuk format 3 kolom kita
df_clean = pd.DataFrame()

# 3. GABUNGKAN NAMA TANAMAN & PENYAKIT
# Hasil: "Bercak Daun (Anggrek)"
df_clean['Penyakit'] = df['jenis_hama_penyakit_tanaman'].astype(str).str.title() + " (" + df['nama_tanaman'].astype(str).str.title() + ")"

# 4. GEJALA TETAP (huruf kecil semua biar rapi buat TF-IDF)
df_clean['Gejala'] = df['gejala'].astype(str).str.lower()

# 5. SELIPKAN ORGANISME PENYEBAB KE DALAM SOLUSI
# Cek dulu kalau ada organisme yang kosong (NaN), kita kasih string kosong
df['Organisme Penyebab'] = df['Organisme Penyebab'].fillna('Tidak diketahui')
# Hasil: "(Penyebab: Cercospora dendrobii). Pangkas daun terinfeksi..."
df_clean['Solusi'] = "**(Penyebab: " + df['Organisme Penyebab'].astype(str) + ")**\n\nLangkah Penanganan:\n" + df['solusi_penanganan'].astype(str)

# 6. Hapus data yang kosong (kalau Wian nggak sengaja kelebihan narik baris di Excel)
df_clean = df_clean.dropna()

# 7. Save ke CSV yang siap di-import ke Admin Panel
df_clean.to_csv('dataset_agribot_final.csv', index=False)

print(f"✅ Selesai, Bos! Berhasil memproses {len(df_clean)} baris data.")
print("📁 Silakan cek file 'dataset_agribot_final.csv'")