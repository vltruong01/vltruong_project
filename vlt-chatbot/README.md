# VLT Personal RAG Chatbot

A CPU-only personal knowledge chatbot built with FastAPI, SentenceTransformer embeddings, cosine similarity, and markdown files.

This project does not use OpenAI API, Gemini API, Claude API, paid AI APIs, GPU, Redis, PostgreSQL, or a cloud vector database.

## Architecture

```text
Question
-> Query embedding
-> Semantic retrieval
-> Top-K markdown knowledge chunks
-> Grounded answer composer
-> JSON response
```

The chatbot is RAG-style, but it does not use an LLM. It retrieves relevant knowledge chunks and formats an answer only from the retrieved text.

## Code Structure

```text
app.py
chatbot/
  knowledge.py   # load markdown documents and create chunks
  retriever.py   # SentenceTransformer + cosine similarity
  composer.py    # non-LLM grounded answer composition
  utils.py       # normalization and small helpers
data/
  profile.json
  knowledge/
    about.md
    education.md
    skills.md
    projects.md
    thesis.md
    experience.md
    contact.md
    certifications.md
```

## Retrieval Pipeline

At startup:

1. Load all `data/knowledge/*.md` files.
2. Split markdown into chunks.
3. Attach metadata to each chunk: `id`, `title`, `category`, `content`, `source`.
4. Encode all chunks once with `sentence-transformers/all-MiniLM-L6-v2`.
5. Keep embeddings in memory.

Per request:

1. Encode the user question.
2. Compute cosine similarity against cached chunk embeddings.
3. Select Top-K chunks.
4. Compose an answer from retrieved content.
5. Return fallback if confidence is low.

## API

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Những công nghệ bạn sử dụng?","lang":"vi"}'
```

Response:

```json
{
  "answer": "Dựa trên dữ liệu hiện có: ...",
  "confidence": 0.85,
  "type": "semantic",
  "sources": [
    {
      "title": "Skills",
      "category": "skills",
      "source": "data/knowledge/skills.md"
    }
  ]
}
```

If confidence is low:

```json
{
  "answer": "Mình chưa có đủ thông tin để trả lời câu hỏi này.",
  "confidence": 0.12,
  "type": "unknown",
  "sources": []
}
```

## Update Knowledge

Edit markdown files in `data/knowledge/`.

Example:

```text
data/knowledge/projects.md
data/knowledge/skills.md
data/knowledge/contact.md
```

Restart the app after editing so embeddings are rebuilt from the updated markdown files.

## Run Local

```bash
pip install --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt
uvicorn app:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

## Deploy To Fly.io

The existing Fly.io configuration keeps cost low:

```toml
auto_start_machines = true
min_machines_running = 0
```

Deploy:

```bash
fly deploy
```

The Docker image preloads the embedding model during build, so the app does not need to download the model at runtime.

## Runtime Notes

- Runs on CPU.
- Uses the lightweight `all-MiniLM-L6-v2` embedding model.
- Embeddings are generated once at startup, not on every request.
- Only the query is encoded per request.
- Best for factual profile, portfolio, FAQ, education, skills, projects, thesis, experience, contact, and certification data.
