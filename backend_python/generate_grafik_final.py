import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import precision_score, recall_score, f1_score

print("📊 Memulai Analisis Dataset & Generate Grafik Final...")

# 1. Load Dataset
df = pd.read_csv('dataset_agribot_final.csv')
total_data = len(df)

# 2. Cek Variasi Unik
# Menghitung berapa banyak teks gejala yang benar-benar berbeda
variasi_unik = df['Gejala'].nunique()

print("\n" + "="*40)
print("📌 STATISTIK DATASET BAB 4")
print("="*40)
print(f"Total Baris Data       : {total_data}")
print(f"Total Variasi Gejala   : {variasi_unik}")
print(f"Persentase Keunikan    : {(variasi_unik/total_data)*100:.2f}%")
print("="*40)

# 3. Hitung Ulang Metrik Evaluasi
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(df['Gejala'])

y_true = df['Penyakit'].tolist()
y_pred = []

for gejala_input in df['Gejala']:
    input_vec = vectorizer.transform([gejala_input])
    similarity_scores = cosine_similarity(input_vec, tfidf_matrix).flatten()
    best_match_idx = similarity_scores.argmax()
    y_pred.append(df.iloc[best_match_idx]['Penyakit'])

# Hitung Precision, Recall, F1 (weighted)
precision = precision_score(y_true, y_pred, average='weighted', zero_division=0) * 100
recall = recall_score(y_true, y_pred, average='weighted', zero_division=0) * 100
f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0) * 100

print(f"\n📈 Precision : {precision:.2f}%")
print(f"📈 Recall    : {recall:.2f}%")
print(f"📈 F1-Score  : {f1:.2f}%\n")

# 4. Generate Grafik Bar Chart
labels = ['Precision', 'Recall', 'F1-Score']
values = [precision, recall, f1]
colors = ['#3498db', '#f1c40f', '#2ecc71'] # Biru, Kuning, Hijau

plt.figure(figsize=(8, 6))
bars = plt.bar(labels, values, color=colors, width=0.6)

# Tambahkan label angka di atas batang
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 1, f'{yval:.2f}%', 
             ha='center', va='bottom', fontsize=12, fontweight='bold')

plt.title('Hasil Evaluasi Kinerja Chatbot (Metode TF-IDF)', fontsize=14, fontweight='bold', pad=20)
plt.ylabel('Persentase (%)', fontsize=12)
plt.ylim(0, 110) # Biar mentok atasnya 100% lebih dikit buat margin
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Save Grafik
nama_file = 'grafik_evaluasi_bab4.png'
plt.savefig(nama_file, dpi=300, bbox_inches='tight')
print(f"✅ Grafik berhasil disimpan sebagai '{nama_file}'")
print("🚀 Kirim angka statistik dan gambar ini ke Wian buat ditaruh di laporan!")