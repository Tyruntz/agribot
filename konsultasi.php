<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AgriBot - Konsultasi Hama & Penyakit Tanaman</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        /* UI Palette - Deep Emerald & Creme */
        :root {
            --primary-emerald: #10451D;
            --emerald-mid: #1A7431;
            --emerald-light: #2e7d32;
            --bg-page: #F4F7F5; 
            --bg-bubble-bot: #ffffff;
            --text-bot: #2D3748;
            --text-muted: #718096;
            --shadow-bubble: 0 2px 4px rgba(16, 69, 29, 0.05);
        }

        * { box-sizing: border-box; }

        body {
            font-family: 'Poppins', sans-serif;
            margin: 0;
            background-color: var(--bg-page); 
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        /* Full Screen Chat Container */
        .chat-container {
            width: 100%;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }

        /* Chat Header */
        .chat-header {
            background-color: var(--primary-emerald);
            color: white;
            padding: 16px 5%; 
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 15px rgba(16, 69, 29, 0.1);
            z-index: 1000;
        }

        .header-title {
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 18px;
            font-weight: 600;
        }

        .action-buttons button {
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.2);
            color: white;
            padding: 6px 14px;
            border-radius: 30px;
            cursor: pointer;
            font-size: 12px;
            transition: 0.3s;
        }
        .action-buttons button:hover { background: rgba(255,255,255,0.25); }

        /* Chat Box */
        .chat-box {
            flex: 1;
            padding: 30px 5%; 
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 20px; 
            scroll-behavior: smooth;
        }

        /* Bubble Messages */
        .message {
            max-width: 80%; 
            padding: 14px 20px;
            border-radius: 20px; 
            font-size: 15px;
            line-height: 1.6;
            position: relative;
            box-shadow: var(--shadow-bubble);
            word-wrap: break-word;
        }

        .bot-msg {
            background-color: var(--bg-bubble-bot);
            color: var(--text-bot);
            align-self: flex-start;
            border: 1px solid #edf2f0;
        }

        .user-msg {
            background: linear-gradient(135deg, var(--emerald-mid) 0%, var(--primary-emerald) 100%);
            color: white;
            align-self: flex-end;
        }

        .bot-title {
            font-weight: 700;
            color: var(--primary-emerald);
            margin-bottom: 6px;
            font-size: 13px;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }

        /* Markdown Styles Inside Bot Message */
        .markdown-content p { margin: 0 0 10px 0; }
        .markdown-content p:last-child { margin-bottom: 0; }
        .markdown-content ul, .markdown-content ol { margin: 5px 0 10px 0; padding-left: 20px; }
        .markdown-content h1, .markdown-content h2, .markdown-content h3 { 
            font-size: 16px; 
            color: var(--primary-emerald); 
            margin: 15px 0 8px 0;
        }
        .markdown-content strong { color: var(--primary-emerald); }

        /* Input Area */
        .input-area-wrapper {
            padding: 20px 5%; 
            background-color: var(--bg-page);
        }

        .input-pill {
            display: flex;
            background: #ffffff;
            padding: 8px 10px;
            border-radius: 50px;
            gap: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.05);
            border: 1px solid #edf2f0;
        }

        .input-pill input {
            flex: 1;
            padding: 12px 20px;
            border: none;
            outline: none;
            font-size: 15px;
            font-family: 'Poppins', sans-serif;
        }

        .btn-kirim {
            background: linear-gradient(135deg, var(--emerald-light) 0%, var(--primary-emerald) 100%);
            color: white;
            border: none;
            width: 48px;
            height: 48px;
            border-radius: 50%;
            cursor: pointer;
            font-size: 18px;
            transition: all 0.3s ease;
        }
        .btn-kirim:hover { transform: scale(1.05); }

        .timestamp {
            font-size: 10px;
            color: var(--text-muted);
            text-align: right;
            margin-top: 8px;
            display: block;
        }
        
        /* Typing Indicator */
        .typing-indicator {
            display: flex;
            gap: 5px;
            padding: 14px 20px;
            background: #fff;
            border-radius: 20px;
            width: fit-content;
            margin-bottom: 20px;
            align-self: flex-start;
            border: 1px solid #edf2f0;
        }
        .dot {
            width: 8px;
            height: 8px;
            background-color: #CBD5E0;
            border-radius: 50%;
            animation: bounce 1.4s infinite ease-in-out both;
        }
        .dot:nth-child(1) { animation-delay: -0.32s; }
        .dot:nth-child(2) { animation-delay: -0.16s; }
        @keyframes bounce {
            0%, 80%, 100% { transform: scale(0); background-color: #CBD5E0; }
            40% { transform: scale(1); background-color: var(--primary-emerald); }
        }

        /* Scrollbar */
        .chat-box::-webkit-scrollbar { width: 6px; }
        .chat-box::-webkit-scrollbar-thumb { background: #E2E8F0; border-radius: 10px; }
    </style>
</head>
<body>

<div class="chat-container">
    <div class="chat-header">
        <div class="header-title">
            <span>🌱</span> AgriBot AI Expert
        </div>
        <div class="action-buttons">
            <button onclick="bersihkanChat()">🗑️ Bersihkan Obrolan</button>
        </div>
    </div>

    <div class="chat-box" id="chat-box">
        </div>

    <div class="input-area-wrapper">
        <div class="input-pill">
            <input type="text" id="input-pesan" placeholder="Ketik keluhan tanaman Anda di sini..." autocomplete="off">
            <button class="btn-kirim" id="btn-kirim">➤</button>
        </div>
    </div>
</div>

<script>
    const chatBox = document.getElementById('chat-box');
    const inputPesan = document.getElementById('input-pesan');
    const btnKirim = document.getElementById('btn-kirim');

    // Mencegah Marked.js mengubah <br> bawaan kita jadi paragraf ganda
    marked.setOptions({ breaks: true });

    window.onload = () => {
        appendMessage('bot', "Halo! I'm AgriBot AI. Silakan deskripsikan gejala atau masalah pada tanaman Anda sedetail mungkin, biar saya bisa identifikasi penyebabnya.");
    };

    function getTime() {
        const now = new Date();
        return now.getHours().toString().padStart(2, '0') + ':' + now.getMinutes().toString().padStart(2, '0');
    }

    function appendMessage(sender, text) {
        const div = document.createElement('div');
        div.classList.add('message');
        
        let content = '';
        if (sender === 'user') {
            div.classList.add('user-msg');
            content = text;
        } else {
            div.classList.add('bot-msg');
            // MAGIC HAPPENS HERE: marked.parse() otomatis merender ### dan ** jadi elemen HTML rapi!
            let formattedText = marked.parse(text); 
            content = `<div class="bot-title">Pakar AgriBot</div><div class="markdown-content">${formattedText}</div>`;
        }
        
        div.innerHTML = content + `<span class="timestamp">${getTime()}</span>`;
        chatBox.appendChild(div);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function showTypingIndicator() {
        const id = 'typing-' + Date.now();
        const div = document.createElement('div');
        div.id = id;
        div.className = 'typing-indicator';
        div.innerHTML = '<div class="dot"></div><div class="dot"></div><div class="dot"></div>';
        chatBox.appendChild(div);
        chatBox.scrollTop = chatBox.scrollHeight;
        return id;
    }

    async function sendMessage() {
        const pesan = inputPesan.value.trim();
        if (!pesan) return;

        appendMessage('user', pesan);
        inputPesan.value = '';

        const typingId = showTypingIndicator();

        try {
            const response = await fetch('http://34.101.40.40:5000/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ pesan: pesan })
            });

            const data = await response.json();
            document.getElementById(typingId).remove();
            appendMessage('bot', data.jawaban);

        } catch (error) {
            document.getElementById(typingId).remove();
            appendMessage('bot', 'Aduh maaf bos, server AI lagi offline di luar MySQL. Pastikan Python API sudah berjalan.');
        }
    }

    function bersihkanChat() {
        if(confirm("Yakin ingin menghapus seluruh riwayat obrolan?")) {
            chatBox.innerHTML = '';
            appendMessage('bot', "Halo! I'm AgriBot AI. Silakan deskripsikan gejala atau masalah pada tanaman Anda sedetail mungkin, biar saya bisa identifikasi penyebabnya.");
        }
    }

    btnKirim.addEventListener('click', sendMessage);
    inputPesan.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') sendMessage();
    });
</script>

</body>
</html>