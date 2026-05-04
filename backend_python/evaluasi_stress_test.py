import pandas as pd
import re
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import accuracy_score

# Inisialisasi Sastrawi
stemmer = StemmerFactory().create_stemmer()
stopword_remover = StopWordRemoverFactory().create_stop_word_remover()

def agribot_preprocessing(text):
    # 1. Case Folding
    text = text.lower()
    # 2. Cleansing (Hapus tanda baca & angka)
    text = re.sub(r'[^a-z\s]', '', text)
    # 3. Tokenizing (Otomatis saat split/join)
    # 4. Normalization (Contoh sederhana: ganti singkatan umum)
    text = re.sub(r'\bgmn\b', 'bagaimana', text)
    text = re.sub(r'\bkek\b', 'seperti', text)
    # 5. Stopword Removal
    text = stopword_remover.remove(text)
    # 6. Stemming
    text = stemmer.stem(text)
    return text

print("🌪️ MEMULAI SIMULASI STRESS TEST (V2 - FULL PREPROCESSING)...")

# Load Data
df_kb = pd.read_csv('dataset_agribot_final.csv')
df_test = pd.read_csv('stress_test.csv')

# Preprocessing Knowledge Base (Otak)
print("🧠 Preprocessing Knowledge Base...")
df_kb['Gejala_Clean'] = df_kb['Gejala'].apply(agribot_preprocessing)

# Build Model
vectorizer = TfidfVectorizer()
tfidf_matrix_kb = vectorizer.fit_transform(df_kb['Gejala_Clean'])

y_true = df_test['Target_Penyakit'].tolist()
y_pred = []

print("\n🔍 Mengevaluasi 30 Query Liar dengan Engine Baru...\n")
for i, query in enumerate(df_test['Query_User']):
    # Preprocessing input user (Fair Test!)
    clean_query = agribot_preprocessing(query)
    query_vec = vectorizer.transform([clean_query])
    
    similarity_scores = cosine_similarity(query_vec, tfidf_matrix_kb).flatten()
    best_idx = similarity_scores.argmax()
    tebakan = df_kb.iloc[best_idx]['Penyakit']
    y_pred.append(tebakan)
    
    status = "✅ BENAR" if tebakan == y_true[i] else "❌ SALAH"
    print(f"[{status}] Query: '{query}' -> Clean: '{clean_query}'")

# Final Result
akurasi = accuracy_score(y_true, y_pred) * 100
print(f"\n🎯 Akurasi Stress Test V2: {akurasi:.2f}%")