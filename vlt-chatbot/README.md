# Personal Chatbot (FastAPI)

Một chatbot cực đơn giản để trả lời các câu hỏi cơ bản về **bản thân bạn**.

## Chạy nhanh (local)
```bash
pip install -r requirements.txt
uvicorn app:app --reload
# mở http://127.0.0.1:8000
```

## Cách chỉnh nội dung
- Sửa file `data/profile.json`:
  - `intents`: danh sách intent dựa trên **keywords** → trả lời cố định (nhanh & chắc).
  - `qa`: danh sách **câu hỏi - câu trả lời** mẫu. Hệ thống sẽ dùng TF‑IDF để tìm câu gần nhất (tự động).
  - `fallback`: câu trả lời dùng khi không khớp gì.

> Tip: thêm từ khóa tiếng Việt *và* tiếng Anh/Pháp/Trung nếu bạn hay được hỏi đa ngôn ngữ.

## Gọi API
```bash
curl -X POST http://127.0.0.1:8000/ask -H "Content-Type: application/json" -d '{"question": "Bạn tên gì?"}'
```

## Tùy biến
- Env var `PROFILE_PATH` để trỏ tới file dữ liệu khác.
- Thay `threshold` trong hàm `semantic_match` để bắt khớp dễ/khó hơn.
- Thêm giao diện web đẹp hơn bằng bất kỳ framework frontend nào (React/Vue, v.v.).

## Bảo mật & riêng tư
- Dự án này **không** lưu nhật ký câu hỏi. Nếu triển khai online, cân nhắc ẩn thông tin nhạy cảm (email/sđt) hoặc trả qua kênh riêng.
