from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Anhsime Infor", version="1.0")

# phục vụ /static/*
app.mount("/static", StaticFiles(directory="static"), name="static")

HTML = """
<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Anhsime • Information</title>

  <meta property="og:title" content="Anhsime — Information" />
  <meta property="og:description" content="Tổng hợp liên kết của Anhsime: Facebook, Zalo, Instagram, TikTok, Chatbot…" />
  <meta property="og:type" content="website" />
  <meta name="theme-color" content="#111827" />

  <link rel="icon" type="image/png" href="/static/fav.png" />
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    body{
      background:
        radial-gradient(1000px 500px at 10% -10%, rgba(59,130,246,.12), transparent 50%),
        radial-gradient(700px 350px at 100% 0%, rgba(139,92,246,.12), transparent 40%),
        #0b1220;
    }

    /* nút link tổng thể gọn */
    .link-btn { display:flex; justify-content:center; align-items:center; gap:8px; }
    .link-btn img { width:18px; height:18px; }

    /* Modal (dùng bản chi tiết) */
    .modal {
      position:fixed; inset:0; background:rgba(0,0,0,0.6);
      display:none; justify-content:center; align-items:center; z-index:50;
    }
    .modal-content {
      background:#1e293b; padding:20px; border-radius:12px;
      width:340px; text-align:center; color:#e2e8f0;
    }
    .modal h2 { font-size:16px; font-weight:700; margin-bottom:10px; }

    /* item có icon trái + text + nút phải, không rớt dòng */
    .list-item {
      display:flex; align-items:center; justify-content:space-between;
      gap:10px; margin:10px 0; padding:8px 10px;
      border:1px solid #334155; border-radius:8px; background:#0f172a;
      font-size:13px;
    }
    .list-item .left {
      display:flex; align-items:center; gap:8px;
      flex:1 1 auto; min-width:0;
      max-width: calc(100% - 90px); /* luôn chừa chỗ cho nút */
    }
    .list-item .left img { width:20px; height:20px; flex:0 0 auto; }
    .left span { overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }

    .copy-btn, .view-btn {
      flex:0 0 auto; width:74px; white-space:nowrap;
      background:#3b82f6; color:#fff; border:none; border-radius:6px;
      padding:4px 6px; font-size:12px; line-height:1; cursor:pointer; text-align:center;
    }
    .download-link {
      display:inline-block; margin-top:10px;
      background:#10b981; color:white; padding:6px 12px;
      border-radius:6px; font-size:13px; text-decoration:none;
    }
    .qr-img { width:250px; max-width:90%; margin:10px auto; border-radius:8px; }
  </style>
</head>
<body class="min-h-screen text-slate-100 antialiased">
  <main class="mx-auto w-[640px] max-w-[95vw] px-4 pt-4 pb-3">
    <section class="bg-slate-900/60 backdrop-blur rounded-2xl border border-slate-700/60 shadow-xl p-5 md:p-6 text-center">

      <!-- Avatar (gọn) -->
      <div class="mx-auto w-[142px] h-[142px] rounded-full ring-4 ring-blue-500/30 overflow-hidden shadow-lg">
        <img alt="avatar" class="w-full h-full object-cover" src="/static/avatar.jpg" />
      </div>

      <h1 class="mt-4 text-2xl md:text-3xl font-bold tracking-tight">Nguyễn Ngọc Ánh</h1>
      <p class="mt-1 text-slate-300 text-[14px]">Đây là infor của mình ^^</p>

      <!-- Liên kết (gọn) -->
      <div class="mt-4 space-y-2">

        <!-- Chatbot -->
        <a href="https://anhsime-chatbot.fly.dev/" target="_blank" rel="noopener"
           class="link-btn w-full py-2.5 px-4 rounded-xl font-semibold text-[15px]
                  border border-indigo-500/50 bg-indigo-600/20 hover:bg-indigo-600/30 transition">
          🤖 Chatbot giới thiệu Anhsime
        </a>

        <a href="https://www.facebook.com/anhsimee" target="_blank" rel="noopener"
           class="link-btn w-full py-2.5 px-4 rounded-xl font-semibold text-[15px]
                  border border-blue-500/40 bg-blue-600/20 hover:bg-blue-600/30 transition">
          <img src="/static/icons/facebook.png" alt="Facebook"/>Facebook
        </a>

        <a href="https://zalo.me/84945529606" target="_blank" rel="noopener"
           class="link-btn w-full py-2.5 px-4 rounded-xl font-semibold text-[15px]
                  border border-cyan-500/40 bg-cyan-600/20 hover:bg-cyan-600/30 transition">
          <img src="/static/icons/zalo.png" alt="Zalo"/>Zalo
        </a>

        <a href="https://www.instagram.com/anhsimee" target="_blank" rel="noopener"
           class="link-btn w-full py-2.5 px-4 rounded-xl font-semibold text-[15px]
                  border border-pink-500/40 bg-pink-600/20 hover:bg-pink-600/30 transition">
          <img src="/static/icons/instagram.png" alt="Instagram"/>Instagram
        </a>

        <a href="https://www.tiktok.com/@anhsime" target="_blank" rel="noopener"
           class="link-btn w-full py-2.5 px-4 rounded-xl font-semibold text-[15px]
                  border border-rose-500/40 bg-rose-600/20 hover:bg-rose-600/30 transition">
          <img src="/static/icons/tiktok.png" alt="TikTok"/>TikTok
        </a>

        <a href="https://locket.camera/links/h6TKJzCoGGVz9n9u6" target="_blank" rel="noopener"
           class="link-btn w-full py-2.5 px-4 rounded-xl font-semibold text-[15px]
                  border border-yellow-500/40 bg-yellow-600/20 hover:bg-yellow-600/30 transition">
          <img src="/static/icons/locket.png" alt="Locket"/>Locket
        </a>

        <!-- Games -->
        <button onclick="openModal('gameModal')" 
           class="link-btn w-full py-2.5 px-4 rounded-xl font-semibold text-[15px]
                  border border-green-500/40 bg-green-600/20 hover:bg-green-600/30 transition">
          🎮 Các game đang chơi
        </button>

        <!-- Bank/Payments -->
        <button onclick="openModal('bankModal')" 
           class="link-btn w-full py-2.5 px-4 rounded-xl font-semibold text-[15px]
                  border border-emerald-500/40 bg-emerald-600/20 hover:bg-emerald-600/30 transition">
          💳 Tài khoản thanh toán
        </button>
      </div>

      <p class="mt-4 text-xs text-slate-400 text-center">
        © 2025 Anhsime • All rights reserved
      </p>
    </section>
  </main>

  <!-- Modal: Games (phiên bản chi tiết) -->
  <div id="gameModal" class="modal" onclick="backdropClose(event, 'gameModal')">
    <div class="modal-content">
      <h2>🎮 Các game đang chơi</h2>

      <div class="list-item">
        <div class="left">
          <img src="/static/icons/lienquan.png" alt="Liên Quân"/>
          <span>Liên Quân: <b>anhsime</b></span>
        </div>
        <button class="copy-btn" onclick="copyText('anhsime')">Copy tên</button>
      </div>

      <div class="list-item">
        <div class="left">
          <img src="/static/icons/playtogether.png" alt="Play Together"/>
          <span>Play Together: <b>anhsime</b></span>
        </div>
        <button class="copy-btn" onclick="copyText('anhsime')">Copy tên</button>
      </div>

      <button class="mt-2 px-3 py-2 bg-gray-500 rounded-lg text-sm" onclick="closeModal('gameModal')">Đóng</button>
    </div>
  </div>

  <!-- Modal: Bank/Payments (phiên bản chi tiết + xem QR trong modal) -->
  <div id="bankModal" class="modal" onclick="backdropClose(event, 'bankModal')">
    <div class="modal-content">
      <h2>💳 Tài khoản thanh toán</h2>

      <div class="list-item">
        <div class="left">
          <img src="/static/icons/ocb.png" alt="OCB"/>
          <span>OCB</span>
        </div>
        <button class="view-btn" onclick="showQR('/static/qr/qr_ocb.jpg')">Xem QR</button>
      </div>

      <div class="list-item">
        <div class="left">
          <img src="/static/icons/momo.png" alt="MoMo"/>
          <span>MoMo</span>
        </div>
        <button class="view-btn" onclick="showQR('/static/qr/qr_momo.jpg')">Xem QR</button>
      </div>

      <button class="mt-2 px-3 py-2 bg-gray-500 rounded-lg text-sm" onclick="closeModal('bankModal')">Đóng</button>
    </div>
  </div>

  <!-- Modal: Hiển thị QR + nút tải -->
  <div id="qrModal" class="modal" onclick="backdropClose(event, 'qrModal')">
    <div class="modal-content">
      <h2>📷 QR Thanh toán</h2>
      <img id="qrImage" src="" alt="QR Code" class="qr-img"/>
      <a id="qrDownload" href="" download class="download-link">⬇️ Tải QR</a>
      <button class="mt-2 px-3 py-2 bg-gray-500 rounded-lg text-sm" onclick="closeModal('qrModal')">Đóng</button>
    </div>
  </div>

  <script>
    function openModal(id){ document.getElementById(id).style.display='flex'; }
    function closeModal(id){ document.getElementById(id).style.display='none'; }
    function backdropClose(e, id){ if(e.target.id === id){ closeModal(id); } }

    function copyText(text){
      navigator.clipboard.writeText(text).then(()=>{ alert('Đã copy: ' + text); });
    }

    function showQR(path){
      document.getElementById('qrImage').src = path;
      document.getElementById('qrDownload').href = path;
      openModal('qrModal');
    }
  </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(HTML, headers={"Cache-Control": "no-store"})

@app.get("/health")
def health():
    return {"status": "ok"}
