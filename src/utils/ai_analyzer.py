import requests
import json
import re
from .. import config

class AIAnalyzer:
    """
    Utility class to interact with OpenAI API for activity analysis.
    """
    def __init__(self):
        self.api_key = config.OPENAI_API_KEY
        self.model = "gpt-4o-mini" # Fast and cheap for this task
        self.url = "https://api.openai.com/v1/chat/completions"

    def analyze_activities(self, activities, training_points_summary, user_profile=None):
        """
        Analyze activities and compare with training point criteria and user schedule.
        Returns a dict: {"summary": str, "recommendations": list}
        """
        if not self.api_key:
            print("OpenAI API Key is missing.")
            return {"summary": "", "recommendations": []}

        user_info = f"Mô tả bản thân: {user_profile.get('self_description', 'Không có')}\nThời khóa biểu: {user_profile.get('timetable', 'Không có')}" if user_profile else "Không có thông tin cá nhân."

        # Strip non-serializable objects (like datetime) before sending to AI
        serializable_activities = []
        for a in activities:
            clean_act = {k: v for k, v in a.items() if not k.startswith('_')}
            serializable_activities.append(clean_act)

        prompt = f"""
Bạn là một trợ lý thông minh giúp sinh viên Đại học Bách khoa Hà Nội (HUST).
Tôi sẽ cung cấp danh sách các hoạt động ngoại khóa mới, tóm tắt điểm rèn luyện hiện tại và thông tin cá nhân (bao gồm thời khóa biểu).

Thông tin người dùng:
{user_info}

Dữ liệu điểm rèn luyện (Các hạng mục cần thêm điểm):
{json.dumps(training_points_summary, ensure_ascii=False, indent=2)}

Danh sách hoạt động mới:
{json.dumps(serializable_activities, ensure_ascii=False, indent=2)}

Nhiệm vụ của bạn:
1. Phân tích TẤT CẢ các hoạt động.
2. Viết một đoạn TỔNG HỢP (summary) ngắn gọn (khoảng 3-5 câu) về những hoạt động TỐT NHẤT mà sinh viên nên tham gia ngay.
3. Trong đoạn tổng hợp, hãy liệt kê các đường link đăng ký hoặc form khảo sát (nếu tìm thấy trong dữ liệu hoạt động).
4. Đánh giá chi tiết từng hoạt động.
5. Trả về kết quả dưới dạng JSON object:
   - "summary": Đoạn tổng hợp (tiếng Việt, có thể dùng HTML cơ bản như <b>, <a>).
   - "recommendations": Danh sách các đối tượng:
     - "activity_id": ID của hoạt động.
     - "reason": Phân tích lý do (ngắn gọn, tiếng Việt).
     - "category_name": Tên hạng mục điểm rèn luyện.
     - "is_online": Boolean.

Chỉ trả về mã JSON, không giải thích gì thêm.
"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": { "type": "json_object" }
        }

        try:
            response = requests.post(self.url, headers=headers, json=payload, timeout=45)
            response.raise_for_status()
            result = response.json()
            text = result['choices'][0]['message']['content']
            data = json.loads(text)
            
            summary = data.get("summary", "")
            recs = data.get("recommendations", [])
            return {"summary": summary, "recommendations": recs}
        except Exception as e:
            print(f"Error calling OpenAI API for activities: {e}")
            return {"summary": "", "recommendations": []}

    def analyze_scholarships(self, scholarships, user_profile=None):
        """
        Analyze scholarships and match with user self-description.
        Returns a dict: {"summary": str, "matches": list}
        """
        if not self.api_key:
            return {"summary": "", "matches": []}

        user_info = f"Mô tả bản thân: {user_profile.get('self_description', 'Không có')}" if user_profile else "Không có thông tin cá nhân."

        # Strip non-serializable objects (like datetime)
        serializable_scholarships = []
        for s in scholarships:
            clean_s = {k: v for k, v in s.items() if not k.startswith('_')}
            serializable_scholarships.append(clean_s)

        prompt = f"""
Bạn là một chuyên gia về học bổng tại Đại học Bách khoa Hà Nội.
Tôi sẽ cung cấp danh sách học bổng mới và mô tả về bản thân sinh viên.

Thông tin sinh viên:
{user_info}

Danh sách học bổng:
{json.dumps(serializable_scholarships, ensure_ascii=False, indent=2)}

Nhiệm vụ của bạn:
1. Phân tích TẤT CẢ các học bổng.
2. Viết một đoạn TỔNG HỢP (summary) ngắn gọn (3-5 câu) về những học bổng PHÙ HỢP NHẤT.
3. Trong đoạn tổng hợp, liệt kê các link đăng ký/form hoặc thông tin liên hệ quan trọng nếu có.
4. Trả về kết quả dưới dạng JSON object:
   - "summary": Đoạn tổng hợp (tiếng Việt, có thể dùng HTML cơ bản).
   - "matches": Danh sách các đối tượng:
     - "scholarship_id": ID của học bổng (DocumentId).
     - "match_score": Điểm phù hợp (0-100).
     - "reason": Giải thích tại sao phù hợp hoặc không (tiếng Việt).

Chỉ trả về mã JSON, không giải thích gì thêm.
"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": { "type": "json_object" }
        }

        try:
            response = requests.post(self.url, headers=headers, json=payload, timeout=45)
            response.raise_for_status()
            result = response.json()
            text = result['choices'][0]['message']['content']
            data = json.loads(text)
            
            summary = data.get("summary", "")
            matches = data.get("matches", [])
            return {"summary": summary, "matches": matches}
        except Exception as e:
            print(f"Error calling OpenAI API for scholarships: {e}")
            return {"summary": "", "matches": []}
    def analyze_awards(self, awards, user_profile=None):
        """
        Analyze awards from QLĐT and match with user profile.
        Returns a dict: {"summary": str, "matches": list}
        """
        if not self.api_key:
            return {"summary": "", "matches": []}

        user_info = f"Mô tả bản thân: {user_profile.get('self_description', 'Không có')}" if user_profile else "Không có thông tin cá nhân."

        # Strip non-serializable objects
        serializable_awards = []
        for a in awards:
            clean_a = {k: v for k, v in a.items() if not k.startswith('_')}
            serializable_awards.append(clean_a)

        prompt = f"""
Bạn là một chuyên gia về học bổng và giải thưởng tại Đại học Bách khoa Hà Nội.
Tôi sẽ cung cấp danh sách học bổng/giải thưởng mới từ cổng thông tin QLĐT và mô tả về bản thân sinh viên.

Thông tin sinh viên:
{user_info}

Danh sách học bổng/giải thưởng QLĐT:
{json.dumps(serializable_awards, ensure_ascii=False, indent=2)}

Nhiệm vụ của bạn:
1. Phân tích TẤT CẢ các mục.
2. Viết một đoạn TỔNG HỢP (summary) ngắn gọn (3-5 câu) về những mục PHÙ HỢP NHẤT hoặc đáng chú ý nhất.
3. Trong đoạn tổng hợp, liệt kê các link đăng ký hoặc thông tin quan trọng nếu có.
4. Trả về kết quả dưới dạng JSON object:
   - "summary": Đoạn tổng hợp (tiếng Việt, có thể dùng HTML cơ bản).
   - "matches": Danh sách các đối tượng:
     - "award_id": ID của giải thưởng (id).
     - "match_score": Điểm phù hợp (0-100).
     - "reason": Giải thích tại sao phù hợp hoặc không (tiếng Việt).

Chỉ trả về mã JSON, không giải thích gì thêm.
"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": { "type": "json_object" }
        }

        try:
            response = requests.post(self.url, headers=headers, json=payload, timeout=45)
            response.raise_for_status()
            result = response.json()
            text = result['choices'][0]['message']['content']
            data = json.loads(text)
            
            summary = data.get("summary", "")
            matches = data.get("matches", [])
            return {"summary": summary, "matches": matches}
        except Exception as e:
            print(f"Error calling OpenAI API for awards: {e}")
            return {"summary": "", "matches": []}
    def analyze_training_strategy(self, training_points_summary, activities, user_profile=None):
        """
        Generate a strategic advice for training points based on current gaps and available activities.
        """
        if not self.api_key:
            return "Vui lòng cấu hình OpenAI API Key để nhận được tư vấn chiến lược."

        user_info = f"Mô tả bản thân: {user_profile.get('self_description', 'Không có')}\nThời khóa biểu: {user_profile.get('timetable', 'Không có')}" if user_profile else "Không có thông tin cá nhân."
        
        serializable_activities = []
        for a in activities:
            clean_act = {k: v for k, v in a.items() if not k.startswith('_')}
            serializable_activities.append(clean_act)

        prompt = f"""
Bạn là một cố vấn học tập tại Đại học Bách khoa Hà Nội.
Hãy phân tích bảng điểm rèn luyện hiện tại, danh sách các hoạt động đang mở và thời khóa biểu của sinh viên để đưa ra chiến lược tối ưu nhất.

Thông tin người dùng:
{user_info}

Bảng điểm rèn luyện (Hạng mục và điểm hiện tại):
{json.dumps(training_points_summary, ensure_ascii=False, indent=2)}

Các hoạt động đang diễn ra:
{json.dumps(serializable_activities, ensure_ascii=False, indent=2)}

Nhiệm vụ:
1. Nhận diện các hạng mục điểm rèn luyện còn thiếu nhiều điểm nhất (ưu tiên hạng mục lớn).
2. Đối chiếu với danh sách hoạt động để chỉ ra các hoạt động PHÙ HỢP NHẤT giúp bù đắp các khoảng trống đó.
3. Kiểm tra thời gian của hoạt động có bị trùng với thời khóa biểu hay không.
4. Viết một đoạn tư vấn chiến lược (3-5 câu) thật súc tích, chuyên nghiệp và có tính hành động cao (Call to Action).
5. Sử dụng HTML cơ bản (<b>, <ul>, <li>) để trình bày đẹp mắt.

Trả về một chuỗi văn bản HTML (không bao gồm thẻ <html> hay <body>).
"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}]
        }

        try:
            response = requests.post(self.url, headers=headers, json=payload, timeout=45)
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']
        except Exception as e:
            print(f"Error calling OpenAI API for training strategy: {e}")
            return "Không thể kết nối với trí tuệ nhân tạo để đưa ra chiến lược lúc này."
