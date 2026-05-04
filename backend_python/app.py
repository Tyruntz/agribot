import warnings
warnings.filterwarnings("ignore")

from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from google import genai # <--- Pakai SDK Baru
import re
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# ==========================================
# 1. SETUP GEMINI API (VERSI TERBARU)
# ==========================================
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

# ==========================================
# 2. SETUP SASTRAWI
# ==========================================
stemmer = StemmerFactory().create_stemmer()
stopword = StopWordRemoverFactory().create_stop_word_remover()

def preprocess_text(text):
    text = re.sub(r'[^a-zA-Z\s]', '', text).lower()
    text = stopword.remove(text)
    text = stemmer.stem(text)
    return text

# ==========================================
# 3. KONEKSI DATABASE MYSQL
# ==========================================
def get_knowledge_base():
    try:
        conn = mysql.connector.connect(
	host="localhost",
    	user="agribot",
    	password="password_kuat_123",
    	database="db_pertanian"
	)
        df = pd.read_sql("SELECT * FROM knowledge_base", conn)
        conn.close()
        return df
    except Exception as e:
        print(f"❌ Error Database: {e}")
        return pd.DataFrame() # Return DataFrame kosong jika error

# ==========================================
# 4. GLOBAL INITIALIZATION (Dijalankan SEKALI saat server hidup)
# ==========================================
print("⏳ Memuat Knowledge Base dan membangun Model TF-IDF...")
global_df = get_knowledge_base()

if not global_df.empty:
    global_df['gejala_bersih'] = global_df['gejala'].apply(preprocess_text)
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(global_df['gejala_bersih'])
    print(f"✅ Knowledge Base ({len(global_df)} data) & Model TF-IDF siap!")
else:
    print("⚠️ PERINGATAN: Database kosong atau MySQL belum dinyalakan!")
    vectorizer = None
    tfidf_matrix = None

# Ambang batas skor kemiripan
THRESHOLD = 0.20 

# ==========================================
# 5. ROUTE API UTAMA
# ==========================================
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('pesan', '')

    if not user_message:
        return jsonify({'jawaban': 'Pesan kosong.'})

    # Cek apakah model berhasil dimuat saat startup
    if global_df.empty or vectorizer is None:
        return jsonify({'jawaban': 'Sistem sedang mengalami gangguan. Database Knowledge Base tidak tersedia.'})

    # PROSES LEBIH CEPAT: Langsung pakai model global yang sudah ada di memori
    user_message_clean = preprocess_text(user_message)
    user_vector = vectorizer.transform([user_message_clean])
    
    cosine_scores = cosine_similarity(user_vector, tfidf_matrix)
    
    max_score = cosine_scores.max()
    best_index = cosine_scores.argmax()

    # Logika Hybrid Fallback
    if max_score >= THRESHOLD:
        penyakit = global_df.iloc[best_index]['penyakit']
        solusi = global_df.iloc[best_index]['solusi']
        jawaban_final = f"**Berdasarkan database kami (Skor: {max_score:.2f}):**\nSepertinya tanaman Anda terkena **{penyakit}**.\n\n**Solusi:** {solusi}"
        sumber = "Lokal TF-IDF"
    else:
        try:
            prompt = f"Anda adalah pakar pertanian. Seorang petani bertanya: '{user_message}'. Berikan jawaban singkat, ramah, dan solutif khusus di bidang hama dan penyakit tanaman."
            
            # Memanggil Gemini API
            response = client.models.generate_content(
                model='gemini-2.5-flash', 
                contents=prompt
            )
            jawaban_final = f"**Berdasarkan Pakar AI (Gemini):**\n{response.text}"
            sumber = "Gemini API"
        except Exception as e:
            print("========== ERROR DARI GEMINI ==========")
            print(e) 
            print("=======================================")
            jawaban_final = "Maaf, sistem AI sedang sibuk atau API key bermasalah."
            sumber = "Error"

    return jsonify({
        'jawaban': jawaban_final,
        'sumber': sumber,
        'skor': float(max_score)
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
