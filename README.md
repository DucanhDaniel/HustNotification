# 🚀 HUST Monitoring System (AI-Powered)

Hệ thống theo dõi tự động toàn diện các hoạt động, học bổng và thông tin đào tạo tại Đại học Bách khoa Hà Nội (HUST). Tích hợp trí tuệ nhân tạo (OpenAI) để phân tích, đưa ra chiến lược tối ưu điểm rèn luyện và cá nhân hóa lộ trình sinh viên.

---

## ✨ Tính năng nổi bật

### 1. 📡 Giám sát đa kênh 24/7
-   **Scholarships (CTSV)**: Tự động theo dõi các nguồn học bổng mới nhất.
-   **Activities (CTSV)**: Cập nhật các hoạt động ngoại khóa đang mở đăng ký.
-   **Awards & Scholarships (QLĐT)**: Theo dõi các giải thưởng và học bổng từ cổng quản lý đào tạo.
-   **Training Points**: Theo dõi biến động điểm rèn luyện chi tiết đến từng tiêu chí.

### 2. 🤖 Trí tuệ nhân tạo (GPT-4o Mini)
-   **Chiến lược điểm rèn luyện**: Tự động phân tích các tiêu chí còn thiếu, đối chiếu với danh sách hoạt động đang mở và thời khóa biểu để đưa ra lộ trình tham gia tối ưu nhất.
-   **Phân tích sự phù hợp**: Đánh giá mức độ phù hợp của học bổng dựa trên GPA, chuyên ngành và mô tả bản thân.
-   **Cảnh báo trùng lịch**: Tự động so sánh thời gian hoạt động với **Thời khóa biểu** cá nhân để tránh đăng ký nhầm giờ học.

### 3. 📧 Báo cáo chuyên nghiệp & Định kỳ
-   **Báo cáo biến động**: Gửi email ngay lập tức khi có sự thay đổi (điểm số mới, hoạt động mới).
-   **Báo cáo định kỳ**: Gửi tổng kết điểm rèn luyện kèm lời khuyên từ AI mỗi 6 giờ (mặc định).
-   **Email HTML Cao cấp**: Định dạng rõ ràng, có thanh tiến độ (progress bar) và các huy hiệu (Online, Sắp hết hạn).

### 4. 🛡️ Độ bền bỉ & Bảo mật
-   **Cơ chế Fallback**: Tự động sử dụng dữ liệu cũ từ bộ nhớ đệm JSON nếu hệ thống trường gặp sự cố hoặc phiên đăng nhập hết hạn.
-   **Gộp Cookie thông minh**: Tự động gộp dữ liệu đăng nhập từ UI và file cookies, lọc domain để tránh lỗi header quá lớn.
-   **Đồng bộ SSO**: Tự động chia sẻ token giữa các module CTSV và QLĐT.

---

## 🛠️ Cài đặt & Sử dụng

### 1. Chuẩn bị
-   Python 3.10+ (hoặc Docker)
-   API Key OpenAI (sk-...)
-   File `credentials.json` & `token.json` cho Gmail API (nếu gửi qua Gmail).

### 2. Sử dụng với Docker (Khuyên dùng)
Hệ thống được tách thành 2 dịch vụ độc lập để tối ưu hiệu suất:
```bash
docker-compose up -d --build
```
-   **Dashboard (Port 8000)**: Giao diện cấu hình profile, timetable và upload cookies.
-   **Monitor**: Tiến trình chạy ngầm thực hiện quét dữ liệu và gửi thông báo.

### 3. Cài đặt thủ công
1.  **Cài đặt dependencies** (khuyên dùng `uv`):
    ```bash
    uv sync
    # Hoặc pip install -r requirements.txt
    ```
2.  **Cấu hình biến môi trường**:
    Tạo file `.env` và điền `OPENAI_API_KEY`.
3.  **Khởi chạy Dashboard**:
    ```bash
    python ui_server.py
    ```
4.  **Khởi chạy Monitor**:
    ```bash
    python -m src.main
    ```

---

## 🎨 Dashboard & Authentication
Truy cập `http://localhost:8000` để:
-   Nhập mô tả bản thân và dán Thời khóa biểu từ trang cá nhân.
-   Upload tệp `cookies.txt` (định dạng Netscape) xuất từ trình duyệt.
-   Đồng bộ thông tin đăng nhập tự động.

---

## 📂 Cấu trúc dự án
-   `src/monitors/`: Logic quét dữ liệu CTSV/QLĐT.
-   `src/utils/`: AI Analyzer, Email Sender, API Fetcher.
-   `src/web/`: Frontend Dashboard.
-   `data/`: Lưu trữ Profile, Timetable, Cookies và Cache dữ liệu.

---

