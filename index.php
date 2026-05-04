<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AgriBot - AI Konsultasi Pertanian</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary-dark: #10451D;
            --primary-main: #155D27;
            --primary-light: #1A7431;
            --bg-color: #F8FBF9;
            --text-main: #2D3748;
            --text-muted: #718096;
        }

        * {
            box-sizing: border-box;
        }

        body {
            font-family: 'Poppins', sans-serif;
            margin: 0;
            padding: 0;
            background-color: var(--bg-color);
            color: var(--text-main);
            overflow-x: hidden;
        }

        /* Navbar - Ultra Clean */
        .navbar {
            background-color: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 20px 10%;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: fixed;
            width: 100%;
            top: 0;
            z-index: 1000;
            box-shadow: 0 1px 2px rgba(0,0,0,0.03);
        }

        .logo {
            font-size: 22px;
            font-weight: 700;
            color: var(--primary-dark);
            text-decoration: none;
            letter-spacing: -0.5px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .nav-links a {
            text-decoration: none;
            color: var(--text-muted);
            margin-left: 30px;
            font-weight: 500;
            font-size: 15px;
            transition: all 0.3s ease;
        }

        .nav-links a:hover { 
            color: var(--primary-main); 
        }

        /* Hero Section - Premium Vibe */
        .hero {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            min-height: 90vh;
            padding: 120px 20px 60px;
            background: radial-gradient(circle at top, #E9F4ED 0%, var(--bg-color) 70%);
        }

        .hero-badge {
            background-color: #E6F2EA;
            color: var(--primary-main);
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 24px;
            letter-spacing: 0.5px;
        }

        .hero h1 {
            font-size: 52px;
            font-weight: 700;
            color: var(--primary-dark);
            margin: 0 0 20px;
            line-height: 1.2;
            letter-spacing: -1px;
        }

        .hero p {
            font-size: 18px;
            color: var(--text-muted);
            max-width: 600px;
            margin-bottom: 40px;
            line-height: 1.7;
            font-weight: 300;
        }

        /* CTA Button - Sleek Gradient */
        .btn-primary {
            background: linear-gradient(135deg, var(--primary-main) 0%, var(--primary-dark) 100%);
            color: white;
            padding: 16px 44px;
            border-radius: 50px;
            text-decoration: none;
            font-size: 16px;
            font-weight: 600;
            box-shadow: 0 10px 20px rgba(16, 69, 29, 0.15);
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
            border: 1px solid rgba(255,255,255,0.1);
        }

        .btn-primary:hover {
            transform: translateY(-4px);
            box-shadow: 0 15px 25px rgba(16, 69, 29, 0.25);
        }

        /* Features Section - Soft Cards */
        .features {
            display: flex;
            justify-content: center;
            gap: 30px;
            padding: 60px 10% 100px;
            background: var(--bg-color);
            flex-wrap: wrap;
        }

        .feature-card {
            flex: 1;
            min-width: 280px;
            text-align: left;
            padding: 40px 30px;
            border-radius: 24px;
            background: #ffffff;
            box-shadow: 0 10px 40px rgba(0,0,0,0.03);
            border: 1px solid rgba(0,0,0,0.02);
            transition: all 0.3s ease;
        }

        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.06);
        }

        .feature-icon-wrapper {
            width: 60px;
            height: 60px;
            background: #F0F7F2;
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
            margin-bottom: 24px;
        }

        .feature-card h3 { 
            color: var(--primary-dark);
            font-size: 20px;
            margin: 0 0 12px;
            font-weight: 600;
        }

        .feature-card p {
            color: var(--text-muted);
            font-size: 15px;
            line-height: 1.6;
            margin: 0;
        }

        /* Footer */
        .footer {
            text-align: center;
            padding: 30px;
            background: #ffffff;
            color: var(--text-muted);
            font-size: 14px;
            border-top: 1px solid #edf2f0;
        }
    </style>
</head>
<body>

    <nav class="navbar">
        <a href="#" class="logo">
            <span>🌱</span> AgriBot
        </a>
        <div class="nav-links">
            <a href="#">Beranda</a>
            <a href="#">Teknologi</a>
            <a href="#">Bantuan</a>
        </div>
    </nav>

    <section class="hero">
        <div class="hero-badge">AI-Powered NLP Engine</div>
        <h1>Solusi Cerdas AI untuk<br>Kesehatan Tanaman</h1>
        <p>Identifikasi hama dan penyakit tanaman secara presisi menggunakan teknologi TF-IDF yang didukung kecerdasan Generative AI.</p>
        <a href="konsultasi.php" class="btn-primary">Mulai Konsultasi</a>
    </section>

    <section class="features">
        <div class="feature-card">
            <div class="feature-icon-wrapper">⚡</div>
            <h3>Analisis Real-time</h3>
            <p>Pencocokan gejala menggunakan algoritma Cosine Similarity yang memberikan hasil diagnosis dalam hitungan detik.</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon-wrapper">🧠</div>
            <h3>Hybrid AI Engine</h3>
            <p>Sistem cerdas yang otomatis beralih ke pakar Gemini API jika permasalahan di luar cakupan basis data lokal.</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon-wrapper">📖</div>
            <h3>Data Tervalidasi</h3>
            <p>Solusi dan penanganan bersumber dari literatur dan basis pengetahuan pertanian yang akurat dan terpercaya.</p>
        </div>
    </section>

    <div class="footer">
        &copy; 2026 AgriBot NLP System. Developed for Academic Research. 
    </div>

</body>
</html>