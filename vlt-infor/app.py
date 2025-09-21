from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="VLT Infor", version="1.0")

# phục vụ /static/*
app.mount("/static", StaticFiles(directory="static"), name="static")

HTML = """
<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>VLT • Information</title>

  <meta property="og:title" content="Vương Lộc Trường — Links" />
  <meta property="og:description" content="Tổng hợp liên kết của Vương Lộc Trường: Facebook, Zalo, Instagram, TikTok, Chatbot…" />
  <meta property="og:type" content="website" />
  <meta name="theme-color" content="#111827" />

  <link rel="icon" type="image/png" href="/static/fav.png" />

  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    body{
      background:
        radial-gradient(1200px 600px at 10% -10%, rgba(59,130,246,.12), transparent 50%),
        radial-gradient(800px 400px at 100% 0%, rgba(139,92,246,.12), transparent 40%),
        #0b1220;
    }
    .link-btn {
      display:flex; justify-content:center; align-items:center; gap:10px;
    }
    .link-btn img { width:22px; height:22px; }

    /* Modal chung */
    .modal {
      position:fixed; inset:0; background:rgba(0,0,0,0.6);
      display:none; justify-content:center; align-items:center; z-index:60;
    }
    .modal-content {
      background:#1e293b; padding:20px; border-radius:12px;
      width:360px; text-align:center; color:#e2e8f0;
      border:1px solid #334155;
    }
    .btn { margin-top:14px; padding:8px 14px; background:#3b82f6; border:none; border-radius:8px; color:white; cursor:pointer; }

    /* Progress */
    .countdown { font-size:16px; font-weight:700; margin-top:10px; }
    .progress { width:100%; height:10px; background:#334155; border-radius:6px; margin-top:10px; overflow:hidden; }
    .progress #bar { height:100%; width:0%; background:#3b82f6; transition: width 1s linear; }

    /* Avatar modal */
    .avatar-img { max-width:90vw; max-height:80vh; border-radius:12px; }
  </style>
</head>
<body class="min-h-screen text-slate-100 antialiased">
  <main class="mx-auto w-[720px] max-w-[95vw] px-5 pt-5 pb-3">
    <section class="bg-slate-900/60 backdrop-blur rounded-2xl border border-slate-700/60 shadow-xl p-6 md:p-8 text-center h-[700px]">

      <!-- Avatar (click để mở modal ảnh lớn) -->
      <div class="mx-auto w-40 h-40 rounded-full ring-4 ring-blue-500/30 overflow-hidden shadow-lg cursor-pointer" onclick="showAvatar()">
        <img alt="avatar" class="w-full h-full object-cover" src="/static/avatarcuatoi.jpg" />
      </div>

      <h1 class="mt-5 text-3xl md:text-4xl font-bold tracking-tight">Vương Lộc Trường</h1>
      <p class="mt-2 text-slate-300">Đây là infor của mình ^^</p>

      <!-- Liên kết -->
      <div class="mt-6 space-y-3">
        <a href="https://www.facebook.com/vltruong01/" target="_blank" rel="noopener"
           class="link-btn w-full py-3.5 px-5 rounded-xl font-semibold text-[17px]
                  border border-blue-500/40 bg-blue-600/20 hover:bg-blue-600/30 transition">
          <img src="/static/icons/facebook.png" alt="Facebook"/>Facebook
        </a>
        <a href="https://zalo.me/84869183424" target="_blank" rel="noopener"
           class="link-btn w-full py-3.5 px-5 rounded-xl font-semibold text-[17px]
                  border border-cyan-500/40 bg-cyan-600/20 hover:bg-cyan-600/30 transition">
          <img src="/static/icons/zalo.png" alt="Zalo"/>Zalo
        </a>
        <a href="https://www.instagram.com/102vl_truong" target="_blank" rel="noopener"
           class="link-btn w-full py-3.5 px-5 rounded-xl font-semibold text-[17px]
                  border border-pink-500/40 bg-pink-600/20 hover:bg-pink-600/30 transition">
          <img src="/static/icons/instagram.png" alt="Instagram"/>Instagram
        </a>
        <a href="https://www.tiktok.com/@vltruong1" target="_blank" rel="noopener"
           class="link-btn w-full py-3.5 px-5 rounded-xl font-semibold text-[17px]
                  border border-rose-500/40 bg-rose-600/20 hover:bg-rose-600/30 transition">
          <img src="/static/icons/tiktok.png" alt="TikTok"/>TikTok
        </a>
        <!-- Chatbot -->
        <button onclick="openChatbot()" 
           class="link-btn w-full py-3.5 px-5 rounded-xl font-semibold text-[17px]
                  border border-indigo-500/50 bg-indigo-600/20 hover:bg-indigo-600/30 transition">
          🤖 Chatbot giới thiệu VLT
        </button>
      </div>

      <p class="mt-6 text-xs text-slate-400 text-center">
        © 2025 Vương Lộc Trường • All rights reserved
      </p>
    </section>
  </main>

  <!-- Modal: Chờ Chatbot -->
  <div id="chatbotModal" class="modal" onclick="backdropClose(event,'chatbotModal')">
    <div class="modal-content">
      <h2>⏳ Vui lòng chờ chatbot đánh răng</h2>
      <div class="countdown">Còn <span id="count">60</span> giây</div>
      <div class="progress"><div id="bar"></div></div>
      <p id="status" class="mt-2 text-sm text-slate-300">Nó vừa mới ngủ dậy 🥱</p>
      <button class="btn" onclick="goNow()">Đi ngay</button>
    </div>
  </div>

  <!-- Modal: Avatar -->
  <div id="avatarModal" class="modal" onclick="backdropClose(event,'avatarModal')">
    <div class="modal-content" style="background:transparent; border:none; padding:0; width:auto;">
      <img src="/static/avatarcuatoi.jpg" alt="Avatar full" class="avatar-img"/>
      <button class="mt-3 px-3 py-2 bg-gray-700 rounded-lg text-sm text-white" onclick="closeModal('avatarModal')">Đóng</button>
    </div>
  </div>

  <script>
    const CHATBOT_URL = "https://vlt-chatbot.fly.dev/";
    let didRedirect = false;
    let chatbotTimer = null;
    let chatbotPoll  = null;

    function openModal(id){ document.getElementById(id).style.display='flex'; }
    function closeModal(id){ document.getElementById(id).style.display='none'; }
    function backdropClose(e, id){ if(e.target.id === id){ closeModal(id); } }

    function showAvatar(){ openModal('avatarModal'); }
    function goNow(){ window.location.assign(CHATBOT_URL); }

    function openChatbot(){
      openModal('chatbotModal');

      // Nếu đã có timer/poll thì không tạo mới
      if (chatbotTimer || chatbotPoll) return;

      let sec = 60;
      const total = sec;
      const $c = document.getElementById('count');
      const $s = document.getElementById('status');
      const $bar = document.getElementById('bar');

      chatbotTimer = setInterval(()=>{
        if(didRedirect) return;
        sec = Math.max(0, sec - 1);
        $c.textContent = sec;
        const pct = Math.min(100, Math.round((1 - sec/total) * 100));
        $bar.style.width = pct + "%";
        if(sec <= 0 && !didRedirect){
          didRedirect = true;
          clearInterval(chatbotTimer);
          clearInterval(chatbotPoll);
          chatbotTimer = null;
          chatbotPoll  = null;
          $s.textContent = "⏭️ Hết thời gian, chuyển hướng…";
          window.location.assign(CHATBOT_URL);
        }
      }, 1000);

      chatbotPoll = setInterval(()=>{
        if(didRedirect) return;
        fetch(CHATBOT_URL + "health?t=" + Date.now(), {cache:"no-store"})
          .then(r=>{
            if(r.ok && !didRedirect){
              didRedirect = true;
              clearInterval(chatbotTimer);
              clearInterval(chatbotPoll);
              chatbotTimer = null;
              chatbotPoll  = null;
              $s.textContent = "✅ Chatbot đã sẵn sàng!";
              $bar.style.width = "100%";
              setTimeout(()=>{ window.location.assign(CHATBOT_URL); }, 500);
            }
          })
          .catch(()=>{});
      }, 2000);
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
