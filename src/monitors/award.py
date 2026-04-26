from ..utils.api_fetcher import APIFetcher
from ..utils.data_tracker import DataTracker
from ..utils.email_sender import send_email
from ..utils.ai_analyzer import AIAnalyzer
from .. import config
import os
import json
from datetime import datetime

def check_for_new_awards():
    """
    Check for new awards (scholarships/grants) from student.hust.edu.vn.
    """
    fetcher = APIFetcher(base_url='https://student.hust.edu.vn')
    # This API appears to be public or doesn't require session cookies for this specific GET request
    
    endpoint = f'/api/v1/awards?includeUnit=true&type=get_by_time&userIds={config.QLDT_USER_ID}'
    
    data = fetcher.fetch(
        endpoint=endpoint,
        method='GET',
        headers=config.QLDT_HEADERS
    )

    if data and isinstance(data, dict):
        award_list = data.get('data', [])
        print(f"Awards fetched successfully. Found {len(award_list)} items.")
        
        # Sort by registerTo descending and take top 5
        award_list.sort(key=lambda x: x.get('registerTo') or 0, reverse=True)
        top_awards = award_list[:10]

        if top_awards:
            print(f"Analyzing top {len(top_awards)} awards by deadline...")
            
            # AI Analysis
            user_profile = {}
            if os.path.exists('data/user_profile.json'):
                with open('data/user_profile.json', 'r', encoding='utf-8') as f:
                    user_profile = json.load(f)
            
            analyzer = AIAnalyzer()
            ai_results = analyzer.analyze_awards(top_awards, user_profile)
            summary_text = ai_results.get("summary", "Không có tóm tắt từ AI.")
            matches = ai_results.get("matches", [])
            match_map = {str(m['award_id']): m for m in matches}

            subject = f"🔔 Top {len(top_awards)} Học bổng/Giải thưởng mới nhất từ QLĐT"
            
            body = f"""
            <html>
            <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; max-width: 850px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #1b5e20; border-bottom: 2px solid #1b5e20; padding-bottom: 10px;">🏆 Top {len(top_awards)} Học bổng & Giải thưởng mới nhất (QLĐT)</h2>
                
                <div style="background-color: #f1f8e9; padding: 20px; border-radius: 12px; border-left: 6px solid #2e7d32; margin-bottom: 30px;">
                    <h3 style="color: #2e7d32; margin-top: 0;">🤖 Tóm tắt & Gợi ý từ AI:</h3>
                    <div style="font-size: 15px; color: #1b5e20;">{summary_text}</div>
                </div>

                <p>Danh sách 5 thông tin học bổng/giải thưởng mới nhất trên cổng student.hust.edu.vn:</p>
            """
            
            for award in top_awards:
                aid = str(award.get('id'))
                name = award.get('name') or 'Không có tên'
                partners = ", ".join(award.get('partnerNames', [])) or 'Đang cập nhật'
                award_names = ", ".join(award.get('awardNames', [])) or 'Học bổng'
                value_range = award.get('awardValueRange') or 'Liên hệ'
                num_range = award.get('awardNumRange') or 'Đang cập nhật'
                
                # Convert timestamps
                reg_from = award.get('registerFrom')
                reg_to = award.get('registerTo')
                reg_from_str = datetime.fromtimestamp(reg_from/1000).strftime('%d/%m/%Y') if reg_from else '---'
                reg_to_str = datetime.fromtimestamp(reg_to/1000).strftime('%d/%m/%Y') if reg_to else '---'
                
                desc_html = award.get('description') or '<p>Không có mô tả chi tiết.</p>'
                
                match = match_map.get(aid)
                match_html = ""
                border_style = "border: 1px solid #e8f5e9;"
                
                if match:
                    score = match.get('match_score', 0)
                    color = "#2e7d32" if score >= 70 else "#f9a825"
                    border_style = f"border: 2px solid {color}; transform: scale(1.01);"
                    match_html = f"""
                    <div style="background-color: {color}; color: white; padding: 10px; font-weight: bold; border-radius: 8px 8px 0 0;">
                        ✨ ĐỘ PHÙ HỢP: {score}%
                    </div>
                    <div style="background-color: #f9f9f9; padding: 15px; border-left: 5px solid {color}; font-size: 14px; margin-bottom: 0;">
                        <strong>Gợi ý AI:</strong> {match.get('reason')}
                    </div>
                    """

                body += f"""
                <div style="margin-bottom: 35px; padding: 0; {border_style} border-radius: 12px; background-color: #ffffff; box-shadow: 0 4px 6px rgba(0,0,0,0.05); overflow: hidden;">
                    {match_html}
                    <div style="padding: 25px;">
                        <h3 style="color: #2e7d32; margin-top: 0; font-size: 20px;">🎖️ {name}</h3>
                        
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px; background: #f9f9f9; padding: 15px; border-radius: 8px;">
                            <div>
                                <p style="margin: 5px 0;"><strong>🏢 Đơn vị tài trợ:</strong> {partners}</p>
                                <p style="margin: 5px 0;"><strong>🏷️ Loại giải thưởng:</strong> {award_names}</p>
                                <p style="margin: 5px 0;"><strong>💰 Giá trị:</strong> <span style="color: #c62828; font-weight: bold;">{value_range} VNĐ</span></p>
                            </div>
                            <div>
                                <p style="margin: 5px 0;"><strong>👥 Số lượng:</strong> {num_range}</p>
                                <p style="margin: 5px 0;"><strong>📅 Thời gian đăng ký:</strong></p>
                                <p style="margin: 2px 0 5px 20px; color: #1565c0; font-weight: bold;">{reg_from_str} ➔ {reg_to_str}</p>
                            </div>
                        </div>

                        <div style="margin-top: 20px; border-top: 1px dashed #ccc; padding-top: 15px;">
                            <strong style="color: #455a64; display: block; margin-bottom: 10px;">📄 Chi tiết thông báo:</strong>
                            <div style="font-size: 14px; color: #555; background: #fff; padding: 10px; border: 1px solid #f0f0f0; border-radius: 4px;">
                                {desc_html}
                            </div>
                        </div>
                        
                        <div style="margin-top: 25px; text-align: center;">
                            <a href="https://qldt.hust.edu.vn/" 
                               style="display: inline-block; padding: 12px 30px; background-color: #2e7d32; color: #ffffff; text-decoration: none; border-radius: 6px; font-weight: bold; transition: background 0.3s;">
                               Truy cập QLĐT để đăng ký
                            </a>
                        </div>
                    </div>
                </div>
                """
            
            body += f"""
                <div style="text-align: center; color: #999; font-size: 12px; margin-top: 40px; border-top: 1px solid #eee; padding-top: 20px;">
                    <p>Hệ thống giám sát tự động student.hust.edu.vn | {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                    <p>Phân tích bởi OpenAI AI</p>
                </div>
            </body>
            </html>
            """
            send_email(subject, body, to_email=config.TARGET_EMAIL, is_html=True)
        else:
            print("Không có học bổng/giải thưởng mới từ QLĐT.")
    else:
        print("Không thể lấy dữ liệu từ API QLĐT Awards.")

if __name__ == "__main__":
    check_for_new_awards()
