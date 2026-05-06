"""
KODE 1: Preprocessing Pipeline AgriBot
======================================
Berisi semua fungsi preprocessing yang digunakan sistem:
- Normalisasi slang/dialek petani (Layer 1)
- Preprocessing teks standar: stopword + stemming (Layer 2)

Cara pakai:
    from preprocessing_pipeline import preprocess_text, normalize_slang
"""

import re
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

# ── Setup Sastrawi ────────────────────────────────────────────────────
stemmer  = StemmerFactory().create_stemmer()
stopword = StopWordRemoverFactory().create_stop_word_remover()

# ── Kamus Normalisasi Slang (40+ kata) ───────────────────────────────
# Mengonversi kata dialek/slang petani ke bentuk baku
# sebelum diproses oleh TF-IDF vectorizer.
SLANG_DICT = {
    # --- Sinonim Komoditas ---
    'bayem'     : 'bayam',
    'cabe'      : 'cabai',
    'kol'       : 'kubis',
    'brambang'  : 'bawang merah',

    # --- Gejala Slang → Deskripsi Baku ---
    'benyek'     : 'busuk berair membusuk akar busuk',
    'lonyot'     : 'busuk lunak membusuk berlendir',
    'bosok'      : 'busuk membusuk',
    'bonyok'     : 'busuk membusuk',
    'oyot'       : 'akar akar busuk',
    'godhong'    : 'daun',
    'godhonge'   : 'daun',
    'krowok'     : 'berlubang bolong dimakan',
    'bolong'     : 'berlubang bolong dimakan',
    'gosong'     : 'bercak coklat kering gosong',
    'alum'       : 'layu',
    'kuntet'     : 'kerdil pertumbuhan terhambat',
    'burik'      : 'bercak kasar',
    'bacin'      : 'berbau busuk menyengat',
    'bauk'       : 'berbau busuk',
    'amis'       : 'berbau busuk',
    'ulet'       : 'ulat',
    'uletnya'    : 'ulat',
    'bedak'      : 'tepung putih embun tepung',
    'ketumpahan' : 'tertutup tepung putih',
    'bintik'     : 'bercak bintik',
    'mati'       : 'mati layu',

    # --- Kata Informal Tanpa Makna Gejala (dihapus/disederhanakan) ---
    'kyk'  : 'seperti',
    'kek'  : 'seperti',
    'gt'   : '',
    'pd'   : '',
    'trus' : '',
    'tlg'  : '',
    'gmn'  : '',
    'knp'  : '',
    'kok'  : '',
    'aing' : '',
    'kulo' : '',
    'min'  : '',
    'bang' : '',
    'gan'  : '',
    'parah': 'parah berat',
    'bgt'  : 'sangat',
    'sm'   : 'dan',
    'jg'   : '',
    'gak'  : 'tidak',
}


def normalize_slang(text: str) -> str:
    """
    Layer 1: Normalisasi slang/dialek petani ke kata baku.
    Dipanggil SEBELUM stopword removal dan stemming.

    Args:
        text: Query mentah dari pengguna

    Returns:
        Teks yang sudah dinormalisasi

    Contoh:
        >>> normalize_slang("oyot cabe benyek")
        'akar akar busuk cabai busuk berair membusuk akar busuk'
    """
    text  = text.lower()
    text  = re.sub(r'[^a-zA-Z\s]', ' ', text)
    words = text.split()
    result = []
    for w in words:
        replacement = SLANG_DICT.get(w, w)
        if replacement:
            result.extend(replacement.split())
    return ' '.join(result)


def preprocess_text(text: str, use_slang: bool = True) -> str:
    """
    Layer 2: Preprocessing lengkap (opsional slang + stopword + stemming).

    Args:
        text      : Teks input (query pengguna atau gejala KB)
        use_slang : True untuk query pengguna, False untuk teks KB (sudah baku)

    Returns:
        Teks bersih siap divektorisasi TF-IDF

    Contoh:
        >>> preprocess_text("oyot cabe benyek", use_slang=True)
        'akar busuk cabai busuk berair'
        >>> preprocess_text("cabai akar membusuk layu", use_slang=False)
        'cabai akar busuk layu'
    """
    if use_slang:
        text = normalize_slang(text)
    else:
        text = re.sub(r'[^a-zA-Z\s]', '', str(text)).lower()
    text = stopword.remove(text)
    text = stemmer.stem(text)
    return text


if __name__ == '__main__':
    # Quick test
    test_queries = [
        "oyot cabe kulo benyek parah tlg",
        "min daun bayem bercak gosong kyk kebakar",
        "brambang krowok bolong dimakanin ulet",
        "kol lonyot bau bacin gmn ngatasinnya",
    ]
    print("=== Test Preprocessing Pipeline ===\n")
    for q in test_queries:
        hasil = preprocess_text(q, use_slang=True)
        print(f"Input : {q}")
        print(f"Output: {hasil}\n")
