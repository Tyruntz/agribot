<?php
session_start();
$ADMIN_USER = "admin";
$ADMIN_PASS = "agribot2026";
if (isset($_POST["login"])) {
    if ($_POST["username"] === $ADMIN_USER && $_POST["password"] === $ADMIN_PASS) {
        $_SESSION["logged_in"] = true;
    } else {
        $login_error = "Username atau password salah!";
    }
}
if (isset($_GET["logout"])) {
    session_destroy();
    header("Location: admin.php");
    exit;
}
if (!isset($_SESSION["logged_in"]) || !$_SESSION["logged_in"]) {
    echo "<!DOCTYPE html><html><head><meta charset=UTF-8><title>Login Admin AgriBot</title><style>*{box-sizing:border-box;margin:0;padding:0}body{font-family:sans-serif;background:#f0fdf4;display:flex;align-items:center;justify-content:center;height:100vh}.card{background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:40px;width:360px}h2{color:#15803d;margin-bottom:24px}label{font-size:13px;color:#475569;display:block;margin-bottom:6px}input{width:100%;padding:10px 12px;border:1px solid #e2e8f0;border-radius:8px;font-size:14px;margin-bottom:16px}button{width:100%;padding:11px;background:#16a34a;color:#fff;border:none;border-radius:8px;font-size:14px;font-weight:600;cursor:pointer}.error{color:#dc2626;font-size:13px;margin-bottom:16px}</style></head><body><div class=card><h2>Admin AgriBot</h2>";
    if (isset($login_error)) echo "<div class=error>".$login_error."</div>";
    echo "<form method=POST><label>Username</label><input type=text name=username required><label>Password</label><input type=password name=password required><button type=submit name=login>Masuk</button></form></div></body></html>";
    exit;
}

$host = "localhost";
$user = "agribot";
$pass = "password_kuat_123";
$db   = "db_pertanian";

$conn = new mysqli($host, $user, $pass, $db);
if ($conn->connect_error) {
    die("Koneksi gagal: " . $conn->connect_error);
}

if (isset($_POST['tambah'])) {
    $penyakit = $conn->real_escape_string($_POST['penyakit']);
    $gejala   = $conn->real_escape_string($_POST['gejala']);
    $solusi   = $conn->real_escape_string($_POST['solusi']);
    $sql = "INSERT INTO knowledge_base (penyakit, gejala, solusi) VALUES ('$penyakit', '$gejala', '$solusi')";
    $conn->query($sql);
    header("Location: admin.php?status=success");
    exit;
}

if (isset($_POST['import_csv'])) {
    if ($_FILES['file_csv']['size'] > 0) {
        $file   = $_FILES['file_csv']['tmp_name'];
        $handle = fopen($file, "r");
        $is_header = true;
        $imported = 0;
        while (($data = fgetcsv($handle, 10000, ",")) !== FALSE) {
            if ($is_header) { $is_header = false; continue; }
            $penyakit = $conn->real_escape_string($data[0]);
            $gejala   = $conn->real_escape_string($data[1]);
            $solusi   = $conn->real_escape_string($data[2]);
            if (!empty($penyakit) && !empty($gejala)) {
                $conn->query("INSERT INTO knowledge_base (penyakit, gejala, solusi) VALUES ('$penyakit', '$gejala', '$solusi')");
                $imported++;
            }
        }
        fclose($handle);
        header("Location: admin.php?status=import_success&count=$imported");
        exit;
    }
}

if (isset($_GET['hapus'])) {
    $id = (int)$_GET['hapus'];
    $conn->query("DELETE FROM knowledge_base WHERE id=$id");
    header("Location: admin.php?status=deleted");
    exit;
}

$result      = $conn->query("SELECT * FROM knowledge_base ORDER BY id DESC");
$count_result = $conn->query("SELECT COUNT(*) AS total FROM knowledge_base");
$row_count   = $count_result->fetch_assoc();
$total_data  = $row_count['total'];

$unique_result = $conn->query("SELECT COUNT(DISTINCT penyakit) AS unique_count FROM knowledge_base");
$unique_row    = $unique_result->fetch_assoc();
$unique_count  = $unique_row["unique_count"];
?>
<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Admin Panel · AgriBot</title>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --green-50:#f0fdf4;--green-100:#dcfce7;--green-200:#bbf7d0;--green-300:#86efac;
  --green-500:#22c55e;--green-600:#16a34a;--green-700:#15803d;--green-900:#14532d;
  --slate-50:#f8fafc;--slate-100:#f1f5f9;--slate-200:#e2e8f0;--slate-300:#cbd5e1;
  --slate-400:#94a3b8;--slate-500:#64748b;--slate-600:#475569;--slate-700:#334155;
  --slate-800:#1e293b;--slate-900:#0f172a;
  --red-50:#fef2f2;--red-200:#fecaca;--red-500:#ef4444;--red-600:#dc2626;
  --amber-50:#fffbeb;--amber-200:#fde68a;--amber-600:#d97706;
  --radius:10px;--radius-sm:6px;
}
body{font-family:'Plus Jakarta Sans',sans-serif;background:var(--slate-50);color:var(--slate-800);font-size:14px;line-height:1.5;display:flex;min-height:100vh}

/* ── SIDEBAR ── */
.sidebar{width:240px;background:#fff;border-right:1px solid var(--slate-200);display:flex;flex-direction:column;position:fixed;height:100vh;z-index:50}
.brand{padding:20px 20px 16px;border-bottom:1px solid var(--slate-100)}
.brand-logo{display:flex;align-items:center;gap:10px}
.brand-icon{width:34px;height:34px;background:var(--green-600);border-radius:8px;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.brand-icon svg{width:18px;height:18px;fill:white}
.brand-name{font-size:15px;font-weight:700;color:var(--slate-900)}
.brand-sub{font-size:11px;color:var(--slate-400);font-family:'JetBrains Mono',monospace;margin-top:1px}
.nav{padding:14px 12px;flex:1;overflow-y:auto}
.nav-label{font-size:10px;font-weight:700;color:var(--slate-400);letter-spacing:.08em;text-transform:uppercase;padding:0 8px 6px;display:block}
.nav-item{display:flex;align-items:center;gap:10px;padding:9px 10px;border-radius:var(--radius-sm);color:var(--slate-500);font-weight:500;font-size:13px;margin-bottom:2px;text-decoration:none;transition:all .15s}
.nav-item:hover{background:var(--slate-50);color:var(--slate-800)}
.nav-item.active{background:var(--green-50);color:var(--green-700);font-weight:600}
.nav-item svg{width:15px;height:15px;flex-shrink:0}
.nav-section{margin-top:16px}
.sidebar-footer{padding:14px 16px;border-top:1px solid var(--slate-100)}
.status-pill{display:flex;align-items:center;gap:8px;background:var(--green-50);border:1px solid var(--green-200);border-radius:20px;padding:7px 14px}
.dot{width:7px;height:7px;background:var(--green-500);border-radius:50%;box-shadow:0 0 0 2px var(--green-200);flex-shrink:0}
.status-text{font-size:12px;color:var(--green-700);font-weight:600}

/* ── MAIN ── */
.main{margin-left:240px;flex:1;display:flex;flex-direction:column;min-height:100vh}
.topbar{background:#fff;border-bottom:1px solid var(--slate-200);padding:14px 28px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:40}
.topbar-title{font-size:16px;font-weight:700;color:var(--slate-900)}
.topbar-sub{font-size:12px;color:var(--slate-400);margin-top:1px}
.badge-records{background:var(--green-50);color:var(--green-700);border:1px solid var(--green-200);padding:5px 14px;border-radius:20px;font-size:12px;font-weight:700;font-family:'JetBrains Mono',monospace}
.content{padding:24px 28px}

/* ── ALERTS ── */
.alert{border-radius:var(--radius);padding:12px 16px;display:flex;align-items:center;gap:10px;margin-bottom:20px;font-size:13px;font-weight:500}
.alert-success{background:var(--green-50);border:1px solid var(--green-200);color:var(--green-700)}
.alert-deleted{background:#fff7ed;border:1px solid #fed7aa;color:#c2410c}
.alert-icon{width:20px;height:20px;border-radius:50%;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.alert-success .alert-icon{background:var(--green-600)}
.alert-deleted .alert-icon{background:#ea580c}
.alert-icon svg{width:11px;height:11px;fill:white}

/* ── METRICS ── */
.metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:22px}
.metric-card{background:#fff;border:1px solid var(--slate-200);border-radius:var(--radius);padding:18px 20px}
.metric-card.green{border-color:var(--green-200);background:var(--green-50)}
.metric-label{font-size:11px;font-weight:700;color:var(--slate-400);text-transform:uppercase;letter-spacing:.06em;margin-bottom:10px}
.metric-value{font-size:28px;font-weight:700;color:var(--slate-900);font-family:'JetBrains Mono',monospace;line-height:1}
.metric-card.green .metric-value{color:var(--green-700)}
.metric-engine{display:flex;align-items:center;gap:8px;font-size:14px;font-weight:700;color:var(--slate-800);margin-top:4px}
.metric-sub{font-size:12px;color:var(--slate-400);margin-top:6px}
.metric-sub b{color:var(--green-600);font-weight:600}

/* ── FORM GRID ── */
.form-row{display:grid;grid-template-columns:1.1fr .9fr;gap:16px;margin-bottom:20px}
.panel{background:#fff;border:1px solid var(--slate-200);border-radius:var(--radius);overflow:hidden}
.panel-head{padding:14px 18px;border-bottom:1px solid var(--slate-100);display:flex;align-items:center;gap:10px}
.panel-head-icon{width:26px;height:26px;background:var(--slate-100);border-radius:6px;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.panel-head-icon svg{width:13px;height:13px;stroke:var(--slate-500);fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
.panel-head-text{font-size:13px;font-weight:600;color:var(--slate-700)}
.panel-body{padding:20px}
.form-group{margin-bottom:15px}
.form-label{font-size:12px;font-weight:600;color:var(--slate-600);display:block;margin-bottom:5px}
.form-hint{font-size:11px;color:var(--slate-400);margin-top:4px}
input[type=text],textarea{width:100%;padding:9px 12px;border:1px solid var(--slate-200);border-radius:var(--radius-sm);font-family:'Plus Jakarta Sans',sans-serif;font-size:13px;color:var(--slate-800);background:#fff;transition:border-color .15s,box-shadow .15s;resize:vertical}
input[type=text]:focus,textarea:focus{outline:none;border-color:var(--green-500);box-shadow:0 0 0 3px rgba(34,197,94,.12)}
textarea{min-height:76px}
input::placeholder,textarea::placeholder{color:var(--slate-300)}
.btn{padding:10px 16px;border-radius:var(--radius-sm);font-family:'Plus Jakarta Sans',sans-serif;font-size:13px;font-weight:600;cursor:pointer;transition:all .15s;display:inline-flex;align-items:center;justify-content:center;gap:7px;width:100%}
.btn svg{width:14px;height:14px;flex-shrink:0}
.btn-primary{background:var(--green-600);color:#fff;border:none}
.btn-primary:hover{background:var(--green-700)}
.btn-primary svg{stroke:#fff;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
.btn-outline{background:#fff;color:var(--green-700);border:1.5px solid var(--green-300)}
.btn-outline:hover{background:var(--green-50)}
.btn-outline svg{stroke:var(--green-700);fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}

/* ── IMPORT ZONE ── */
.import-zone{border:1.5px dashed var(--slate-300);border-radius:var(--radius-sm);padding:20px;text-align:center;background:var(--slate-50);margin-bottom:14px;cursor:pointer;transition:all .2s}
.import-zone:hover{border-color:var(--green-400);background:var(--green-50)}
.import-zone-icon{width:36px;height:36px;background:var(--slate-200);border-radius:8px;display:flex;align-items:center;justify-content:center;margin:0 auto 10px}
.import-zone-icon svg{width:18px;height:18px;stroke:var(--slate-500);fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
.import-zone p{font-size:12px;color:var(--slate-500);margin-bottom:6px;font-weight:500}
.import-zone code{font-size:11px;font-family:'JetBrains Mono',monospace;background:#fff;border:1px solid var(--slate-200);padding:2px 7px;border-radius:4px;color:var(--slate-600)}
.file-label-btn{display:inline-flex;align-items:center;gap:6px;background:#fff;border:1px solid var(--slate-200);border-radius:var(--radius-sm);padding:6px 14px;font-size:12px;font-weight:600;color:var(--slate-600);cursor:pointer;margin-top:10px;transition:all .15s}
.file-label-btn:hover{border-color:var(--green-400);color:var(--green-700)}
.file-label-btn svg{width:12px;height:12px;stroke:currentColor;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
input[type=file]{display:none}
.file-selected{font-size:12px;color:var(--green-700);font-weight:600;margin-top:6px;display:none}
.warning-box{background:var(--amber-50);border:1px solid var(--amber-200);border-radius:var(--radius-sm);padding:10px 14px;margin-bottom:14px}
.warning-title{font-size:11px;font-weight:700;color:var(--amber-600);margin-bottom:3px}
.warning-text{font-size:11px;color:var(--amber-600)}

/* ── TABLE PANEL ── */
.table-panel{background:#fff;border:1px solid var(--slate-200);border-radius:var(--radius);overflow:hidden}
.table-head-row{padding:14px 18px;border-bottom:1px solid var(--slate-100);display:flex;align-items:center;justify-content:space-between;gap:12px}
.table-head-left{display:flex;align-items:center;gap:10px}
.table-title{font-size:13px;font-weight:600;color:var(--slate-700)}
.table-count{font-size:12px;color:var(--slate-400);font-family:'JetBrains Mono',monospace}
.search-box{display:flex;align-items:center;gap:8px;background:var(--slate-50);border:1px solid var(--slate-200);border-radius:var(--radius-sm);padding:7px 11px}
.search-box svg{width:13px;height:13px;stroke:var(--slate-400);fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;flex-shrink:0}
.search-box input{border:none;background:transparent;font-size:13px;color:var(--slate-700);font-family:'Plus Jakarta Sans',sans-serif;outline:none;width:200px}
.search-box input::placeholder{color:var(--slate-300)}
.table-wrapper{overflow-x:auto}
table{width:100%;border-collapse:collapse}
th{padding:10px 16px;text-align:left;font-size:11px;font-weight:700;color:var(--slate-400);text-transform:uppercase;letter-spacing:.06em;background:var(--slate-50);border-bottom:1px solid var(--slate-100);white-space:nowrap}
td{padding:13px 16px;border-bottom:1px solid var(--slate-100);vertical-align:middle;font-size:13px}
tr:last-child td{border-bottom:none}
tr:hover td{background:var(--slate-50)}
.id-badge{font-family:'JetBrains Mono',monospace;font-size:11px;background:var(--slate-100);color:var(--slate-500);padding:3px 7px;border-radius:4px;font-weight:500}
.disease-name{font-weight:600;color:var(--green-700)}
.gejala-text{font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--slate-400);max-width:240px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;display:block}
.solusi-text{color:var(--slate-500);font-size:12px;max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;display:block}
.btn-drop{background:transparent;border:1px solid var(--red-200);color:var(--red-600);padding:5px 12px;border-radius:var(--radius-sm);font-size:12px;font-weight:600;cursor:pointer;transition:all .15s;font-family:'Plus Jakarta Sans',sans-serif;white-space:nowrap}
.btn-drop:hover{background:var(--red-50);border-color:var(--red-500)}
.empty-state{text-align:center;padding:48px 20px;color:var(--slate-300)}
.empty-state svg{width:36px;height:36px;stroke:var(--slate-200);fill:none;stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round;margin:0 auto 10px;display:block}
.empty-state p{font-size:13px}
.table-footer{padding:12px 18px;border-top:1px solid var(--slate-100);font-size:12px;color:var(--slate-400);display:flex;align-items:center;justify-content:space-between;background:var(--slate-50)}
</style>
</head>
<body>

<div class="sidebar">
  <div class="brand">
    <div class="brand-logo">
      <div class="brand-icon">
        <svg viewBox="0 0 20 20"><path d="M10 2C5.58 2 2 5.58 2 10s3.58 8 8 8 8-3.58 8-8-3.58-8-8-8zm0 3c1.1 0 2 .9 2 2s-.9 2-2 2-2-.9-2-2 .9-2 2-2zm0 10.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/></svg>
      </div>
      <div>
        <div class="brand-name">AgriBot</div>
        <div class="brand-sub">admin · v2.0</div>
      </div>
    </div>
  </div>

  <div class="nav">
    <span class="nav-label">Panel Utama</span>
    <a href="admin.php" class="nav-item active">
      <svg viewBox="0 0 16 16" fill="currentColor"><path d="M2 2h5v5H2V2zm7 0h5v5H9V2zM2 9h5v5H2V9zm7 0h5v5H9V9z"/></svg>
      Dashboard
    </a>
    <a href="index.php" target="_blank" class="nav-item">
      <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M8 3H3a1 1 0 00-1 1v9a1 1 0 001 1h10a1 1 0 001-1V8M10 2h4v4M14 2L8 8"/></svg>
      Lihat Chatbot
    </a>
    <div class="nav-section">
      <span class="nav-label">Knowledge Base</span>
      <a href="#form-manual" class="nav-item">
        <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="8" cy="8" r="6"/><path d="M8 5v6M5 8h6"/></svg>
        Tambah Data Manual
      </a>
      <a href="#import-csv" class="nav-item">
        <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M8 10V3M5 7l3 3 3-3M2 13h12"/></svg>
        Import Batch CSV
      </a>
      <a href="#tabel-data" class="nav-item">
        <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><rect x="1" y="1" width="14" height="14" rx="2"/><path d="M1 6h14M6 6v8"/></svg>
        Lihat Semua Data
      </a>
<a href="admin.php?logout=1" class="nav-item" style="color:#ef4444">
    <svg viewBox="0 0 16 16" fill="currentColor"><path d="M6 2H3a1 1 0 00-1 1v10a1 1 0 001 1h3M10 5l3 3-3 3M13 8H6"/></svg>
    Logout
</a>
    </div>
  </div>

  <div class="sidebar-footer">
    <div class="status-pill">
      <div class="dot"></div>
      <div class="status-text">Hybrid Engine Aktif</div>
    </div>
  </div>
</div>

<div class="main">
  <div class="topbar">
    <div>
      <div class="topbar-title">Dataset Control Panel</div>
      <div class="topbar-sub">Kelola knowledge base dan konfigurasi algoritma TF-IDF</div>
    </div>
    <span class="badge-records"><?= $total_data ?> records</span>
  </div>

  <div class="content">

    <?php if(isset($_GET['status'])): ?>
      <?php if($_GET['status'] === 'success'): ?>
        <div class="alert alert-success">
          <div class="alert-icon"><svg viewBox="0 0 11 11"><polyline points="2,5.5 4.5,8 9,3" stroke="white" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg></div>
          Data baru berhasil ditambahkan ke knowledge base.
        </div>
      <?php elseif($_GET['status'] === 'import_success'): ?>
        <div class="alert alert-success">
          <div class="alert-icon"><svg viewBox="0 0 11 11"><polyline points="2,5.5 4.5,8 9,3" stroke="white" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg></div>
          Import berhasil — <strong><?= (int)$_GET['count'] ?> baris data</strong> telah dimasukkan ke dalam model NLP.
        </div>
      <?php elseif($_GET['status'] === 'deleted'): ?>
        <div class="alert alert-deleted">
          <div class="alert-icon"><svg viewBox="0 0 11 11"><line x1="2" y1="2" x2="9" y2="9" stroke="white" stroke-width="1.5" stroke-linecap="round"/><line x1="9" y1="2" x2="2" y2="9" stroke="white" stroke-width="1.5" stroke-linecap="round"/></svg></div>
          Record berhasil dihapus dari knowledge base.
        </div>
      <?php endif; ?>
    <?php endif; ?>

    <div class="metrics">
      <div class="metric-card">
        <div class="metric-label">Total Records</div>
        <div class="metric-value"><?= $total_data ?></div>
        <div class="metric-sub"><b><?= $unique_count ?></b> penyakit unik terdaftar</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Engine Status</div>
        <div class="metric-engine"><span class="dot"></span>HYBRID_ACTIVE</div>
        <div class="metric-sub">TF-IDF + <b>Gemini</b> online</div>
      </div>
      <div class="metric-card green">
        <div class="metric-label">TF-IDF F1-Score</div>
        <div class="metric-value">0.9152</div>
        <div class="metric-sub">Weighted Average · <b>91.52%</b></div>
      </div>
    </div>

    <div class="form-row">
      <div class="panel" id="form-manual">
        <div class="panel-head">
          <div class="panel-head-icon">
            <svg viewBox="0 0 14 14"><circle cx="7" cy="7" r="5"/><path d="M7 4v6M4 7h6"/></svg>
          </div>
          <div class="panel-head-text">Tambah Data Manual</div>
        </div>
        <div class="panel-body">
          <form method="POST" action="">
            <div class="form-group">
              <label class="form-label">Nama Penyakit / Hama</label>
              <input type="text" name="penyakit" placeholder="Contoh: Busuk Lunak (Kubis)" required>
              <div class="form-hint">Format: Nama Penyakit (Komoditas)</div>
            </div>
            <div class="form-group">
              <label class="form-label">Deskripsi Gejala</label>
              <textarea name="gejala" placeholder="Contoh: daun menguning layu batang busuk berair..." required></textarea>
              <div class="form-hint">Kata kunci gejala untuk ekstraksi fitur TF-IDF</div>
            </div>
            <div class="form-group">
              <label class="form-label">Solusi Penanganan</label>
              <textarea name="solusi" placeholder="Contoh: 1. Cabut tanaman terinfeksi..." required></textarea>
              <div class="form-hint">Mendukung format Markdown untuk tampilan chatbot</div>
            </div>
            <button type="submit" name="tambah" class="btn btn-primary">
              <svg viewBox="0 0 14 14"><circle cx="7" cy="7" r="5"/><path d="M7 4v6M4 7h6"/></svg>
              Simpan ke Knowledge Base
            </button>
          </form>
        </div>
      </div>

      <div class="panel" id="import-csv">
        <div class="panel-head">
          <div class="panel-head-icon">
            <svg viewBox="0 0 14 14"><path d="M7 10V3M4 7l3 3 3-3M2 12h10"/></svg>
          </div>
          <div class="panel-head-text">Import Batch CSV</div>
        </div>
        <div class="panel-body">
          <form method="POST" action="" enctype="multipart/form-data">
            <div class="import-zone" onclick="document.getElementById('csvfile').click()">
              <div class="import-zone-icon">
                <svg viewBox="0 0 18 18"><path d="M9 12V4M5 8l4-4 4 4M2 15h14"/></svg>
              </div>
              <p>Klik untuk pilih file CSV</p>
              <code>Penyakit, Gejala, Solusi</code>
              <label class="file-label-btn" onclick="event.stopPropagation();" for="csvfile">
                <svg viewBox="0 0 12 12"><path d="M6 8V2M3 5l3-3 3 3M1 10h10"/></svg>
                Pilih File
              </label>
              <div class="file-selected" id="file-selected-name"></div>
            </div>
            <input type="file" id="csvfile" name="file_csv" accept=".csv" onchange="showFileName(this)">
            <div class="warning-box">
              <div class="warning-title">Perhatian</div>
              <div class="warning-text">Pastikan header CSV sesuai format. Baris pertama (header) akan dilewati otomatis oleh sistem.</div>
            </div>
            <button type="submit" name="import_csv" class="btn btn-outline">
              <svg viewBox="0 0 14 14"><path d="M7 10V3M4 7l3 3 3-3M2 12h10"/></svg>
              Eksekusi Import Batch
            </button>
          </form>
        </div>
      </div>
    </div>

    <div class="table-panel" id="tabel-data">
      <div class="table-head-row">
        <div class="table-head-left">
          <div class="panel-head-icon">
            <svg viewBox="0 0 14 14"><rect x="1" y="1" width="12" height="12" rx="2"/><path d="M1 5h12M5 5v8"/></svg>
          </div>
          <div class="table-title">Knowledge Base</div>
          <span class="table-count"><?= $total_data ?> entries</span>
        </div>
        <div class="search-box">
          <svg viewBox="0 0 14 14"><circle cx="6" cy="6" r="4"/><path d="M14 14l-3.5-3.5"/></svg>
          <input type="text" id="search-input" placeholder="Cari penyakit atau gejala..." oninput="filterTable()">
        </div>
      </div>

      <div class="table-wrapper">
        <table>
          <thead>
            <tr>
              <th width="7%">ID</th>
              <th width="22%">Nama Penyakit</th>
              <th width="36%">Gejala (Vektor Fitur)</th>
              <th width="25%">Solusi</th>
              <th width="10%">Aksi</th>
            </tr>
          </thead>
          <tbody id="table-body">
            <?php
            $rows = [];
            while ($row = $result->fetch_assoc()) { $rows[] = $row; }
            if (empty($rows)):
            ?>
            <tr><td colspan="5">
              <div class="empty-state">
                <svg viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="3"/><path d="M3 9h18M9 21V9"/></svg>
                <p>Belum ada data. Tambahkan melalui form di atas.</p>
              </div>
            </td></tr>
            <?php else: foreach ($rows as $row): ?>
            <tr class="data-row"
                data-penyakit="<?= strtolower(htmlspecialchars($row['penyakit'])) ?>"
                data-gejala="<?= strtolower(htmlspecialchars($row['gejala'])) ?>">
              <td><span class="id-badge"><?= sprintf("%04d", $row['id']) ?></span></td>
              <td><span class="disease-name"><?= htmlspecialchars($row['penyakit']) ?></span></td>
              <td><span class="gejala-text"><?= htmlspecialchars($row['gejala']) ?></span></td>
              <td><span class="solusi-text"><?= htmlspecialchars(mb_strimwidth($row['solusi'], 0, 80, "...")) ?></span></td>
              <td>
                <a href="admin.php?hapus=<?= $row['id'] ?>"
                   class="btn-drop"
                   onclick="return confirm('Hapus record ini dari knowledge base?\n\nPenyakit: <?= addslashes($row['penyakit']) ?>')">
                  Hapus
                </a>
              </td>
            </tr>
            <?php endforeach; endif; ?>
          </tbody>
        </table>
      </div>

      <div class="table-footer">
        <span id="showing-count">Menampilkan <?= count($rows) ?> dari <?= $total_data ?> records</span>
        <span>AgriBot Knowledge Base</span>
      </div>
    </div>

  </div>
</div>

<script>
function filterTable() {
  const q = document.getElementById('search-input').value.toLowerCase().trim();
  const rows = document.querySelectorAll('.data-row');
  let visible = 0;
  rows.forEach(row => {
    const match = !q || row.dataset.penyakit.includes(q) || row.dataset.gejala.includes(q);
    row.style.display = match ? '' : 'none';
    if (match) visible++;
  });
  const total = <?= $total_data ?>;
  document.getElementById('showing-count').textContent =
    q ? `Menampilkan ${visible} dari ${total} records (filter aktif)` : `Menampilkan ${total} dari ${total} records`;
}

function showFileName(input) {
  const el = document.getElementById('file-selected-name');
  if (input.files[0]) {
    el.textContent = '✓ ' + input.files[0].name;
    el.style.display = 'block';
  }
}

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function(e) {
    const target = document.querySelector(this.getAttribute('href'));
    if (target) { e.preventDefault(); target.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
  });
});
</script>
</body>
</html>
