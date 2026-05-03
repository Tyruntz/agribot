import pandas as pd
import mysql.connector

# 1. BACA LANGSUNG FILE EXCEL ASLINYA (Gak usah di-save ke CSV)
df = pd.read_excel('dataset_pertanian.xlsx')

# 2. Konek ke Database
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="db_pertanian"
)
cursor = conn.cursor()

# 3. Looping data dan masukkan ke MySQL
print("Mulai import data...")
sukses = 0

for index, row in df.iterrows():
    # Gabung nama tanaman dan penyakit
    nama_lengkap_penyakit = f"{row['jenis_hama_penyakit_tanaman']} ({row['nama_tanaman']})"
    gejala = row['gejala']
    solusi = row['solusi']

    # Pake try-except biar kalau ada baris yang kosong/error, script nggak langsung mati
    try:
        sql = "INSERT INTO knowledge_base (penyakit, gejala, solusi) VALUES (%s, %s, %s)"
        val = (nama_lengkap_penyakit, gejala, solusi)
        cursor.execute(sql, val)
        sukses += 1
    except Exception as e:
        print(f"Error di baris {index}: {e}")

conn.commit()
print(f"Beres bos! {sukses} baris data berhasil masuk ke MySQL.")

cursor.close()
conn.close()