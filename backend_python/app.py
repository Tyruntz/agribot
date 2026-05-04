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
from google import genai 
import re
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# ==========================================
# 1. SETUP GEMINI API
# ==========================================
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

# ==========================================
# 2. THE "SECRET WEAPONS" (NLP Data Structures)
# ==========================================
# A. Lexical Normalization (Translasi bahasa gaul/daerah petani)
slang_dict = {
    "godhong": "daun", "godong": "daun", "oyot": "akar", "kembang": "bunga", 
    "pang": "dahan", "rencek": "ranting", "bonggol": "batang", "pentil": "buah", 
    "benyek": "busuk", "lonyot": "busuk", "bosok": "busuk", "kresek": "hawar", 
    "bulai": "jamur putih", "kuntet": "kerdil", "macet": "kerdil", "alum": "layu", 
    "garing": "kering", "tugel": "patah", "gosong": "nekrosis", "item": "hitam", 
    "ireng": "hitam", "ijo": "hijau", "abang": "merah", "butek": "kusam", 
    "bolong": "lubang", "bercak2": "bercak", "bintik2": "bintik", "rontok": "gugur", 
    "keriting": "kerut", "grenjel": "bengkak", "benjol": "bengkak", "nyerang": "serang", 
    "nular": "tular", "obatin": "obati", "ngobatin": "obati", "nanem": "tanam"
}

# B. Noise Filtering (Sampah obrolan WA)
custom_stopwords = [
    "min", "bang", "dong", "gimana", "cara", "ngobatin", "obatnya", "kok", "kek", 
    "yg", "ya", "halo", "punten", "nanya", "wkwk", "wkwkwk", "terus", "ada", "bos", 
    "sih", "deh", "lho", "gan", "juragan", "pak", "bu", "tolong", "bantuannya", "nih"
]

# C. Semantic Expansion (Sinonim untuk nge-cheat skor Cosine Similarity)
expansion_dict = {
    "busuk": "busuk hancur basah berair lonyot benyek membusuk rusak daging",
    "bercak": "bercak bintik noda karat titik trotol blorok",
    "nekrosis": "nekrosis gosong hitam gelap mati jaringan terbakar",
    "kanker": "kanker luka pecah retak getah eksudasi",
    "hawar": "hawar kresek melepuh",
    "kerdil": "kerdil kerdilnya kecil lambat stunting macet kuntet hipoplastik",
    "layu": "layu alum lunglai lemah rebah lemas dehidrasi",
    "kering": "kering gersang kerontang mati",
    "klorosis": "klorosis kuning pucat etiolasi memudar",
    "bengkak": "bengkak benjol tumor puru gall hiperplastik cecidia",
    "kerut": "keriting keriput melengkung menggulung berkerut kusut",
    "gugur": "gugur rontok jatuh lepas luruh absisi",
    "patah": "patah rebah kecambah rapuh putus",
    "lubang": "lubang bolong tembus keropos dimakan sobek",
    "jamur": "jamur kapang cendawan putih tepung spora",
    "hama": "hama ulat serangga kutu tungau wereng walang kumbang",
    "embun": "embun bulu tepung berbulu putih",
    "antraknosa": "antraknosa patek colletotrichum",
    "pucat": "pucat putih terang memudar etiolasi"
}

# ==========================================
# 3. SETUP SASTRAWI & MASTER STOPWORDS
# ==========================================
stemmer = StemmerFactory().create_stemmer()
# Ambil list bawaan Sastrawi, lalu gabung sama custom_stopwords buatan kita
sastrawi_stopword_list = StopWordRemoverFactory().get_stop_words()
master_stopwords = set(sastrawi_stopword_list + custom_stopwords)

# ==========================================
# 4. THE ULTIMATE PREPROCESSING PIPELINE
# ==========================================
def preprocess_text(text):
    # Step 1: Regex Cleansing (Lowercase & hapus tanda baca)
    text = re.sub(r'[^a-zA-Z\s]', '', text).lower()
    
    # Step 2: Tokenization
    tokens = text.split()
    
    # Step 3: Noise Filtering (Buang stopword & kata sapaan WA)
    tokens = [word for word in tokens if word not in master_stopwords]
    
    # Step 4: Lexical Normalization (Translate dialek/slang ke bahasa baku)
    normalized_tokens = [slang_dict.get(word, word) for word in tokens]
    
    # Step 5: Stemming Sastrawi (Kembalikan ke kata dasar)
    text_joined = " ".join(normalized_tokens)
    stemmed_text = stemmer.stem(text_joined)
    
    # Step 6: Semantic Query Expansion (Suntik sinonim)
    stemmed_tokens = stemmed_text.split()
    expanded_tokens = []
    for word in stemmed_tokens:
        expanded_tokens.append(word)
        if word in expansion_dict:
            # Masukin semua sinonimnya ke dalam array
            expanded_tokens.extend(expansion_dict[word].split())
            
    return " ".join(expanded_tokens)

# ==========================================
# 5. KONEKSI DATABASE MYSQL
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
        return pd.DataFrame() 

# ==========================================
# 6. GLOBAL INITIALIZATION 
# ==========================================
print("⏳ Memuat Knowledge Base dan membangun Model TF-IDF...")
global_df = get_knowledge_base()

if not global_df.empty:
    global_df['gejala_bersih'] = global_df['gejala'].apply(preprocess_text)
    # TF-IDF BUFF: Tambahin ngram_range=(1,2) biar paham konteks dua kata (contoh: "busuk akar")
    vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    tfidf_matrix = vectorizer.fit_transform(global_df['gejala_bersih'])
    print(f"✅ Knowledge Base ({len(global_df)} data) & Model TF-IDF siap!")
else:
    print("⚠️ PERINGATAN: Database kosong atau MySQL belum dinyalakan!")
    vectorizer = None
    tfidf_matrix = None

# Ambang batas skor kemiripan
THRESHOLD = 0.20 

# ==========================================
# 7. ROUTE API UTAMA
# ==========================================
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('pesan', '')

    if not user_message:
        return jsonify({'jawaban': 'Pesan kosong.'})

    if global_df.empty or vectorizer is None:
        return jsonify({'jawaban': 'Sistem sedang mengalami gangguan. Database Knowledge Base tidak tersedia.'})

    user_message_clean = preprocess_text(user_message)
    user_vector = vectorizer.transform([user_message_clean])
    
    cosine_scores = cosine_similarity(user_vector, tfidf_matrix)
    
    max_score = cosine_scores.max()
    best_index = cosine_scores.argmax()

    if max_score >= THRESHOLD:
        penyakit = global_df.iloc[best_index]['penyakit']
        solusi = global_df.iloc[best_index]['solusi']
        jawaban_final = f"**Berdasarkan database kami (Skor: {max_score:.2f}):**\nSepertinya tanaman Anda terkena **{penyakit}**.\n\n**Solusi:** {solusi}"
        sumber = "Lokal TF-IDF"
    else:
        try:
            prompt = f"Anda adalah pakar pertanian. Seorang petani bertanya: '{user_message}'. Berikan jawaban singkat, ramah, dan solutif khusus di bidang hama dan penyakit tanaman."
            
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