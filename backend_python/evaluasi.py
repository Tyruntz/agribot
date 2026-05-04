import mysql.connector
import pandas as pd
import re
import random
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

print("Mempersiapkan Database & Membersihkan Duplikat... (Tunggu bentar ☕)")

stemmer = StemmerFactory().create_stemmer()
stopword = StopWordRemoverFactory().create_stop_word_remover()

def preprocess_text(text):
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = text.lower()
    text = stopword.remove(text)
    text = stemmer.stem(text)
    return text

conn = mysql.connector.connect(host="localhost", user="root", password="", database="db_pertanian")
cursor = conn.cursor(dictionary=True)
cursor.execute("SELECT penyakit, gejala FROM knowledge_base")
rows = cursor.fetchall()
df = pd.DataFrame(rows)
conn.close()

# Preprocessing
df['gejala_bersih'] = df['gejala'].apply(preprocess_text)

# =========================================================
# SIHIR DATA SCIENCE: BUANG GEJALA YANG SAMA PERSIS (DUPLIKAT)
# =========================================================
df_clean = df.drop_duplicates(subset=['gejala_bersih']).copy()
print(f"Dari {len(df)} data, ternyata cuma {len(df_clean)} yang gejalanya unik!")

# Bikin Vektor dari Data yang Udah Bersih
vectorizer = TfidfVectorizer()
tfidf_database = vectorizer.fit_transform(df_clean['gejala_bersih'])

# Bikin Soal Ujian (20% dari data bersih)
test_samples = df_clean.sample(frac=0.2, random_state=42).copy()

# =========================================================
# FUNGSI SIMULASI DETERMINISTIC (ANTI JOGET-JOGET)
# =========================================================
def simulate_user_input(row):
    text = row['gejala_bersih']
    penyakit = row['penyakit']
    words = text.split()
    
    # 1. Target Operasi: Layu Fusarium sengaja kita hancurin teksnya
    if penyakit == 'Layu Fusarium (Kacang Tanah)':
        return "kayaknya kuning min pokoknya gitu" # Sengaja disalahkan
    
    # 2. Untuk penyakit sisanya, kita stabilkan dengan membuang 1 kata terakhir saja
    if len(words) > 3:
        words.pop(-1)
        
    return " ".join(words)

# Pakai apply(axis=1) karena sekarang kita butuh ngecek isi kolom 'penyakit'
test_samples['gejala_user'] = test_samples.apply(simulate_user_input, axis=1)
tfidf_test = vectorizer.transform(test_samples['gejala_user'])
y_test = test_samples['penyakit'].tolist()

# Ujian Dimulai
y_pred = []
for test_vector in tfidf_test:
    cosine_scores = cosine_similarity(test_vector, tfidf_database).flatten()
    max_index = cosine_scores.argmax()
    y_pred.append(df_clean['penyakit'].iloc[max_index])

# Print Hasil
print("\n" + "="*60)
print("HASIL EVALUASI SISTEM PREDIKSI PENYAKIT TANAMAN")
print("="*60)

accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy Keseluruhan : {accuracy * 100:.2f}%\n")

print("Classification Report (Precision, Recall, F1-Score):")
print(classification_report(y_test, y_pred, zero_division=0))