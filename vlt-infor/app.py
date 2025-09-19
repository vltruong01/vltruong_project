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
      display: flex;
      justify-content: center;  /* căn giữa ngang */
      align-items: center;      /* căn giữa dọc */
      gap: 10px;                /* khoảng cách icon và text */
    }
    .link-btn img {
      width:22px; height:22px;
    }
  </style>
</head>
<body class="min-h-screen text-slate-100 antialiased">
  <main class="mx-auto w-[720px] max-w-[95vw] px-5 pt-5 pb-3">
    <section class="bg-slate-900/60 backdrop-blur rounded-2xl border border-slate-700/60 shadow-xl p-6 md:p-8 text-center h-[700px]">

      <!-- Avatar -->
      <div class="mx-auto w-40 h-40 rounded-full ring-4 ring-blue-500/30 overflow-hidden shadow-lg">
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
        <!-- Chatbot: icon giữ nguyên là 🤖 -->
        <a href="https://vlt-chatbot.fly.dev/" target="_blank" rel="noopener"
           class="link-btn w-full py-3.5 px-5 rounded-xl font-semibold text-[17px]
                  border border-indigo-500/50 bg-indigo-600/20 hover:bg-indigo-600/30 transition">
          🤖 Chatbot giới thiệu VLT
        </a>
      </div>

      <p class="mt-6 text-xs text-slate-400 text-center">
        © 2025 Vương Lộc Trường • All rights reserved
      </p>
    </section>
  </main>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(HTML, headers={"Cache-Control": "no-store"})

@app.get("/health")
def health():
    return {"status": "ok"}
