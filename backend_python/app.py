import warnings
warnings.filterwarnings("ignore")

import os
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

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# ==========================================
# 1. SETUP GEMINI API
# ==========================================
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
client = genai.Client(api_key=GEMINI_API_KEY)

# ==========================================
# 2. SETUP SASTRAWI
# ==========================================
stemmer = StemmerFactory().create_stemmer()
stopword = StopWordRemoverFactory().create_stop_word_remover()

# ==========================================
# 3. KAMUS NORMALISASI SLANG (Layer 1)
#    Mengonversi kata dialek/slang petani
#    ke bentuk baku sebelum preprocessing
# ==========================================
SLANG_DICT = {
    # Sinonim komoditas
    'bayem': 'bayam', 'cabe': 'cabai', 'kol': 'kubis',
    'brambang': 'bawang merah',
    # Gejala slang → deskripsi baku
    'benyek': 'busuk berair membusuk akar busuk',
    'lonyot': 'busuk lunak membusuk berlendir',
    'bosok': 'busuk membusuk', 'bonyok': 'busuk membusuk',
    'oyot': 'akar akar busuk', 'godhong': 'daun', 'godhonge': 'daun',
    'krowok': 'berlubang bolong dimakan',
    'bolong': 'berlubang bolong dimakan',
    'gosong': 'bercak coklat kering gosong',
    'alum': 'layu', 'kuntet': 'kerdil pertumbuhan terhambat',
    'burik': 'bercak kasar',
    'bacin': 'berbau busuk menyengat',
    'bauk': 'berbau busuk', 'amis': 'berbau busuk',
    'ulet': 'ulat', 'uletnya': 'ulat',
    'bedak': 'tepung putih embun tepung',
    'ketumpahan': 'tertutup tepung putih',
    'bintik': 'bercak bintik',
    # Kata informal tanpa makna gejala (dihapus)
    'kyk': 'seperti', 'kek': 'seperti', 'gt': '',
    'pd': '', 'trus': '', 'tlg': '', 'gmn': '', 'knp': '',
    'kok': '', 'aing': '', 'kulo': '', 'min': '', 'bang': '', 'gan': '',
    'parah': 'parah berat', 'bgt': 'sangat',
    'sm': 'dan', 'jg': '', 'gak': 'tidak', 'mati': 'mati layu',
}

def normalize_slang(text):
    """Layer 1: Normalisasi slang/dialek petani ke kata baku."""
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    words = text.split()
    result = []
    for w in words:
        replacement = SLANG_DICT.get(w, w)
        if replacement:
            result.extend(replacement.split())
    return ' '.join(result)

def preprocess_text(text, use_slang=True):
    """Layer 2: Preprocessing standar (stopword + stemming)."""
    if use_slang:
        text = normalize_slang(text)
    else:
        text = re.sub(r'[^a-zA-Z\s]', '', str(text)).lower()
    text = stopword.remove(text)
    text = stemmer.stem(text)
    return text

# ==========================================
# 4. COMMODITY BOOST (Layer 5)
#    Naikkan skor TF-IDF jika komoditas
#    terdeteksi di query pengguna
# ==========================================
COMMODITY_KEYWORDS = {
    'bayam':        ['bayam', 'bayem'],
    'cabai':        ['cabai', 'cabe'],
    'kubis':        ['kubis', 'kol'],
    'bawang merah': ['bawang merah', 'brambang'],
    'anggur':       ['anggur'],
    'apel':         ['apel'],
}
COMMODITY_PENALTY = {
    # Jika user sebut "bawang merah", turunkan skor "bawang daun/putih"
    'bawang merah': ['bawang daun', 'bawang putih'],
}
BOOST_VALUE   = 0.30  # tambah skor jika komoditas match
PENALTY_VALUE = 0.20  # kurangi skor jika komoditas mirip tapi berbeda

def detect_commodity(raw_query):
    """Deteksi komoditas dari query mentah (sebelum preprocessing)."""
    raw_lower = raw_query.lower()
    # Cek frasa dua kata lebih dulu (lebih spesifik)
    if 'bawang merah' in raw_lower or 'brambang' in raw_lower:
        return 'bawang merah'
    for commodity, keywords in COMMODITY_KEYWORDS.items():
        for kw in keywords:
            if kw in raw_lower:
                return commodity
    return None

def is_commodity_in_kb(raw_query):
    """
    Cek apakah komoditas yang disebut user ada di KB.
    Kalau tidak ada → langsung fallback Gemini.
    Kalau tidak sebut komoditas apapun → biarkan TF-IDF jalan normal.
    """
    KB_COMMODITIES = [
        'bayam', 'bayem',
        'cabai', 'cabe',
        'kubis', 'kol',
        'bawang merah', 'brambang',
        'anggur',
        'apel',
    ]
    raw_lower = raw_query.lower()
    
    # Deteksi apakah user menyebut komoditas apapun
    ALL_COMMODITY_HINTS = [
        'bayam', 'bayem', 'cabai', 'cabe', 'kubis', 'kol',
        'bawang', 'brambang', 'anggur', 'apel',
        'singkong', 'tomat', 'jagung', 'padi', 'kopi', 'kakao',
        'pisang', 'mangga', 'jeruk', 'semangka', 'melon', 'wortel',
        'kentang', 'terong', 'timun', 'kangkung', 'sawi', 'seledri',
        'buncis', 'kacang', 'ubi', 'talas', 'jahe', 'kunyit',
    ]
    
    user_mentioned_commodity = any(hint in raw_lower for hint in ALL_COMMODITY_HINTS)
    
    # Kalau user tidak sebut komoditas apapun → biarkan TF-IDF jalan
    if not user_mentioned_commodity:
        return True
    
    # Kalau user sebut komoditas tapi bukan yang ada di KB → Gemini
    in_kb = any(c in raw_lower for c in KB_COMMODITIES)
    return in_kb

def apply_commodity_boost(scores, raw_query, df_kb, col_penyakit=None):
    """Terapkan boost/penalti berdasarkan komoditas yang terdeteksi."""
    detected = detect_commodity(raw_query)
    if not detected:
        return scores
    # Deteksi nama kolom otomatis jika tidak diberikan
    if col_penyakit is None:
        cols = {c.lower(): c for c in df_kb.columns}
        col_penyakit = cols.get('penyakit', df_kb.columns[0])
    for i, row in df_kb.iterrows():
        penyakit_lower = row[col_penyakit].lower()
        if detected in penyakit_lower:
            scores[i] = min(scores[i] + BOOST_VALUE, 1.0)
        if detected in COMMODITY_PENALTY:
            for penalti_komod in COMMODITY_PENALTY[detected]:
                if penalti_komod in penyakit_lower:
                    scores[i] = max(scores[i] - PENALTY_VALUE, 0.0)
    return scores

# ==========================================
# 5. KONEKSI DATABASE MYSQL
# ==========================================
def get_knowledge_base():
    try:
        conn = mysql.connector.connect(
            host=os.environ.get("DB_HOST","localhost"), user=os.environ.get("DB_USER","root"), password=os.environ.get("DB_PASS",""), database=os.environ.get("DB_NAME","db_pertanian")
        )
        df = pd.read_sql("SELECT * FROM knowledge_base", conn)
        conn.close()
        return df
    except Exception as e:
        print(f"❌ Error Database: {e}")
        return pd.DataFrame()

# ==========================================
# 6. ENRICHMENT KNOWLEDGE BASE (Layer 2)
#    Tambahkan sinonim slang ke teks gejala
#    agar TF-IDF mengenal kata dialek petani
# ==========================================
KB_ENRICHMENT = {
    'Bercak Daun Cercospora (Bayam)':
        ' bayem bayam bercak cercospora daun bercak coklat keabu gosong kering jamur bercak daun bolong',
    'Busuk Akar Phytophthora (Cabai)':
        ' cabe cabai akar busuk busuk akar phytophthora benyek oyot membusuk berair layu mendadak akar membusuk batang coklat',
    'Busuk Lunak (Kubis)':
        ' kol kubis busuk lunak lonyot berlendir bacin bau busuk lendir daun kubis busuk',
    'Ulat Grayak (Bawang Merah)':
        ' bawang merah brambang ulat grayak daun berlubang krowok bolong dimakan ulat bawang merah daun putus ulat hijau',
    'Embun Tepung (Apel)':
        ' apel daun bedak putih tepung embun tepung bercak putih apel embun tepung daun apel',
    'Powdery Mildew (Embun Tepung) (Anggur)':
        ' anggur daun bedak putih tepung embun tepung burik anggur embun tepung',
}

def enrich_knowledge_base(df):
    """Tambahkan kata slang ke kolom gejala di KB."""
    df_enriched = df.copy()
    for penyakit, tambahan in KB_ENRICHMENT.items():
        mask = df_enriched['Penyakit'].str.lower() == penyakit.lower()
        if mask.any():
            df_enriched.loc[mask, 'Gejala'] = df_enriched.loc[mask, 'Gejala'] + tambahan
        # Coba match case-insensitive partial
        else:
            mask2 = df_enriched['penyakit'].str.lower() == penyakit.lower()
            if mask2.any():
                df_enriched.loc[mask2, 'gejala'] = df_enriched.loc[mask2, 'gejala'] + tambahan
    return df_enriched

# ==========================================
# 7. GLOBAL INITIALIZATION
# ==========================================
print("⏳ Memuat Knowledge Base dan membangun Model TF-IDF...")
global_df_raw = get_knowledge_base()

if not global_df_raw.empty:
    # Deteksi nama kolom (case-insensitive)
    cols = {c.lower(): c for c in global_df_raw.columns}
    col_penyakit = cols.get('penyakit', 'penyakit')
    col_gejala   = cols.get('gejala', 'gejala')
    col_solusi   = cols.get('solusi', 'solusi')

    # Enrichment KB
    global_df = global_df_raw.copy()
    for penyakit_key, tambahan in KB_ENRICHMENT.items():
        mask = global_df[col_penyakit].str.lower() == penyakit_key.lower()
        if mask.any():
            global_df.loc[mask, col_gejala] = global_df.loc[mask, col_gejala] + tambahan

    # Preprocessing KB (tanpa slang normalisasi — KB sudah baku)
    global_df['gejala_bersih'] = global_df[col_gejala].apply(
        lambda x: preprocess_text(x, use_slang=False))

    # TF-IDF dengan bigram (Layer 3)
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
    tfidf_matrix = vectorizer.fit_transform(global_df['gejala_bersih'])
    print(f"✅ Knowledge Base ({len(global_df)} data) & Model TF-IDF Optimasi siap!")
    print(f"   Fitur TF-IDF: {tfidf_matrix.shape[1]} (unigram+bigram)")
else:
    print("⚠️ PERINGATAN: Database kosong atau MySQL belum dinyalakan!")
    vectorizer = None
    tfidf_matrix = None
    col_penyakit = col_gejala = col_solusi = None

# Threshold hybrid fallback
THRESHOLD = 0.20

# ==========================================
# 8. ROUTE API UTAMA
# ==========================================
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('pesan', '')

    if not user_message:
        return jsonify({'jawaban': 'Pesan kosong.'})

    if 'global_df' not in globals() or global_df is None or global_df.empty or vectorizer is None:
        return jsonify({'jawaban': 'Sistem sedang mengalami gangguan. Database Knowledge Base tidak tersedia.'})

    # Layer 1 + 2: Normalisasi slang + preprocessing query
    # Cek komoditas — kalau disebut tapi tidak ada di KB, langsung Gemini
    if not is_commodity_in_kb(user_message):
        try:
            prompt = (
                f"Anda adalah pakar pertanian. Seorang petani bertanya: '{user_message}'. "
                f"Berikan jawaban singkat, ramah, dan solutif khusus di bidang hama dan penyakit tanaman."
            )
            response = client.models.generate_content(
                model='gemini-2.5-flash', contents=prompt)
            return jsonify({
                'jawaban': f"**Berdasarkan Pakar AI (Gemini):**\n{response.text}",
                'sumber': 'Gemini API',
                'skor': 0.0
            })
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return jsonify({
                'jawaban': 'Maaf, sistem AI sedang sibuk atau API key bermasalah.',
                'sumber': 'Error',
                'skor': 0.0
            })

    # Layer 1 + 2: Normalisasi slang + preprocessing query
    user_message_clean = preprocess_text(user_message, use_slang=True)
    user_vector = vectorizer.transform([user_message_clean])

    # Layer 3 + 4: TF-IDF cosine similarity
    cosine_scores = cosine_similarity(user_vector, tfidf_matrix).flatten()

    # Layer 5: Commodity boost + penalti
    cosine_scores = apply_commodity_boost(cosine_scores, user_message, global_df, col_penyakit)

    max_score = cosine_scores.max()
    best_index = cosine_scores.argmax()

    # Logika Hybrid Fallback
    if max_score >= THRESHOLD:
        penyakit = global_df.iloc[best_index][col_penyakit]
        solusi   = global_df.iloc[best_index][col_solusi]
        jawaban_final = (
            f"**Berdasarkan database kami (Skor: {max_score:.2f}):**\n"
            f"Sepertinya tanaman Anda terkena **{penyakit}**.\n\n"
            f"**Solusi:** {solusi}"
        )
        sumber = "Lokal TF-IDF"
    else:
        try:
            prompt = (
                f"Anda adalah pakar pertanian. Jawab pertanyaan petani berikut dengan SINGKAT dan PADAT, "
                f"maksimal 3-4 kalimat saja. Langsung ke poin utama, tidak perlu pembuka panjang. "
                f"Fokus pada: nama penyakit/hama, penyebab, dan solusi praktis. "
                f"Pertanyaan petani: '{user_message}'"
            )
            response = client.models.generate_content(
                model='gemini-2.5-flash', contents=prompt, config={'max_output_tokens': 300})
            jawaban_final = f"**Berdasarkan Pakar AI (Gemini):**\n{response.text}"
            sumber = "Gemini API"
        except Exception as e:
            import traceback
            print(f"========== ERROR GEMINI ==========")
            print(traceback.format_exc())
            print(f"==================================")
            jawaban_final = "Maaf, sistem AI sedang sibuk atau API key bermasalah."
            sumber = "Error"

    return jsonify({
        'jawaban': jawaban_final,
        'sumber':  sumber,
        'skor':    float(max_score)
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
