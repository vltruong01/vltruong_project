from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles


app = FastAPI(title="VLT Infor", version="1.1")
app.mount("/static", StaticFiles(directory="static"), name="static")

HTML = """<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Các liên kết và thông tin của Vương Lộc Trường.">
  <meta property="og:title" content="Vương Lộc Trường | Links">
  <meta property="og:description" content="Tổng hợp liên kết, dự án và chatbot của Vương Lộc Trường.">
  <meta property="og:type" content="website">
  <meta name="theme-color" content="#101827">
  <title>Vương Lộc Trường | Links</title>
  <link rel="icon" type="image/png" href="/static/fav.png">
  <style>
    :root {
      color-scheme: dark;
      --bg: #0b1220;
      --panel: rgba(18, 28, 46, .9);
      --panel-soft: #152238;
      --text: #f8fafc;
      --muted: #a8b4c7;
      --line: rgba(148, 163, 184, .22);
      --accent: #60a5fa;
      --success: #34d399;
      --shadow: 0 24px 70px rgba(0, 0, 0, .3);
    }
    * { box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body {
      min-width: 320px;
      min-height: 100vh;
      margin: 0;
      padding: 24px 16px;
      background: var(--bg);
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    body::before {
      position: fixed;
      inset: 0;
      z-index: -1;
      content: "";
      background: linear-gradient(135deg, rgba(37, 99, 235, .16), transparent 42%),
                  linear-gradient(315deg, rgba(16, 185, 129, .1), transparent 38%);
      pointer-events: none;
    }
    main { width: min(680px, 100%); margin: 0 auto; }
    .profile {
      padding: 28px 20px 22px;
      border: 1px solid var(--line);
      border-radius: 18px;
      background: var(--panel);
      box-shadow: var(--shadow);
      text-align: center;
      backdrop-filter: blur(16px);
    }
    .avatar {
      display: block;
      width: 132px;
      height: 132px;
      margin: 0 auto;
      padding: 4px;
      border: 0;
      border-radius: 50%;
      background: linear-gradient(135deg, var(--accent), var(--success));
      cursor: zoom-in;
    }
    .avatar img { display: block; width: 100%; height: 100%; border-radius: 50%; object-fit: cover; }
    h1 { margin: 18px 0 7px; font-size: clamp(28px, 7vw, 40px); line-height: 1.1; }
    .intro { max-width: 470px; margin: 0 auto; color: var(--muted); line-height: 1.6; }
    .quick-facts { display: flex; justify-content: center; flex-wrap: wrap; gap: 8px; margin-top: 17px; }
    .fact { padding: 7px 11px; border: 1px solid var(--line); border-radius: 999px; color: #dbeafe; background: rgba(37, 99, 235, .12); font-size: 13px; }
    .links { display: grid; gap: 11px; margin-top: 25px; }
    .link-btn {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
      min-height: 52px;
      padding: 12px 16px;
      border: 1px solid var(--line);
      border-radius: 11px;
      color: var(--text);
      background: var(--panel-soft);
      font: inherit;
      font-weight: 700;
      text-decoration: none;
      cursor: pointer;
      transition: transform .16s ease, border-color .16s ease, background .16s ease;
    }
    .link-btn:hover, .link-btn:focus-visible { transform: translateY(-2px); border-color: var(--accent); background: #1b2e4c; }
    .link-btn:focus-visible, .modal-close:focus-visible { outline: 3px solid rgba(96, 165, 250, .45); outline-offset: 2px; }
    .link-btn img { width: 23px; height: 23px; object-fit: contain; }
    .link-btn.primary { border-color: rgba(96, 165, 250, .55); background: rgba(37, 99, 235, .26); }
    .link-btn.green { border-color: rgba(52, 211, 153, .48); background: rgba(16, 185, 129, .18); }
    .link-btn.pink { border-color: rgba(244, 114, 182, .45); background: rgba(219, 39, 119, .16); }
    .link-btn.indigo { border-color: rgba(129, 140, 248, .5); background: rgba(79, 70, 229, .19); }
    .link-btn .symbol { width: 23px; font-size: 20px; line-height: 1; }
    footer { margin-top: 20px; color: #8290a5; font-size: 12px; }
    .modal { display: none; position: fixed; inset: 0; z-index: 10; align-items: center; justify-content: center; padding: 16px; background: rgba(2, 6, 23, .78); }
    .modal.is-open { display: flex; }
    .modal-card { position: relative; width: min(410px, 100%); max-height: 92vh; overflow: auto; padding: 24px; border: 1px solid var(--line); border-radius: 16px; background: #17243a; box-shadow: var(--shadow); text-align: center; }
    .modal-card h2 { margin: 0 0 16px; font-size: 20px; }
    .modal-close { position: absolute; top: 10px; right: 10px; width: 34px; height: 34px; border: 0; border-radius: 50%; color: var(--muted); background: transparent; font-size: 23px; cursor: pointer; }
    .modal-close:hover { color: var(--text); background: rgba(148, 163, 184, .14); }
    .modal-text { color: var(--muted); line-height: 1.5; }
    .progress { height: 9px; margin: 17px 0 10px; overflow: hidden; border-radius: 999px; background: #263752; }
    .progress-bar { width: 0; height: 100%; border-radius: inherit; background: var(--accent); transition: width .25s ease; }
    .countdown { font-size: 16px; font-weight: 700; }
    .modal-actions { display: flex; justify-content: center; gap: 9px; margin-top: 18px; }
    .small-btn { padding: 9px 14px; border: 0; border-radius: 8px; color: white; background: #334155; font: inherit; cursor: pointer; text-decoration: none; }
    .small-btn.success { background: #059669; }
    .bank-row { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin: 11px 0; padding: 12px; border: 1px solid var(--line); border-radius: 10px; background: #0f1b2d; }
    .bank-name { display: flex; align-items: center; gap: 10px; min-width: 0; font-weight: 700; }
    .bank-name img { width: 25px; height: 25px; object-fit: contain; }
    .qr-img { display: block; width: min(280px, 100%); margin: 8px auto 0; border-radius: 10px; }
    .avatar-large { display: block; max-width: 100%; max-height: 76vh; margin: 0 auto; border-radius: 12px; object-fit: contain; }
    .toast { position: fixed; right: 16px; bottom: 16px; z-index: 20; padding: 11px 14px; border: 1px solid rgba(52, 211, 153, .45); border-radius: 9px; color: #d1fae5; background: #064e3b; opacity: 0; transform: translateY(10px); transition: .2s ease; pointer-events: none; }
    .toast.show { opacity: 1; transform: translateY(0); }
    @media (max-width: 520px) { body { padding: 12px; } .profile { padding: 24px 15px 18px; } .avatar { width: 116px; height: 116px; } .link-btn { min-height: 50px; } .modal-card { padding: 22px 16px; } }
    @media (prefers-reduced-motion: reduce) { *, *::before, *::after { scroll-behavior: auto !important; transition-duration: .01ms !important; } }
  </style>
</head>
<body>
  <main>
    <section class="profile" aria-labelledby="profile-title">
      <button class="avatar" type="button" onclick="openModal('avatarModal')" aria-label="Xem ảnh đại diện lớn">
        <img src="/static/avatarcuatoi.jpg" width="132" height="132" alt="Ảnh đại diện của Vương Lộc Trường" fetchpriority="high">
      </button>
      <h1 id="profile-title">Vương Lộc Trường</h1>
      <p class="intro">Góc nhỏ để kết nối với mình, xem các dự án cá nhân và khám phá chatbot giới thiệu VLT.</p>
      <div class="quick-facts" aria-label="Thông tin nhanh">
        <span class="fact">AI &amp; Python</span><span class="fact">FastAPI</span><span class="fact">Research</span>
      </div>
      <nav class="links" aria-label="Liên kết cá nhân">
        <a class="link-btn primary" href="https://www.facebook.com/vltruong01/" target="_blank" rel="noopener noreferrer"><img src="/static/icons/facebook.png" width="23" height="23" alt="">Facebook</a>
        <a class="link-btn" href="https://zalo.me/84869183424" target="_blank" rel="noopener noreferrer"><img src="/static/icons/zalo.png" width="23" height="23" alt="">Zalo</a>
        <a class="link-btn pink" href="https://www.instagram.com/102vl_truong" target="_blank" rel="noopener noreferrer"><img src="/static/icons/instagram-optimized.png" width="23" height="23" alt="">Instagram</a>
        <a class="link-btn" href="https://www.tiktok.com/@vltruong1" target="_blank" rel="noopener noreferrer"><img src="/static/icons/tiktok.png" width="23" height="23" alt="">TikTok</a>
        <button class="link-btn green" type="button" onclick="openModal('bankModal')"><span class="symbol" aria-hidden="true">💳</span>Tài khoản thanh toán</button>
        <button class="link-btn indigo" type="button" onclick="openChatbot()"><span class="symbol" aria-hidden="true">🤖</span>Chatbot giới thiệu VLT</button>
        <button class="link-btn" type="button" onclick="copyEmail()"><span class="symbol" aria-hidden="true">✉</span>Copy email liên hệ</button>
      </nav>
      <footer>© 2026 Vương Lộc Trường · All rights reserved</footer>
    </section>
  </main>

  <div id="chatbotModal" class="modal" role="dialog" aria-modal="true" aria-labelledby="chatbotTitle" onclick="backdropClose(event, 'chatbotModal')">
    <div class="modal-card">
      <button class="modal-close" type="button" aria-label="Đóng" onclick="closeModal('chatbotModal')">×</button>
      <h2 id="chatbotTitle">Đang đánh thức chatbot</h2>
      <p id="chatbotStatus" class="modal-text">Chatbot vừa được đánh thức. Bạn sẽ được chuyển tới đó khi sẵn sàng.</p>
      <div class="countdown">Còn <span id="count">20</span> giây</div>
      <div class="progress" aria-hidden="true"><div id="bar" class="progress-bar"></div></div>
      <div class="modal-actions"><button class="small-btn" type="button" onclick="closeModal('chatbotModal')">Để sau</button></div>
    </div>
  </div>
  <div id="bankModal" class="modal" role="dialog" aria-modal="true" aria-labelledby="bankTitle" onclick="backdropClose(event, 'bankModal')">
    <div class="modal-card">
      <button class="modal-close" type="button" aria-label="Đóng" onclick="closeModal('bankModal')">×</button>
      <h2 id="bankTitle">Tài khoản thanh toán</h2>
      <div class="bank-row"><div class="bank-name"><img src="/static/icons/bidv.png" width="25" height="25" alt="">BIDV</div><button class="small-btn success" type="button" onclick="showQR('/static/qr/qr_bidv.jpg')">Xem QR</button></div>
      <div class="bank-row"><div class="bank-name"><img src="/static/icons/momo.png" width="25" height="25" alt="">MoMo</div><button class="small-btn success" type="button" onclick="showQR('/static/qr/qr_momo.jpg')">Xem QR</button></div>
    </div>
  </div>
  <div id="qrModal" class="modal" role="dialog" aria-modal="true" aria-labelledby="qrTitle" onclick="backdropClose(event, 'qrModal')">
    <div class="modal-card">
      <button class="modal-close" type="button" aria-label="Đóng" onclick="closeModal('qrModal')">×</button>
      <h2 id="qrTitle">QR thanh toán</h2>
      <img id="qrImage" class="qr-img" src="" alt="Mã QR thanh toán">
      <div class="modal-actions"><a id="qrDownload" class="small-btn success" href="" download>Tải QR</a><button class="small-btn" type="button" onclick="closeModal('qrModal')">Đóng</button></div>
    </div>
  </div>
  <div id="avatarModal" class="modal" role="dialog" aria-modal="true" aria-label="Ảnh đại diện" onclick="backdropClose(event, 'avatarModal')">
    <div class="modal-card"><button class="modal-close" type="button" aria-label="Đóng" onclick="closeModal('avatarModal')">×</button><img class="avatar-large" src="/static/avatarcuatoi.jpg" alt="Ảnh đại diện của Vương Lộc Trường"></div>
  </div>
  <div id="toast" class="toast" role="status">Đã copy email</div>

  <script>
    const CHATBOT_URL = "https://vlt-chatbot.fly.dev/";
    const CONTACT_EMAIL = "vuongloctruong95@gmail.com";
    let chatbotTimer = null;
    let chatbotPoll = null;
    let redirected = false;
    function openModal(id) {
      const modal = document.getElementById(id);
      modal.classList.add("is-open");
      modal.querySelector(".modal-close")?.focus();
    }
    function closeModal(id) {
      document.getElementById(id).classList.remove("is-open");
      if (id === "chatbotModal") {
        clearInterval(chatbotTimer); clearInterval(chatbotPoll);
        chatbotTimer = null; chatbotPoll = null;
      }
    }
    function backdropClose(event, id) { if (event.target.id === id) closeModal(id); }
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        const openModalElement = document.querySelector(".modal.is-open");
        if (openModalElement) closeModal(openModalElement.id);
      }
    });
    function showQR(path) {
      document.getElementById("qrImage").src = path;
      document.getElementById("qrDownload").href = path;
      openModal("qrModal");
    }
    function goToChatbot() {
      if (redirected) return;
      redirected = true;
      clearInterval(chatbotTimer); clearInterval(chatbotPoll);
      window.location.assign(CHATBOT_URL);
    }
    function openChatbot() {
      openModal("chatbotModal");
      if (chatbotTimer || chatbotPoll) return;
      let seconds = 20;
      const count = document.getElementById("count");
      const bar = document.getElementById("bar");
      const status = document.getElementById("chatbotStatus");
      const poll = () => fetch(CHATBOT_URL + "health?t=" + Date.now(), { cache: "no-store" })
        .then((response) => { if (response.ok) { status.textContent = "Chatbot đã sẵn sàng."; bar.style.width = "100%"; setTimeout(goToChatbot, 300); } })
        .catch(() => {});
      poll();
      chatbotPoll = setInterval(poll, 1500);
      chatbotTimer = setInterval(() => {
        seconds = Math.max(0, seconds - 1);
        count.textContent = seconds;
        bar.style.width = ((1 - seconds / 20) * 100) + "%";
        if (seconds === 0) goToChatbot();
      }, 1000);
    }
    async function copyEmail() {
      try { await navigator.clipboard.writeText(CONTACT_EMAIL); }
      catch (_) { window.prompt("Sao chép email:", CONTACT_EMAIL); return; }
      const toast = document.getElementById("toast");
      toast.classList.add("show");
      setTimeout(() => toast.classList.remove("show"), 1800);
    }
  </script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    return HTMLResponse(HTML, headers={"Cache-Control": "public, max-age=60, s-maxage=60"})


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.middleware("http")
async def cache_static_files(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/static/"):
        response.headers.setdefault("Cache-Control", "public, max-age=86400, s-maxage=86400")
    return response
