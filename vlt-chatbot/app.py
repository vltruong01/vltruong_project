from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from chatbot.composer import GroundedComposer
from chatbot.knowledge import KnowledgeChunk, load_knowledge
from chatbot.legacy import LegacyProfileMatcher
from chatbot.retriever import SemanticRetriever


BASE_DIR = Path(__file__).resolve().parent
PROFILE_PATH = Path(os.environ.get("PROFILE_PATH", BASE_DIR / "data" / "profile.json"))
KNOWLEDGE_DIR = Path(os.environ.get("KNOWLEDGE_DIR", BASE_DIR / "data" / "knowledge"))
MODEL_NAME = os.environ.get("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
TOP_K = int(os.environ.get("TOP_K", "4"))

chunks: List[KnowledgeChunk] = []
retriever: SemanticRetriever | None = None
composer = GroundedComposer()
legacy_matcher = LegacyProfileMatcher(PROFILE_PATH)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    global chunks, retriever
    chunks = load_knowledge(KNOWLEDGE_DIR)
    retriever = SemanticRetriever(chunks, model_name=MODEL_NAME)
    yield


app = FastAPI(title="Personal RAG Chatbot", version="1.0.0-cpu-rag", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://vlt-infor.fly.dev",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


class AskBody(BaseModel):
    question: str
    lang: str = "vi"


@app.get("/health")
def health():
    return {"status": "ok", "knowledge_chunks": len(chunks), "model": MODEL_NAME}


@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_FORM


@app.post("/ask")
async def ask_api(body: AskBody):
    return JSONResponse(get_answer(body.question, body.lang))


def get_answer(question: str, lang: str = "vi") -> dict:
    legacy_answer = legacy_matcher.answer(question, lang)
    if legacy_answer:
        return {
            "answer": legacy_answer.answer,
            "confidence": legacy_answer.confidence,
            "type": legacy_answer.type,
            "sources": legacy_answer.sources,
        }

    active_retriever = retriever
    if active_retriever is None:
        return {
            "answer": "Knowledge index is still starting. Please try again in a moment.",
            "confidence": 0.0,
            "type": "startup",
            "sources": [],
        }
    results = active_retriever.search(question, top_k=TOP_K)
    answer = composer.compose(question, results, lang=lang)
    if answer.type == "unknown":
        return {
            "answer": legacy_matcher.fallback(lang),
            "confidence": answer.confidence,
            "type": answer.type,
            "sources": answer.sources,
        }
    return {
        "answer": answer.answer,
        "confidence": answer.confidence,
        "type": answer.type,
        "sources": answer.sources,
    }


@app.middleware("http")
async def cache_headers(request, call_next):
    response = await call_next(request)
    if request.url.path == "/":
        response.headers["Cache-Control"] = "no-store"
    elif request.url.path.startswith("/static/"):
        response.headers.setdefault("Cache-Control", "public, max-age=300, s-maxage=300")
    return response


HTML_FORM = """
<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>VLT RAG Chatbot</title>
  <link rel="icon" href="/static/cutechatbot.png?v=4">
  <style>
    :root {
      color-scheme: light dark;
      --bg: #f6f7fb;
      --panel: #ffffff;
      --panel-soft: #f0f3f8;
      --text: #172033;
      --muted: #667085;
      --border: #d9deea;
      --accent: #0f766e;
      --user: #0f766e;
      --bot: #eef3f2;
      --shadow: 0 20px 55px rgba(20, 35, 60, .14);
    }
    @media (prefers-color-scheme: dark) {
      :root {
        --bg: #10131a;
        --panel: #171b24;
        --panel-soft: #202633;
        --text: #edf2f7;
        --muted: #a6adbb;
        --border: #303847;
        --accent: #2dd4bf;
        --user: #0f766e;
        --bot: #202833;
        --shadow: 0 20px 55px rgba(0, 0, 0, .32);
      }
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      background: var(--bg);
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
      display: grid;
      place-items: center;
      padding: 18px;
    }
    .shell {
      width: min(980px, 100%);
      height: min(760px, calc(100vh - 36px));
      min-height: 560px;
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 18px;
      box-shadow: var(--shadow);
      display: grid;
      grid-template-rows: auto 1fr auto auto;
      overflow: hidden;
    }
    header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 14px;
      padding: 16px 18px;
      border-bottom: 1px solid var(--border);
    }
    .brand { display: flex; align-items: center; gap: 12px; min-width: 0; }
    .brand img { width: 42px; height: 42px; border-radius: 50%; border: 1px solid var(--border); }
    .title { font-weight: 750; line-height: 1.2; }
    .subtitle { color: var(--muted); font-size: 13px; margin-top: 3px; }
    .lang {
      display: inline-flex;
      background: var(--panel-soft);
      border: 1px solid var(--border);
      border-radius: 999px;
      padding: 3px;
      flex: 0 0 auto;
    }
    .lang button {
      border: 0;
      background: transparent;
      color: var(--muted);
      min-width: 42px;
      min-height: 32px;
      border-radius: 999px;
      font-weight: 700;
      cursor: pointer;
    }
    .lang button.active { background: var(--accent); color: white; }
    .messages {
      overflow-y: auto;
      padding: 18px;
      display: flex;
      flex-direction: column;
      gap: 14px;
      scroll-behavior: smooth;
    }
    .row { display: flex; gap: 10px; align-items: flex-end; }
    .row.user { justify-content: flex-end; }
    .avatar {
      width: 34px;
      height: 34px;
      border-radius: 50%;
      border: 1px solid var(--border);
      overflow: hidden;
      background: var(--panel-soft);
      flex: 0 0 auto;
    }
    .avatar img { width: 100%; height: 100%; object-fit: cover; display: block; }
    .bubble {
      width: fit-content;
      max-width: min(76%, 680px);
      padding: 12px 14px;
      border-radius: 14px;
      line-height: 1.5;
      white-space: pre-wrap;
      overflow-wrap: anywhere;
    }
    .row.user .bubble { background: var(--user); color: white; border-bottom-right-radius: 5px; }
    .row.bot .bubble { background: var(--bot); border: 1px solid var(--border); border-bottom-left-radius: 5px; }
    .meta { color: var(--muted); font-size: 12px; margin-top: 8px; }
    .chips {
      display: flex;
      gap: 8px;
      padding: 12px 18px;
      border-top: 1px solid var(--border);
      overflow-x: auto;
    }
    .chip {
      border: 1px solid var(--border);
      background: var(--panel-soft);
      color: var(--text);
      border-radius: 999px;
      padding: 9px 12px;
      white-space: nowrap;
      cursor: pointer;
      font-weight: 600;
      font-size: 13px;
    }
    .composer {
      display: flex;
      gap: 10px;
      padding: 14px 18px 18px;
      border-top: 1px solid var(--border);
    }
    textarea {
      flex: 1;
      min-height: 48px;
      max-height: 140px;
      resize: none;
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 12px 14px;
      background: var(--panel-soft);
      color: var(--text);
      outline: none;
      font: inherit;
    }
    textarea:focus { border-color: var(--accent); }
    .send {
      border: 0;
      border-radius: 12px;
      min-width: 92px;
      padding: 0 16px;
      background: var(--accent);
      color: white;
      font-weight: 750;
      cursor: pointer;
    }
    .send:disabled { opacity: .65; cursor: wait; }
    .typing { display: inline-flex; gap: 4px; align-items: center; min-width: 48px; }
    .typing span {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: var(--muted);
      animation: pulse 1s infinite ease-in-out;
    }
    .typing span:nth-child(2) { animation-delay: .15s; }
    .typing span:nth-child(3) { animation-delay: .3s; }
    @keyframes pulse { 0%, 80%, 100% { opacity: .35; transform: translateY(0); } 40% { opacity: 1; transform: translateY(-3px); } }
    @media (max-width: 640px) {
      body { padding: 0; }
      .shell { height: 100vh; min-height: 100vh; border-radius: 0; border-left: 0; border-right: 0; }
      header { align-items: flex-start; }
      .subtitle { display: none; }
      .bubble { max-width: 86%; }
      .composer { padding: 12px; }
      .send { min-width: 72px; }
    }
  </style>
</head>
<body>
  <main class="shell">
    <header>
      <div class="brand">
        <img src="/static/cutechatbot.png?v=4" alt="">
        <div>
          <div class="title" id="title">VLT Knowledge Chatbot</div>
          <div class="subtitle" id="subtitle">Hỏi về học vấn, kỹ năng, dự án, nghiên cứu và liên hệ.</div>
        </div>
      </div>
      <div class="lang" aria-label="Language">
        <button id="viBtn" class="active" type="button">VI</button>
        <button id="enBtn" type="button">EN</button>
      </div>
    </header>
    <section class="messages" id="messages" aria-live="polite"></section>
    <section class="chips" id="chips"></section>
    <form class="composer" id="form">
      <textarea id="input" rows="1" placeholder="Nhập câu hỏi..."></textarea>
      <button class="send" id="send" type="submit">Gửi</button>
    </form>
  </main>
  <script>
    const messages = document.getElementById("messages");
    const chips = document.getElementById("chips");
    const form = document.getElementById("form");
    const input = document.getElementById("input");
    const send = document.getElementById("send");
    const viBtn = document.getElementById("viBtn");
    const enBtn = document.getElementById("enBtn");
    const title = document.getElementById("title");
    const subtitle = document.getElementById("subtitle");
    let lang = "vi";
    let typingRow = null;

    const copy = {
      vi: {
        hello: "Chào bạn! Mình trả lời dựa trên knowledge base markdown của Vương Lộc Trường. Bạn muốn hỏi gì?",
        placeholder: "Nhập câu hỏi...",
        send: "Gửi",
        title: "VLT Knowledge Chatbot",
        subtitle: "Hỏi về học vấn, kỹ năng, dự án, nghiên cứu và liên hệ.",
        error: "Có lỗi kết nối. Bạn thử lại giúp mình nhé.",
        suggestions: [
          "Bạn là ai?",
          "Bạn tên đầy đủ là gì?",
          "Bạn bao nhiêu tuổi?",
          "Bạn sinh ra ở đâu?",
          "Quê quán của bạn ở đâu?",
          "Bạn học trường gì?",
          "Bạn học ngành gì?",
          "Bạn có tính cách thế nào?",
          "Bạn thích môn thể thao nào?",
          "Món ăn yêu thích của bạn?",
          "Gia đình bạn có mấy người?",
          "Triết lý sống của bạn là gì?",
          "Bạn nói được những ngôn ngữ nào?",
          "Bạn có bạn gái chưa?",
          "Ước mơ nghề nghiệp của bạn?",
          "Email của bạn?",
          "Số điện thoại của bạn?"
        ]
      },
      en: {
        hello: "Hi! I answer from Vuong Loc Truong's local markdown knowledge base. What would you like to know?",
        placeholder: "Type a question...",
        send: "Send",
        title: "VLT Knowledge Chatbot",
        subtitle: "Ask about education, skills, projects, research, and contact.",
        error: "Connection error. Please try again.",
        suggestions: [
          "Who are you?",
          "What is your full name?",
          "How old are you?",
          "Where were you born?",
          "Where is your hometown?",
          "Which university did you study?",
          "What was your major?",
          "What is your personality like?",
          "What sport do you like?",
          "What is your favorite food?",
          "How many people are in your family?",
          "What is your life motto?",
          "What languages do you speak?",
          "Do you have a girlfriend?",
          "What is your career goal?",
          "What is your email?",
          "What is your phone number?"
        ]
      }
    };

    function scrollToBottom() {
      messages.scrollTop = messages.scrollHeight;
    }

    function addMessage(text, who = "bot", meta = "") {
      const row = document.createElement("div");
      row.className = `row ${who}`;
      if (who === "bot") {
        const avatar = document.createElement("div");
        avatar.className = "avatar";
        avatar.innerHTML = '<img src="/static/cutechatbot.png?v=4" alt="">';
        row.appendChild(avatar);
      }
      const bubble = document.createElement("div");
      bubble.className = "bubble";
      bubble.textContent = text;
      if (meta) {
        const details = document.createElement("div");
        details.className = "meta";
        details.textContent = meta;
        bubble.appendChild(details);
      }
      row.appendChild(bubble);
      messages.appendChild(row);
      scrollToBottom();
    }

    function showTyping() {
      if (typingRow) return;
      typingRow = document.createElement("div");
      typingRow.className = "row bot";
      typingRow.innerHTML = '<div class="avatar"><img src="/static/cutechatbot.png?v=4" alt=""></div><div class="bubble"><div class="typing"><span></span><span></span><span></span></div></div>';
      messages.appendChild(typingRow);
      scrollToBottom();
    }

    function hideTyping() {
      if (typingRow) typingRow.remove();
      typingRow = null;
    }

    function renderChips() {
      chips.innerHTML = "";
      copy[lang].suggestions.forEach((text) => {
        const chip = document.createElement("button");
        chip.className = "chip";
        chip.type = "button";
        chip.textContent = text;
        chip.addEventListener("click", () => {
          input.value = text;
          submitQuestion();
        });
        chips.appendChild(chip);
      });
    }

    function setLang(nextLang) {
      lang = nextLang;
      viBtn.classList.toggle("active", lang === "vi");
      enBtn.classList.toggle("active", lang === "en");
      input.placeholder = copy[lang].placeholder;
      send.textContent = copy[lang].send;
      title.textContent = copy[lang].title;
      subtitle.textContent = copy[lang].subtitle;
      renderChips();
    }

    async function submitQuestion() {
      const question = input.value.trim();
      if (!question) return;
      addMessage(question, "user");
      input.value = "";
      input.focus();
      send.disabled = true;
      showTyping();
      try {
        const response = await fetch("/ask", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ question, lang })
        });
        const data = await response.json();
        const sourceText = (data.sources || []).map((s) => s.title).join(", ");
        const meta = data.type === "semantic"
          ? `confidence ${Number(data.confidence || 0).toFixed(2)}${sourceText ? " | sources: " + sourceText : ""}`
          : `confidence ${Number(data.confidence || 0).toFixed(2)}`;
        hideTyping();
        addMessage(data.answer || copy[lang].error, "bot", meta);
      } catch (error) {
        hideTyping();
        addMessage(copy[lang].error, "bot");
      } finally {
        send.disabled = false;
      }
    }

    form.addEventListener("submit", (event) => {
      event.preventDefault();
      submitQuestion();
    });
    input.addEventListener("keydown", (event) => {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        submitQuestion();
      }
    });
    viBtn.addEventListener("click", () => setLang("vi"));
    enBtn.addEventListener("click", () => setLang("en"));

    setLang("vi");
    addMessage(copy.vi.hello, "bot");
  </script>
</body>
</html>
"""
