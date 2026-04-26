from ..utils.api_fetcher import APIFetcher
from ..utils.data_tracker import DataTracker
from ..utils.email_sender import send_email
from ..utils.ai_analyzer import AIAnalyzer
from .. import config
import os
import json
from datetime import datetime

def parse_hust_date(date_str):
    """Parse HUST date format DD/MM/YYYY HH:MM:SS"""
    if not date_str or date_str == 'Không rõ':
        return None
    try:
        if len(date_str.split(':')) == 2:
            return datetime.strptime(date_str, '%d/%m/%Y %H:%M')
        return datetime.strptime(date_str, '%d/%m/%Y %H:%M:%S')
    except:
        return None

def check_for_new_scholarships():
    """
    Check for new scholarships and send email if any.
    """
    fetcher = APIFetcher(base_url='https://ctsv.hust.edu.vn')
    fetcher.set_auth('bearer_token', config.HUST_TOKEN)

    # Fetch data
    body = {
        "UserCode": config.USER_CODE,
        "Semester": config.CURRENT_SEMESTER,
        "UserName": config.USER_NAME
    }

    data = fetcher.fetch(
        endpoint='/api-t/HWScholarship/GetApprovedScholarship',
        method='POST',
        headers=config.HUST_HEADERS,
        body=body
    )

    if data and isinstance(data, dict):
        scholarship_list = data.get('ScholarshipLst', [])
        print(f"Scholarships fetched successfully. Found {len(scholarship_list)} items.")
        
        # 1. Filter and Sort by Deadline
        now = datetime.now()
        valid_scholarships = []
        for s in scholarship_list:
            deadline_str = s.get('Deadline')
            deadline_dt = parse_hust_date(deadline_str)
            if not deadline_dt or deadline_dt > now:
                s['_deadline_dt'] = deadline_dt
                valid_scholarships.append(s)

        # Sort by Deadline ascending (closest first)
        valid_scholarships.sort(key=lambda x: x['_deadline_dt'] if x['_deadline_dt'] else datetime.max)
        
        # Take top 15
        new_scholarships = valid_scholarships[:15]

        if new_scholarships:
            print(f"Processing top {len(new_scholarships)} closest scholarships.")
            
            # --- AI Matching Analysis ---
            print("Analyzing scholarship matches with OpenAI AI...")
            user_profile = {}
            profile_path = 'data/user_profile.json'
            if os.path.exists(profile_path):
                with open(profile_path, 'r', encoding='utf-8') as f:
                    user_profile = json.load(f)

            analyzer = AIAnalyzer()
            ai_results = analyzer.analyze_scholarships(new_scholarships, user_profile)
            summary_text = ai_results.get("summary", "Không có tóm tắt từ AI.")
            matches = ai_results.get("matches", [])
            match_map = {str(m['scholarship_id']): m for m in matches}

            subject = f"Có {len(new_scholarships)} học bổng sắp hết hạn & phù hợp!"
            body = f"""
            <html>
            <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #d32f2f; border-bottom: 2px solid #d32f2f; padding-bottom: 10px;">🎓 Học bổng (Ưu tiên Hạn nộp gần nhất)</h2>
                
                <div style="background-color: #fffde7; padding: 20px; border-radius: 12px; border-left: 6px solid #f9a825; margin-bottom: 30px;">
                    <h3 style="color: #f9a825; margin-top: 0;">🤖 Tóm tắt & Gợi ý từ AI:</h3>
                    <div style="font-size: 15px; color: #5f5000;">{summary_text}</div>
                </div>

                <p>Chi tiết các học bổng được liệt kê dưới đây:</p>
            """
            
            for scholarship in new_scholarships:
                sid = str(scholarship.get('DocumentId'))
                title = scholarship.get('Title') or 'Không có tiêu đề'
                desc = scholarship.get('Description') or 'Không có mô tả'
                deadline = scholarship.get('Deadline') or 'Không rõ hạn nộp'
                price = scholarship.get('TotalPrice') or 'Liên hệ để biết thêm'
                quantity = scholarship.get('Quantity') or 'Không giới hạn'
                content_html = scholarship.get('Content') or '<p>Không có nội dung chi tiết.</p>'
                
                deadline_dt = scholarship.get('_deadline_dt')
                is_soon = False
                if deadline_dt:
                    is_soon = (deadline_dt - now).days < 3

                match = match_map.get(sid)
                match_html = ""
                border_style = "border: 1px solid #e0e0e0;"
                
                soon_badge = ""
                if is_soon:
                    soon_badge = '<span style="background-color: #d32f2f; color: white; padding: 3px 8px; border-radius: 4px; font-size: 11px; margin-left: 10px; vertical-align: middle;">⏰ SẮP HẾT HẠN</span>'
                    border_style = "border: 2px solid #d32f2f; box-shadow: 0 0 10px rgba(211, 47, 47, 0.2);"

                if match:
                    score = match.get('match_score', 0)
                    color = "#2e7d32" if score >= 70 else "#f9a825"
                    if not is_soon:
                        border_style = f"border: 2px solid {color}; transform: scale(1.02);"
                    match_html = f"""
                    <div style="background-color: {color}; color: white; padding: 10px; font-weight: bold; border-radius: 4px 4px 0 0;">
                        ✨ ĐỘ PHÙ HỢP: {score}%
                    </div>
                    <div style="background-color: #f1f8e9; padding: 15px; border-left: 5px solid {color}; margin-bottom: 15px; font-size: 14px;">
                        <strong>Gợi ý AI:</strong> {match.get('reason')}
                    </div>
                    """

                body += f"""
                <div style="margin-bottom: 40px; padding: 0; {border_style} border-radius: 8px; background-color: #ffffff; box-shadow: 0 4px 12px rgba(0,0,0,0.1); overflow: hidden;">
                    {match_html}
                    <div style="padding: 20px;">
                        <h3 style="color: #1976d2; margin-top: 0;">🌟 {title} {soon_badge}</h3>
                        <table style="width: 100%; border-collapse: collapse; margin-bottom: 15px;">
                            <tr><td style="padding: 5px 0; width: 120px;"><strong>💰 Giá trị:</strong></td><td>{price}</td></tr>
                            <tr><td style="padding: 5px 0;"><strong>📅 Hạn nộp:</strong></td><td style="color: #d32f2f; font-weight: bold;">{deadline}</td></tr>
                            <tr><td style="padding: 5px 0;"><strong>👥 Số lượng:</strong></td><td>{quantity}</td></tr>
                        </table>
                        
                        <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #eee;">
                            <strong style="display: block; margin-bottom: 10px; color: #555;">🔍 Nội dung chi tiết:</strong>
                            <div style="font-size: 14px; color: #444; overflow-x: auto; max-width: 100%;">
                                {content_html}
                            </div>
                        </div>
                        
                        <div style="margin-top: 20px; text-align: center;">
                            <a href="https://ctsv.hust.edu.vn/#/hoc-bong/{sid}/chi-tiet" 
                               style="display: inline-block; padding: 12px 25px; background-color: #d32f2f; color: #ffffff; text-decoration: none; border-radius: 4px; font-weight: bold;">
                               Xem chi tiết
                            </a>
                        </div>
                    </div>
                </div>
                """
            
            body += """
                <div style="text-align: center; color: #888; font-size: 12px; margin-top: 30px; border-top: 1px solid #eee; padding-top: 20px;">
                    <p>Phân tích mức độ phù hợp bởi OpenAI AI | Ưu tiên hạn nộp gần nhất</p>
                </div>
            </body>
            </html>
            """
            send_email(subject, body, to_email=config.TARGET_EMAIL, is_html=True)
        else:
            print("Không có học bổng hợp lệ (tất cả đã hết hạn).")
    else:
        print("Không thể lấy dữ liệu từ API Học bổng.")

if __name__ == "__main__":
    check_for_new_scholarships()
