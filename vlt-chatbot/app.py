from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, List, Tuple
import json, os, re, unicodedata
from fastapi.middleware.cors import CORSMiddleware

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer, util

# ---------- Load profile & Q&A ----------
DATA_PATH = os.environ.get("PROFILE_PATH", "data/profile.json")
with open(DATA_PATH, "r", encoding="utf-8") as f:
    PROFILE = json.load(f)

INTENTS: Dict[str, Dict] = {intent["name"]: intent for intent in PROFILE.get("intents", [])}

# chỉ lấy những item có đủ "q" và "a"
QA_ALL: List[Tuple[str, str]] = []
for item in PROFILE.get("qa", []):
    if "vi" in item and "q" in item["vi"] and "a" in item["vi"]:
        QA_ALL.append((item["vi"]["q"], item["vi"]["a"]))
    if "en" in item and "q" in item["en"] and "a" in item["en"]:
        QA_ALL.append((item["en"]["q"], item["en"]["a"]))

FALLBACK_VI = PROFILE.get("fallback", {}).get("vi", "Xin lỗi, mình chưa rõ câu hỏi. Bạn có thể hỏi cụ thể hơn không?")
FALLBACK_EN = PROFILE.get("fallback", {}).get("en", "Sorry, I'm not sure I understood. Could you ask more specifically?")

# ---------- Helpers ----------
def strip_diacritics(s: str) -> str:
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(c for c in nfkd if not unicodedata.combining(c))

def normalize(text: str) -> str:
    t = strip_diacritics(text.lower().strip())
    t = re.sub(r"\s+", " ", t)
    return t

def is_english(s: str) -> bool:
    try:
        s.encode("ascii")
        return True
    except Exception:
        return False

# Split QA by language
QA_VI: List[Tuple[str, str]] = []
QA_EN: List[Tuple[str, str]] = []
for q, a in QA_ALL:
    if is_english(q):
        QA_EN.append((q, a))
    else:
        QA_VI.append((q, a))

# ---------- Intent patterns ----------
INTENT_PATTERNS = {}
for intent_name, intent in INTENTS.items():
    pats = []
    for lang in ["vi", "en"]:
        if lang in intent.get("keywords", {}):
            for kw in intent["keywords"][lang]:
                nk = normalize(kw)
                if not nk:
                    continue
                if len(nk) <= 2 or " " not in nk:
                    pats.append(re.compile(rf"(?:^|\W){re.escape(nk)}(?:$|\W)"))
                else:
                    pats.append(f" {nk} ")
    INTENT_PATTERNS[intent_name] = pats

def match_intent(question: str) -> str:
    q = " " + normalize(question) + " "
    for intent_name, pats in INTENT_PATTERNS.items():
        for pat in pats:
            if isinstance(pat, str):
                if pat in q:
                    return intent_name
            else:
                if pat.search(q):
                    return intent_name
    return ""

def answer_for_intent(intent_name: str, lang: str) -> str:
    if not intent_name:
        return ""
    intent = INTENTS.get(intent_name, {})
    if lang == "en":
        return intent.get("answer", {}).get("en", "") or intent.get("answer", "")
    return intent.get("answer", {}).get("vi", "") or intent.get("answer", "")

# ---------- Semantic indexes ----------
VECTORIZER_VI = TfidfVectorizer(ngram_range=(1, 2), lowercase=True) if QA_VI else None
VECTORIZER_EN = TfidfVectorizer(ngram_range=(1, 2), lowercase=True) if QA_EN else None

MATRIX_VI = VECTORIZER_VI.fit_transform([q for q, _ in QA_VI]) if QA_VI and VECTORIZER_VI else None
MATRIX_EN = VECTORIZER_EN.fit_transform([q for q, _ in QA_EN]) if QA_EN and VECTORIZER_EN else None

EMBED_MODEL = None
QA_EMBEDS_VI = None
QA_EMBEDS_EN = None

def ensure_embed_model():
    global EMBED_MODEL, QA_EMBEDS_VI, QA_EMBEDS_EN
    if EMBED_MODEL is None:
        EMBED_MODEL = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        if QA_VI:
            QA_EMBEDS_VI = EMBED_MODEL.encode([q for q, _ in QA_VI], convert_to_tensor=True)
        if QA_EN:
            QA_EMBEDS_EN = EMBED_MODEL.encode([q for q, _ in QA_EN], convert_to_tensor=True)

def embedding_match(question: str, lang: str, threshold: float = 0.55) -> str:
    ensure_embed_model()
    if lang == "vi" and QA_VI and QA_EMBEDS_VI is not None:
        q_emb = EMBED_MODEL.encode([question], convert_to_tensor=True)
        sims = util.cos_sim(q_emb, QA_EMBEDS_VI)[0]
        best_idx = int(sims.argmax())
        if float(sims[best_idx]) >= threshold:
            return QA_VI[best_idx][1]
    if lang == "en" and QA_EN and QA_EMBEDS_EN is not None:
        q_emb = EMBED_MODEL.encode([question], convert_to_tensor=True)
        sims = util.cos_sim(q_emb, QA_EMBEDS_EN)[0]
        best_idx = int(sims.argmax())
        if float(sims[best_idx]) >= threshold:
            return QA_EN[best_idx][1]
    return ""

def semantic_match(question: str, lang: str, threshold: float = 0.35) -> str:
    if lang == "vi" and QA_VI and MATRIX_VI is not None and VECTORIZER_VI:
        try:
            sims = cosine_similarity(VECTORIZER_VI.transform([question]), MATRIX_VI)[0]
            best_idx = sims.argmax()
            if sims[best_idx] >= threshold:
                return QA_VI[best_idx][1]
        except:
            pass
    if lang == "en" and QA_EN and MATRIX_EN is not None and VECTORIZER_EN:
        try:
            sims = cosine_similarity(VECTORIZER_EN.transform([question]), MATRIX_EN)[0]
            best_idx = sims.argmax()
            if sims[best_idx] >= threshold:
                return QA_EN[best_idx][1]
        except:
            pass
    return ""

def fallback(lang: str) -> str:
    return FALLBACK_EN if lang == "en" else FALLBACK_VI

# ---------- FastAPI app ----------
app = FastAPI(title="Personal Chatbot", version="0.5.0-no-auto-translate")

# 👇 Bật CORS
origins = [
    "https://vlt-infor.fly.dev",   # cho phép frontend infor gọi API
    "http://localhost:8000",       # khi dev local
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # domain được phép
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def _health():
    return {"status": "ok"}

app.mount("/static", StaticFiles(directory="static"), name="static")

class AskBody(BaseModel):
    question: str
    lang: str = "vi"

HTML_FORM = """
<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Chatbot của VLTrường</title>
  <link rel="icon" href="/static/cutechatbot.png?v=3">
  <style>
  :root{
    --bg:#0b1220; --panel:#121a2b; --text:#eaf0ff; --muted:#95a1c6; --accent:#4c7fff;
    --bubble-user:#3558ff; --bubble-bot:#1a2438; --border:#26314a;
    --toggle-bg: #2d3748;
    --toggle-checked-bg: var(--accent);
    --toggle-handle: white;
    --toggle-border: var(--border);
  }
  body{margin:0; background:var(--bg); color:var(--text); font-family:system-ui,Arial; height:100vh; display:flex; flex-direction:column;}
  header{padding:14px 18px; border-bottom:1px solid var(--border); background:var(--panel); display:flex; justify-content:space-between; align-items:center;}
  header .title{ font-weight:700; }
  header .subtitle{ color:var(--muted); font-size:13px; }

  /* ==== màu link trong chat ==== */
  .bubble a {
    color: #4ade80;          /* xanh lá sáng */
    font-weight: 600;
    text-decoration: underline;
  }
  .bubble a:visited {
    color: #a78bfa;          /* tím lilac nhạt */
  }
  .bubble a:hover {
    color: #f87171;          /* đỏ nhạt khi hover */
  }
  .bubble a:active {
    color: #ef4444;          /* đỏ đậm khi click */
  }
  /* ============================= */

  .lang-switch {display: flex; align-items: center; gap: 12px;}
  .lang-label {font-size: 14px; color: var(--muted); font-weight: 500;}
  .toggle-container {position: relative; display: inline-block; width: 70px; height: 30px; background: var(--toggle-bg); border: 1px solid var(--toggle-border); border-radius: 25px; cursor: pointer; overflow: hidden;}
  .toggle-option {position: absolute; top: 0; width: 50%; height: 100%; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 600; z-index: 2; transition: color 0.3s ease;}
  .toggle-option.vn {left: 0; color: var(--text);}
  .toggle-option.en {right: 0; color: var(--muted);}
  .toggle-slider {position: absolute; top: 2px; left: 2px; width: 33px; height: 26px; background: var(--toggle-checked-bg); border-radius: 20px; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); z-index: 1;}
  .toggle-container.english .toggle-slider {left: calc(100% - 35px);}
  .toggle-container.english .toggle-option.vn {color: var(--muted);}
  .toggle-container.english .toggle-option.en {color: var(--text);}
  .toggle-container:hover {border-color: var(--accent);}
  .toggle-checkbox {position: absolute; opacity: 0; width: 0; height: 0;}

  .container{flex:1; display:flex; justify-content:center; align-items:stretch; padding:12px;}
  .chat{width:min(900px,100%); display:flex; flex-direction:column; border:1px solid var(--border); border-radius:16px; overflow:hidden; background:var(--panel);}
  .messages{flex:1; padding:16px; overflow-y:auto; scroll-behavior:smooth; display:flex; flex-direction:column; gap:12px; max-height:450px;}
  .bubble{max-width:75%; padding:12px 14px; border-radius:14px; line-height:1.45; white-space:pre-wrap; box-shadow:0 3px 10px rgba(0,0,0,.15);}
  .row{ display:flex; gap:10px; align-items:flex-end; }
  .row.user{ justify-content:flex-end; }
  .row.user .bubble{ background:var(--bubble-user); }
  .row.bot  .bubble{ background:var(--bubble-bot); border:1px solid var(--border); }
  .avatar{width:32px; height:32px; border-radius:50%; overflow:hidden; flex:0 0 auto; border:1px solid var(--border); background:#243152;}
  .avatar img{ width:100%; height:100%; object-fit:cover; display:block; }
  .composer{border-top:1px solid var(--border); padding:12px; background:var(--panel); display:flex; gap:10px;}
  textarea{flex:1; resize:none; background:#0e1526; color:var(--text); border:1px solid var(--border); border-radius:12px; padding:12px 14px; min-height:48px; outline:none;}
  button{background:var(--accent); color:white; border:none; border-radius:12px; padding:12px 16px; font-weight:600; cursor:pointer;}
  .footer-note {color: var(--muted); font-size: 12px; padding: 4px 12px; border-top: 1px dashed var(--border); display: flex; justify-content: center; align-items: center;}
  .suggest-wrap {display: flex; gap: 6px; align-items: center; margin: 17px;}
  select {background:#0e1526; color:#cfe0ff; border:1px solid var(--border); border-radius:8px; padding:4px 8px; font-size:12px; max-width:100%;}
  </style>
</head>
<body>
  <header>
    <div>
      <div id="headerTitle" class="title">🤖Đây là Chatbot của Vương Lộc Trường :3</div>
      <div id="headerSubtitle" class="subtitle">Bạn có thể hỏi về: quê quán, học vấn, sở thích, liên hệ…</div>
    </div>
    <div class="lang-switch">
      <span class="lang-label">Language:</span>
      <label class="toggle-container" id="toggleContainer">
        <input type="checkbox" class="toggle-checkbox" id="langToggle">
        <div class="toggle-slider"></div>
        <div class="toggle-option vn">VN</div>
        <div class="toggle-option en">EN</div>
      </label>
    </div>
  </header>

  <div class="container">
    <div class="chat">
      <div id="messages" class="messages">
        <div class="row bot">
          <div class="avatar"><img src="/static/cutechatbot.png?v=3" alt="bot"></div>
          <div class="bubble">Chào bạn! Mình là chatbot giới thiệu về Vương Lộc Trường. Bạn muốn hỏi điều gì? 😊<br>Đây là toàn bộ infor của mình bạn có thể click vào nhé <a href="https://vlt-infor.fly.dev/" target="_blank" rel="noopener">vlt-infor.fly.dev</a></div>
        </div>
      </div>

      <div class="composer">
        <textarea id="input" placeholder="Nhập câu hỏi… (Enter để gửi)"></textarea>
        <button id="sendBtn">Gửi</button>
      </div>
      <div class="footer-note">
        <div class="suggest-wrap">
          <span>Gợi ý câu hỏi:</span>
          <select id="suggestSelect">
            <option value="">Chọn một câu hỏi gợi ý</option>
          </select>
        </div>
      </div>
    </div>
  </div>

  <script>
  const $messages = document.getElementById('messages');
  const $input = document.getElementById('input');
  const $send = document.getElementById('sendBtn');
  const $langToggle = document.getElementById('langToggle');
  const $toggleContainer = document.getElementById('toggleContainer');
  const $suggest = document.getElementById('suggestSelect');

  let loadingRow = null;
  let currentLang = "vi";

  // Suggestions for both languages
  const SUGGESTIONS_VI = [
    "Bạn là ai?","Bạn tên đầy đủ là gì?","Bạn bao nhiêu tuổi?","Bạn sinh ra ở đâu?",
    "Quê quán của bạn ở đâu?","Bạn học trường gì?","Bạn học ngành gì?","Bạn có tính cách thế nào?",
    "Bạn thích môn thể thao nào?","Món ăn yêu thích của bạn?","Gia đình bạn có mấy người?",
    "Triết lý sống của bạn là gì?","Bạn nói được những ngôn ngữ nào?","Bạn có bạn gái chưa?",
    "Ước mơ nghề nghiệp của bạn?","Email của bạn?","Số điện thoại của bạn?"
  ];

  const SUGGESTIONS_EN = [
    "Who are you?","What is your full name?","How old are you?","Where were you born?",
    "Where is your hometown?","Which university did you study?","What was your major?",
    "What is your personality like?","What sport do you like?","What is your favorite food?",
    "How many people are in your family?","What is your life motto?","What languages do you speak?",
    "Do you have a girlfriend?","What is your career goal?","What is your email?",
    "What is your phone number?"
  ];

  function populateSelect(){
    while($suggest.options.length > 1){ $suggest.remove(1); }
    const list = currentLang === 'en' ? SUGGESTIONS_EN : SUGGESTIONS_VI;
    list.forEach(q=>{
      const opt = document.createElement('option');
      opt.value = q; opt.textContent = q;
      $suggest.appendChild(opt);
    });
  }

  function setLang(lang){
    currentLang = lang;
    $langToggle.checked = (lang === 'en');
    
    if (lang === 'en') {
      $toggleContainer.classList.add('english');
      // đổi title/subtitle
      document.getElementById('headerTitle').textContent = "🤖This is Vuong Loc Truong’s Chatbot :3";
      document.getElementById('headerSubtitle').textContent = "You can ask about: hometown, education, hobbies, contact…";
      // đổi UI khác
      $input.placeholder = "Type a question… (Press Enter to send)";
      $send.textContent = "Send";
      document.querySelector('.footer-note span').textContent = "Suggested questions:";
      $suggest.options[0].textContent = "Pick a suggestion";
    } else {
      $toggleContainer.classList.remove('english');
      // đổi title/subtitle
      document.getElementById('headerTitle').textContent = "🤖Đây là Chatbot của Vương Lộc Trường :3";
      document.getElementById('headerSubtitle').textContent = "Bạn có thể hỏi về: quê quán, học vấn, sở thích, liên hệ…";
      // đổi UI khác
      $input.placeholder = "Nhập câu hỏi… (Enter để gửi)";
      $send.textContent = "Gửi";
      document.querySelector('.footer-note span').textContent = "Gợi ý câu hỏi:";
      $suggest.options[0].textContent = "Chọn một câu hỏi gợi ý";
    }
    populateSelect();
  }

  // Click handler for toggle
  $toggleContainer.addEventListener('click', (e) => {
    e.preventDefault();
    const newLang = currentLang === 'vi' ? 'en' : 'vi';
    setLang(newLang);
  });

  // Also handle checkbox change for accessibility
  $langToggle.addEventListener('change', () => {
    setLang($langToggle.checked ? 'en' : 'vi');
  });

  function addMessage(text, who="bot"){
    const row = document.createElement('div');
    row.className = 'row ' + (who === 'user' ? 'user' : 'bot');
    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    bubble.textContent = text;

    if(who === 'user'){
      row.appendChild(bubble);
    } else {
      const av = document.createElement('div');
      av.className = 'avatar';
      const img = document.createElement('img');
      img.src = '/static/cutechatbot.png';
      img.alt = 'bot';
      av.appendChild(img);
      row.appendChild(av);
      row.appendChild(bubble);
    }
    $messages.appendChild(row);
    $messages.scrollTop = $messages.scrollHeight;
  }

  function setLoading(on){
    $send.disabled = on;
    if(on){
      if(!loadingRow){
        const row = document.createElement('div');
        row.className = 'row bot';
        const av = document.createElement('div');
        av.className = 'avatar';
        const img = document.createElement('img');
        img.src = '/static/cutechatbot.png'; img.alt = 'bot';
        av.appendChild(img);
        const bubble = document.createElement('div');
        bubble.className = 'bubble';
        bubble.textContent = (currentLang === 'en') ? 'Thinking…' : 'Đang suy nghĩ…';
        row.appendChild(av); row.appendChild(bubble);
        $messages.appendChild(row);
        $messages.scrollTop = $messages.scrollHeight;
        loadingRow = row;
      }
    } else {
      if(loadingRow){ loadingRow.remove(); loadingRow = null; }
    }
  }

  async function ask(q){
    try{
      const resp = await fetch('/ask', {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ question: q, lang: currentLang })
      });
      const data = await resp.json();
      return data.answer || (currentLang === 'en' ? "Sorry, I didn't catch that." : "Xin lỗi, mình chưa rõ câu hỏi.");
    }catch(e){
      console.error(e);
      return (currentLang === 'en') ? "Connection error." : "Có lỗi kết nối.";
    }
  }

  async function onSend(){
    const q = $input.value.trim();
    if(!q) return;
    addMessage(q, 'user');
    $input.value = ""; $input.focus();

    setLoading(true);
    const a = await ask(q);
    setLoading(false);
    addMessage(a, 'bot');

    $suggest.value = "";
  }

  $suggest.addEventListener('change', ()=>{
    const q = $suggest.value;
    if(!q) return;
    $input.value = q;
    onSend();
  });

  $send.addEventListener('click', onSend);
  $input.addEventListener('keydown', (e)=>{
    if(e.key === 'Enter' && !e.shiftKey){
      e.preventDefault();
      onSend();
    }
  });

  setLang('vi');     // default VN
  populateSelect();
  </script>
  </body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_FORM

@app.post("/ask-form")
async def ask_form(q: str = Form(...), lang: str = Form("vi")):
    return JSONResponse({"answer": get_answer(q, lang)})

@app.post("/ask")
async def ask_api(body: AskBody):
    ans = get_answer(body.question, body.lang)
    return JSONResponse({"answer": ans})

def get_answer(question: str, lang: str) -> str:
    lang = "en" if lang == "en" else "vi"
    
    # Ưu tiên exact matching với các câu hỏi trong QA
    norm_question = normalize(question)
    if lang == "vi":
        for q, a in QA_VI:
            if normalize(q) == norm_question:
                return a
    else:
        for q, a in QA_EN:
            if normalize(q) == norm_question:
                return a
    
    # Sau đó mới đến intent matching
    intent_name = match_intent(question)
    if intent_name:
        ans = answer_for_intent(intent_name, lang)
        if ans:
            return ans
    
    # Cuối cùng là semantic matching
    ans = embedding_match(question, lang)
    if ans:
        return ans
        
    ans = semantic_match(question, lang)
    if ans:
        return ans
        
    return fallback(lang)

# @app.on_event("startup")
# async def _startup():
#     ensure_embed_model()

@app.middleware("http")
async def cache_headers(request, call_next):
    resp = await call_next(request)
    path = request.url.path
    if path == "/":
        resp.headers["Cache-Control"] = "no-store"
    elif path.startswith("/static/"):
        resp.headers.setdefault(
            "Cache-Control", "public, max-age=300, s-maxage=300, must-revalidate"
        )
    return resp

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)