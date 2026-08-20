from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Anhsime Infor", version="1.1")

app.mount("/static", StaticFiles(directory="static"), name="static")

HTML = """
<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Anhsime • Information</title>
  <link rel="icon" type="image/png" href="/static/fav.png" />
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    :root { color-scheme: dark; }
    *, *::before, *::after { box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body{
      min-width:320px;
      min-height:100vh;
      margin:0;
      background:
        radial-gradient(1000px 500px at 10% -10%, rgba(59,130,246,.12), transparent 50%),
        radial-gradient(700px 350px at 100% 0%, rgba(139,92,246,.12), transparent 40%),
        #0b1220;
    }

    .link-btn {
      display:flex; justify-content:center; align-items:center; gap:9px;
      font-size:15px; font-weight:600;
      padding:12px 16px;
      border-radius:11px;
      transition: all .2s ease;
    }
    .link-btn img { width:20px; height:20px; }

    /* Modal */
    .modal {
      position:fixed; inset:0; background:rgba(0,0,0,0.6);
      display:none; justify-content:center; align-items:center; z-index:50;
    }
    .modal-content {
      background:#1e293b; padding:24px; border-radius:14px;
      width:min(380px, calc(100vw - 32px)); max-height:92vh; overflow:auto;
      text-align:center; color:#e2e8f0;
      border:1px solid #334155;
    }
    .modal h2 { font-size:18px; font-weight:700; margin-bottom:12px; }

    /* list-item trong modal to hơn */
    .list-item {
      display:flex; align-items:center; justify-content:space-between;
      gap:12px; margin:12px 0; padding:11px 14px;
      border:1px solid #334155; border-radius:9px; background:#0f172a;
      font-size:15px;
    }
    .list-item .left {
      display:flex; align-items:center; gap:10px;
      flex:1 1 auto; min-width:0;
      max-width: calc(100% - 100px);
    }
    .list-item .left img { width:24px; height:24px; flex:0 0 auto; }
    .left span { overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }

    .copy-btn, .view-btn {
      flex:0 0 auto; width:85px; white-space:nowrap;
      background:#3b82f6; color:#fff; border:none; border-radius:7px;
      padding:7px 9px; font-size:14px; line-height:1; cursor:pointer; text-align:center;
    }
    .download-link {
      display:inline-block; margin-top:12px;
      background:#10b981; color:white; padding:8px 14px;
      border-radius:7px; font-size:14px; text-decoration:none;
    }
    .qr-img { width:260px; max-width:90%; margin:12px auto; border-radius:9px; }

    /* Avatar modal */
    .avatar {
      display:block;
      width:132px;
      height:132px;
      margin:0 auto;
      padding:4px;
      border:0;
      border-radius:50%;
      background:linear-gradient(135deg, #60a5fa, #34d399);
      cursor:zoom-in;
    }
    .avatar img { display:block; width:100%; height:100%; border-radius:50%; object-fit:cover; }
    .avatar-img { display:block; max-width:100%; max-height:76vh; margin:0 auto; border-radius:12px; object-fit:contain; }
    .avatar-modal-card { position:relative; width:min(410px, 100%); padding:24px; border:1px solid #334155; border-radius:16px; background:#17243a; box-shadow:0 24px 70px rgba(0,0,0,.3); text-align:center; }
    .modal-close { position:absolute; top:10px; right:10px; width:34px; height:34px; border:0; border-radius:50%; color:#a8b4c7; background:transparent; font-size:23px; cursor:pointer; }
    .modal-close:hover { color:#f8fafc; background:rgba(148,163,184,.14); }
    .link-btn:focus-visible, .copy-btn:focus-visible, .view-btn:focus-visible,
    .modal button:focus-visible, .download-link:focus-visible {
      outline:3px solid rgba(96,165,250,.55); outline-offset:3px;
    }
    .modal-content > button { cursor:pointer; }
    .avatar-trigger { display:block; padding:0; border:0; background:transparent; }
    @media (max-width:520px) {
      body { padding:12px; }
      .avatar { width:116px; height:116px; }
      .modal-content { padding:20px 16px; }
      .avatar-modal-card { padding:22px 16px; }
    }
    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after { scroll-behavior:auto !important; transition:none !important; }
    }
  </style>
</head>
<body class="min-h-screen text-slate-100 antialiased">
  <main class="mx-auto w-[640px] max-w-[95vw] px-4 pt-4 pb-3">
    <section class="bg-slate-900/60 backdrop-blur rounded-2xl border border-slate-700/60 shadow-xl p-5 md:p-6 text-center">

      <!-- Avatar có onclick mở modal -->
      <button class="avatar" type="button" onclick="showAvatar()" aria-label="Xem ảnh đại diện lớn">
        <img alt="Ảnh đại diện của Nguyễn Ngọc Ánh" src="/static/avatar.jpg" width="132" height="132" fetchpriority="high" />
      </button>

      <h1 class="mt-4 text-2xl md:text-3xl font-bold tracking-tight">Nguyễn Ngọc Ánh</h1>
      <p class="mt-1 text-slate-300 text-[14.5px]">Đây là infor của mình ^^</p>

      <div class="mt-5 space-y-3">
        <!-- CHỈ ĐỔI CHỖ NÀY: chatbot -> mở modal -->
        <button onclick="openModal('chatbotModal')" class="link-btn w-full border border-indigo-500/50 bg-indigo-600/20 hover:bg-indigo-600/30">
          🤖 Chatbot giới thiệu Anhsime
        </button>

        <a href="https://zalo.me/84945529606" target="_blank" rel="noopener noreferrer" class="link-btn w-full border border-cyan-500/40 bg-cyan-600/20 hover:bg-cyan-600/30">
          <img src="/static/icons/zalo.png"/>Zalo
        </a>
        <a href="https://www.instagram.com/anhsimee" target="_blank" rel="noopener noreferrer" class="link-btn w-full border border-pink-500/40 bg-pink-600/20 hover:bg-pink-600/30">
          <img src="/static/icons/instagram.png"/>Instagram
        </a>
        <a href="https://www.tiktok.com/@anhsime" target="_blank" rel="noopener noreferrer" class="link-btn w-full border border-rose-500/40 bg-rose-600/20 hover:bg-rose-600/30">
          <img src="/static/icons/tiktok.png"/>TikTok
        </a>
        <a href="https://locket.camera/links/h6TKJzCoGGVz9n9u6" target="_blank" rel="noopener noreferrer" class="link-btn w-full border border-yellow-500/40 bg-yellow-600/20 hover:bg-yellow-600/30">
          <img src="/static/icons/locket.png"/>Locket
        </a>
        <button onclick="openModal('gameModal')" class="link-btn w-full border border-green-500/40 bg-green-600/20 hover:bg-green-600/30">
          🎮 Các game đang chơi
        </button>
        <button onclick="openModal('bankModal')" class="link-btn w-full border border-emerald-500/40 bg-emerald-600/20 hover:bg-emerald-600/30">
          💳 Tài khoản ngân hàng
        </button>
      </div>

      <p class="mt-4 text-xs text-slate-400 text-center">© 2025 Anhsime • All rights reserved</p>
    </section>
  </main>

  <!-- THÊM MỚI: Modal Chatbot chưa hoạt động -->
  <div id="chatbotModal" class="modal" role="dialog" aria-modal="true" aria-labelledby="chatbotTitle" onclick="backdropClose(event, 'chatbotModal')">
    <div class="modal-content">
      <h2 id="chatbotTitle">🤖 Chatbot này chưa hoạt động</h2>
      <p class="text-slate-300 text-[14.5px]">Hiện tại chatbot của Anhsime chưa được bật. Bạn quay lại sau nha ^^</p>
      <button class="mt-3 px-3 py-2 bg-gray-500 rounded-lg text-sm" onclick="closeModal('chatbotModal')">Đóng</button>
    </div>
  </div>

  <!-- Modal: Games -->
  <div id="gameModal" class="modal" role="dialog" aria-modal="true" aria-labelledby="gameTitle" onclick="backdropClose(event, 'gameModal')">
    <div class="modal-content">
      <h2 id="gameTitle">🎮 Các game đang chơi</h2>
      <div class="list-item"><div class="left"><img src="/static/icons/lienquan.png"/><span>Liên Quân: <b>anhsime</b></span></div><button class="copy-btn" onclick="copyText('anhsime')">Copy tên</button></div>
      <div class="list-item"><div class="left"><img src="/static/icons/playtogether.png"/><span>Play Together: <b>anhsime</b></span></div><button class="copy-btn" onclick="copyText('anhsime')">Copy tên</button></div>
      <button class="mt-3 px-3 py-2 bg-gray-500 rounded-lg text-sm" onclick="closeModal('gameModal')">Đóng</button>
    </div>
  </div>

  <!-- Modal: Bank -->
  <div id="bankModal" class="modal" role="dialog" aria-modal="true" aria-labelledby="bankTitle" onclick="backdropClose(event, 'bankModal')">
    <div class="modal-content">
      <h2 id="bankTitle">💳 Tài khoản thanh toán</h2>
      <div class="list-item"><div class="left"><img src="/static/icons/ocb.png"/><span>OCB</span></div><button class="view-btn" onclick="showQR('/static/qr/qr_ocb.jpg')">Xem QR</button></div>
      <div class="list-item"><div class="left"><img src="/static/icons/momo.png"/><span>MoMo</span></div><button class="view-btn" onclick="showQR('/static/qr/qr_momo.jpg')">Xem QR</button></div>
      <button class="mt-3 px-3 py-2 bg-gray-500 rounded-lg text-sm" onclick="closeModal('bankModal')">Đóng</button>
    </div>
  </div>

  <!-- Modal: QR -->
  <div id="qrModal" class="modal" role="dialog" aria-modal="true" aria-labelledby="qrTitle" onclick="backdropClose(event, 'qrModal')">
    <div class="modal-content">
      <h2 id="qrTitle">📷 QR Thanh toán</h2>
      <img id="qrImage" src="" alt="QR Code" class="qr-img"/>
      <a id="qrDownload" href="" download class="download-link">⬇️ Tải QR</a>
      <button class="mt-2 px-3 py-2 bg-gray-500 rounded-lg text-sm" onclick="closeModal('qrModal')">Đóng</button>
    </div>
  </div>

  <!-- Modal: Avatar -->
  <div id="avatarModal" class="modal" role="dialog" aria-modal="true" aria-label="Ảnh đại diện" onclick="backdropClose(event, 'avatarModal')">
    <div class="avatar-modal-card">
      <button class="modal-close" type="button" aria-label="Đóng" onclick="closeModal('avatarModal')">×</button>
      <img src="/static/avatar.jpg" alt="Ảnh đại diện của Nguyễn Ngọc Ánh" class="avatar-img"/>
    </div>
  </div>

  <script>
    function openModal(id){
      const modal = document.getElementById(id);
      modal.style.display='flex';
      modal.querySelector('button')?.focus();
    }
    function closeModal(id){ document.getElementById(id).style.display='none'; }
    function backdropClose(e, id){ if(e.target.id === id){ closeModal(id); } }
    async function copyText(text){
      try {
        await navigator.clipboard.writeText(text);
        alert('Đã copy: ' + text);
      } catch (_) {
        window.prompt('Sao chép tên:', text);
      }
    }
    function showQR(path){ document.getElementById('qrImage').src = path; document.getElementById('qrDownload').href = path; openModal('qrModal'); }
    function showAvatar(){ openModal('avatarModal'); }
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') {
        const modal = document.querySelector('.modal[style*="display: flex"]');
        if (modal) closeModal(modal.id);
      }
    });
  </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(HTML, headers={"Cache-Control": "public, max-age=60, s-maxage=60"})

@app.get("/health")
def health():
    return {"status": "ok"}


@app.middleware("http")
async def cache_static_files(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/static/"):
        response.headers.setdefault("Cache-Control", "public, max-age=86400, s-maxage=86400")
    return response
