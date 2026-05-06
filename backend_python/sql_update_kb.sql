-- ============================================================
-- SQL UPDATE: Knowledge Base Enrichment AgriBot
-- Jalankan di MySQL untuk memperbarui kolom gejala
-- Tabel: knowledge_base | Kolom: gejala
-- PENTING: Backup tabel terlebih dahulu sebelum menjalankan!
-- ============================================================

UPDATE knowledge_base
SET gejala = 'bayam cercospora bercak daun hijau bercak kecil pertumbuhan terhambat khas jamur bayem bayam bercak cercospora daun bercak coklat keabu gosong kering jamur bercak daun bolong'
WHERE penyakit = 'Bercak Daun Cercospora (Bayam)';

UPDATE knowledge_base
SET gejala = 'bayam cercospora daun kuning pertumbuhan lambat bercak khas menyebar bayem bayam bercak cercospora daun bercak coklat keabu gosong kering jamur bercak daun bolong'
WHERE penyakit = 'Bercak Daun Cercospora (Bayam)';

UPDATE knowledge_base
SET gejala = 'bayam cercospora bercak daun layu batang busuk infeksi jamur lanjut bayem bayam bercak cercospora daun bercak coklat keabu gosong kering jamur bercak daun bolong'
WHERE penyakit = 'Bercak Daun Cercospora (Bayam)';

UPDATE knowledge_base
SET gejala = 'bayam cercospora daun kuning batang busuk infeksi berat bercak meluas bayem bayam bercak cercospora daun bercak coklat keabu gosong kering jamur bercak daun bolong'
WHERE penyakit = 'Bercak Daun Cercospora (Bayam)';

UPDATE knowledge_base
SET gejala = 'cabai terdapat bercak pada daun daun mengalami kelayuan pertumbuhan tanaman terhambat cabe cabai akar busuk busuk akar phytophthora benyek oyot membusuk berair layu mendadak akar membusuk batang coklat'
WHERE penyakit = 'Busuk Akar Phytophthora (Cabai)';

UPDATE knowledge_base
SET gejala = 'cabai daun tetap hijau terdapat bercak pada daun daun mengalami kelayuan batang mengalami pembusukan pertumbuhan tanaman terhambat cabe cabai akar busuk busuk akar phytophthora benyek oyot membusuk berair layu mendadak akar membusuk batang coklat'
WHERE penyakit = 'Busuk Akar Phytophthora (Cabai)';

UPDATE knowledge_base
SET gejala = 'cabai daun tetap hijau pertumbuhan tanaman terhambat cabe cabai akar busuk busuk akar phytophthora benyek oyot membusuk berair layu mendadak akar membusuk batang coklat'
WHERE penyakit = 'Busuk Akar Phytophthora (Cabai)';

UPDATE knowledge_base
SET gejala = 'cabai terdapat bercak pada daun daun mengalami kelayuan batang mengalami pembusukan cabe cabai akar busuk busuk akar phytophthora benyek oyot membusuk berair layu mendadak akar membusuk batang coklat'
WHERE penyakit = 'Busuk Akar Phytophthora (Cabai)';

UPDATE knowledge_base
SET gejala = 'kubis daun berwarna kuning terdapat bercak pada daun daun mengalami kelayuan kol kubis busuk lunak lonyot berlendir bacin bau busuk lendir daun kubis busuk'
WHERE penyakit = 'Busuk Lunak (Kubis)';

UPDATE knowledge_base
SET gejala = 'kubis terdapat bercak pada daun batang mengalami pembusukan kol kubis busuk lunak lonyot berlendir bacin bau busuk lendir daun kubis busuk'
WHERE penyakit = 'Busuk Lunak (Kubis)';

UPDATE knowledge_base
SET gejala = 'bawang merah ulat grayak daun berlubang bercak putih transparan jaringan rusak bawang merah brambang ulat grayak daun berlubang krowok bolong dimakan ulat bawang merah daun putus ulat hijau'
WHERE penyakit = 'Ulat Grayak (Bawang Merah)';

UPDATE knowledge_base
SET gejala = 'apel daun berlapis putih seperti tepung apel daun bedak putih tepung embun tepung bercak putih apel embun tepung daun apel'
WHERE penyakit = 'Embun Tepung (Apel)';

UPDATE knowledge_base
SET gejala = 'anggur lapisan putih seperti bedak di daun, batang, dan bunga. anggur daun bedak putih tepung embun tepung burik anggur embun tepung'
WHERE penyakit = 'Powdery Mildew (Embun Tepung) (Anggur)';

UPDATE knowledge_base
SET gejala = 'bawang daun berlubang tidak beraturan bawang daun ulat grayak'
WHERE penyakit = 'Ulat Grayak (Bawang Daun)';
