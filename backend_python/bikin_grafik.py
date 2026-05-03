import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Data lengkap dari hasil evaluasi deterministic Wian
data = {
    'Penyakit': [
        'Bercak Daun Cercospora', 'Busuk Akar Phytophthora', 
        'Busuk Buah Botrytis', 'Busuk Lunak', 
        'Karat Daun', 'Lalat Buah', 
        'Layu Fusarium (Kacang Tanah)', 'Penggerek Buah', 'Ulat Grayak'
    ],
    'Precision': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 1.0, 1.0],
    'Recall':    [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 1.0, 1.0],
    'F1-Score':  [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 1.0, 1.0]
}

df = pd.DataFrame(data)

# MAGIC TRICK: Kita 'melt' datanya biar Seaborn bisa bikin grouped bar (berdampingan)
df_melted = df.melt(id_vars='Penyakit', var_name='Metrik', value_name='Skor')

# Styling Grafik Biar Kelihatan Mahal
plt.style.use('default')
sns.set_theme(style="whitegrid", rc={"axes.facecolor": "#f8f9fa"})
plt.figure(figsize=(12, 8))

# Warna Khusus: Precision (Biru), Recall (Kuning), F1-Score (Hijau)
warna = ['#3498db', '#f1c40f', '#2ecc71']

# Bikin Grouped Bar Chart Horizontal
ax = sns.barplot(
    x='Skor', 
    y='Penyakit', 
    hue='Metrik', 
    data=df_melted, 
    palette=warna,
    edgecolor='white',
    linewidth=1
)

plt.title('Evaluasi Algoritma: Precision, Recall, & F1-Score', fontsize=16, fontweight='bold', pad=20, color='#2c3e50')
plt.xlabel('Nilai Metrik (0.0 - 1.0)', fontsize=12, fontweight='bold', color='#34495e')
plt.ylabel('Kelas Target (Penyakit / Hama)', fontsize=12, fontweight='bold', color='#34495e')

# Limit X axis biar angka nggak kepotong di ujung
plt.xlim(0, 1.15)

# Nambahin angka desimal di ujung tiap bar
for p in ax.patches:
    width = p.get_width()
    # Posisikan teks persis di sebelah kanan bar
    ax.text(
        width + 0.015, 
        p.get_y() + p.get_height() / 2, 
        f'{width:.2f}', 
        va='center', 
        fontsize=10, 
        fontweight='bold', 
        color='#34495e'
    )

# Posisi Legend (Keterangan Warna)
plt.legend(title='Metrik Evaluasi', loc='lower right', frameon=True, shadow=True, fontsize=10, title_fontsize=11)

plt.tight_layout()

# Save ke file
plt.savefig('grafik_evaluasi_lengkap.png', dpi=300)
print("Berhasil! Cek file grafik_evaluasi_lengkap.png")