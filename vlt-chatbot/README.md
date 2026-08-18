# VLT Personal RAG Chatbot

A CPU-only personal knowledge chatbot built with FastAPI, SentenceTransformer embeddings, cosine similarity, and markdown files.

This project does not use OpenAI API, Gemini API, Claude API, paid AI APIs, GPU, Redis, PostgreSQL, or a cloud vector database.

## Architecture

```text
Question
-> Legacy FAQ exact match
-> Legacy intent keyword match
-> Query embedding
-> Semantic retrieval
-> Top-K markdown knowledge chunks
-> Grounded answer composer
-> JSON response
```

The chatbot keeps the original deterministic FAQ/intent answers first. If a question does not match the original profile rules, it falls back to the RAG-style markdown retrieval layer. It does not use an LLM.

## Code Structure

```text
app.py
chatbot/
  knowledge.py   # load markdown documents and create chunks
  legacy.py      # original FAQ and intent answers from profile.json
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
    lifestyle.md
    favorites.md
```

## Retrieval Pipeline

At startup:

1. Load all `data/knowledge/*.md` files.
2. Split markdown into chunks.
3. Attach metadata to each chunk: `id`, `title`, `category`, `content`, `source`.
4. Encode all chunks once with `sentence-transformers/all-MiniLM-L6-v2`.
5. Keep embeddings in memory.

Per request:

1. Try exact FAQ and intent matching from `data/profile.json`.
2. If no legacy answer is found, encode the user question.
3. Compute cosine similarity against cached chunk embeddings.
4. Select Top-K chunks.
5. Compose an answer from retrieved content.
6. Return fallback if confidence is low.

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

To preserve or update fixed answers and suggestion-compatible FAQ content, edit `data/profile.json`.

For lifestyle/personality details, edit `data/knowledge/lifestyle.md` and `data/knowledge/favorites.md`.

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
