# 🚀 HUST Monitoring System (AI-Powered)

Hệ thống theo dõi tự động các hoạt động, học bổng và thông tin đào tạo tại Đại học Bách khoa Hà Nội (HUST), tích hợp trí tuệ nhân tạo (OpenAI) để phân tích và gợi ý cá nhân hóa.

## ✨ Tính năng nổi bật

-   **📡 Giám sát đa kênh**: Tự động theo dõi Học bổng (CTSV), Hoạt động ngoại khóa (CTSV), Giải thưởng (QLĐT) và Điểm rèn luyện.
-   **🤖 AI Analysis (OpenAI)**: 
    -   Phân tích mức độ phù hợp của học bổng dựa trên hồ sơ cá nhân (GPA, mục tiêu, chuyên ngành).
    -   Đối chiếu thời gian hoạt động với **Thời khóa biểu** để cảnh báo trùng lịch.
    -   Xác định hoạt động Online/Offline và phân loại theo hạng mục điểm rèn luyện của HUST.
-   **📅 Ưu tiên Deadline**: Tự động lọc các mục hết hạn và ưu tiên hiển thị các mục **Sắp hết hạn (⏰ SẮP HẾT HẠN)** lên đầu email.
-   **🎨 Dashboard hiện đại**: Giao diện Web (FastAPI) giúp người dùng dễ dàng cấu hình hồ sơ cá nhân và thời khóa biểu.
-   **📧 Thông báo tức thì**: Gửi email định dạng HTML chuyên nghiệp, dễ nhìn.
-   **🐳 Dockerized**: Hỗ trợ chạy bằng Docker và Docker Compose chỉ với một câu lệnh.

## 🛠️ Cài đặt & Sử dụng

### 1. Chuẩn bị
-   Python 3.10+
-   File `credentials.json` từ Google Cloud Console (để sử dụng Gmail API).
-   API Key từ OpenAI.

### 2. Cài đặt thủ công
1.  Cài đặt các thư viện:
    ```bash
    pip install -r requirements.txt
    ```
2.  Tạo file `.env` từ mẫu sau:
    ```env
    OPENAI_API_KEY="your_openai_key"
    HUST_COOKIES_JSON='{"TokenCode": "...", ...}'
    QLDT_COOKIES_JSON='{"x-access-token": "...", ...}'
    ```
3.  Chạy Dashboard để nhập thông tin cá nhân:
    ```bash
    python ui_server.py
    ```
    Truy cập `http://localhost:8000` để thiết lập.
4.  Chạy hệ thống Monitor:
    ```bash
    python -m src.main
    ```

### 3. Chạy với Docker (Khuyên dùng)
Hệ thống sẽ chạy song song cả Monitor và Dashboard:
```bash
docker-compose up -d --build
```

## 📂 Cấu trúc thư mục
-   `src/monitors/`: Các module theo dõi (Scholarship, Activity, Award, Training Points).
-   `src/utils/`: Các tiện ích (AI Analyzer, Email Sender, API Fetcher).
-   `src/web/`: Giao diện Dashboard.
-   `data/`: Nơi lưu trữ dữ liệu local và hồ sơ người dùng.
-   `ui_server.py`: Backend FastAPI cho Dashboard.

## 📝 Cấu hình
-   Mọi cấu hình hệ thống (Thời gian giãn cách, Email người nhận) nằm trong `src/config.py`.
-   Các thông tin nhạy cảm nằm trong `.env`.

---
*Phát triển bởi Antigravity AI Assistant.*
