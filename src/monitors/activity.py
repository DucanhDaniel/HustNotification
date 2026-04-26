from ..utils.api_fetcher import APIFetcher
from ..utils.data_tracker import DataTracker
from ..utils.email_sender import send_email
from ..utils.ai_analyzer import AIAnalyzer
from .training_points import get_training_points_data
from .. import config
from datetime import datetime
import os
import json

def parse_hust_date(date_str):
    """Parse HUST date format (DD/MM/YYYY or YYYY-MM-DD)"""
    if not date_str or date_str == 'Không rõ':
        return None
    
    formats = [
        '%d/%m/%Y %H:%M:%S', '%d/%m/%Y %H:%M',
        '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M',
        '%Y-%m-%dT%H:%M:%S'
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except:
            continue
    return None

def get_analyzed_activities():
    """
    Fetch activities, analyze them with AI, and return the analyzed list and summary.
    """
    fetcher = APIFetcher(base_url='https://ctsv.hust.edu.vn')
    fetcher.set_auth('bearer_token', config.HUST_TOKEN)

    body = {
        "UserCode": config.USER_CODE,
        "Semester": config.CURRENT_SEMESTER,
        "UserName": config.USER_NAME
    }

    data = fetcher.fetch(
        endpoint='/api-t/Activity/GetPublishActivity',
        method='POST',
        headers=config.HUST_HEADERS,
        body=body
    )

    if not data or not isinstance(data, dict):
        return [], ""

    activity_list = data.get('Activities', [])
    now = datetime.now()
    valid_activities = []
    for act in activity_list:
        deadline_dt = parse_hust_date(act.get('Deadline'))
        if deadline_dt and deadline_dt > now:
            act['_deadline_dt'] = deadline_dt
            valid_activities.append(act)
        elif not deadline_dt:
            act['_deadline_dt'] = None
            valid_activities.append(act)
    
    valid_activities.sort(key=lambda x: x['_deadline_dt'] if x['_deadline_dt'] else datetime.max)
    new_activities = valid_activities[:15]
    
    if not new_activities:
        return [], ""

    for activity in new_activities:
        aid = activity.get('AId')
        detail_data = fetcher.fetch(
            endpoint='/api-t/Activity/GetActivityById',
            method='POST',
            headers=config.HUST_HEADERS,
            body={'id': aid, 'AId': aid}
        )
        if detail_data and isinstance(detail_data, dict):
            details = detail_data.get('Activities', [])
            if details:
                activity['CriteriaLst'] = details[0].get('CriteriaLst', [])

    # AI Analysis
    training_summary = get_training_points_data()
    user_profile = {}
    profile_path = 'data/user_profile.json'
    if os.path.exists(profile_path):
        try:
            with open(profile_path, 'r', encoding='utf-8') as f:
                user_profile = json.load(f)
        except: pass

    analyzer = AIAnalyzer()
    ai_results = analyzer.analyze_activities(new_activities, training_summary, user_profile)
    summary_text = ai_results.get("summary", "Không có tóm tắt từ AI.")
    recommendations = ai_results.get("recommendations", [])
    rec_map = {str(r['activity_id']): r for r in recommendations}
    
    for activity in new_activities:
        aid = str(activity.get('AId'))
        rec = rec_map.get(aid)
        activity['ai_rec'] = rec
        activity['is_online'] = rec.get('is_online', False) if rec else False

    new_activities.sort(key=lambda x: (
        not x.get('is_soon', False),
        x['ai_rec'] is None,
        not x['is_online'],
        x['_deadline_dt'] if x['_deadline_dt'] else datetime.max
    ))
    
    return new_activities, summary_text

def check_for_new_activities():
    """
    Check for new activities and send email if any.
    """
    new_activities, summary_text = get_analyzed_activities()
    
    if new_activities:
        subject = f"Có {len(new_activities)} hoạt động mới!"
        body = f"""
        <html>
        <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #2e7d32; border-bottom: 2px solid #2e7d32; padding-bottom: 10px;">📅 Hoạt động mới & Phân tích lộ trình điểm</h2>
            
            <div style="background-color: #f1f8e9; padding: 20px; border-radius: 12px; border-left: 6px solid #2e7d32; margin-bottom: 30px;">
                <h3 style="color: #2e7d32; margin-top: 0;">🤖 Tóm tắt & Gợi ý nhanh:</h3>
                <div style="font-size: 15px; color: #1b5e20;">{summary_text}</div>
            </div>

            <p>Chi tiết các hoạt động được liệt kê dưới đây:</p>
        """
        
        for activity in new_activities:
            title = activity.get('AName') or 'Không có tiêu đề'
            type_info = activity.get('AType') or 'Hoạt động'
            place = activity.get('APlace') or 'Không rõ địa điểm'
            start = activity.get('StartTime') or 'Không rõ'
            deadline = activity.get('Deadline') or 'Không rõ'
            desc_html = activity.get('ADesc') or '<p>Không có mô tả chi tiết.</p>'
            criteria_lst = activity.get('CriteriaLst', [])
            
            rec = activity.get('ai_rec')
            is_online = activity.get('is_online', False)
            is_soon = activity.get('is_soon', False)
            
            rec_html = ""
            border_style = "border: 1px solid #e0e0e0;"
            
            online_badge = ""
            if is_online:
                online_badge = '<span style="background-color: #2196f3; color: white; padding: 3px 8px; border-radius: 4px; font-size: 11px; margin-left: 10px; vertical-align: middle;">🌐 ONLINE</span>'
            
            soon_badge = ""
            if is_soon:
                soon_badge = '<span style="background-color: #d32f2f; color: white; padding: 3px 8px; border-radius: 4px; font-size: 11px; margin-left: 10px; vertical-align: middle;">⏰ SẮP HẾT HẠN</span>'
                border_style = "border: 2px solid #d32f2f; box-shadow: 0 0 10px rgba(211, 47, 47, 0.2);"

            if rec:
                if not is_soon:
                    border_style = "border: 2px solid #ff9800; transform: scale(1.02);"
                rec_html = f"""
                <div style="background-color: #ff9800; color: white; padding: 10px; font-weight: bold; border-radius: 4px 4px 0 0;">
                    💡 ĐỀ XUẤT THAM GIA: {rec.get('category_name')}
                </div>
                <div style="background-color: #fff3e0; padding: 10px; border-left: 5px solid #ff9800; margin-bottom: 15px; font-size: 14px;">
                    <strong>Lý do:</strong> {rec.get('reason')}
                </div>
                """

            criteria_html = ""
            if criteria_lst:
                criteria_html = '<div style="margin-top: 15px; padding: 10px; background-color: #e8f5e9; border-radius: 4px;">'
                criteria_html += '<strong style="color: #2e7d32; display: block; margin-bottom: 5px;">🏆 Quyền lợi & Tiêu chí rèn luyện:</strong>'
                criteria_html += '<ul style="margin: 0; padding-left: 20px; font-size: 13px;">'
                for c in criteria_lst:
                    criteria_html += f'<li>{c.get("CName")} (Tối đa: {c.get("CMaxPoint")}đ)</li>'
                criteria_html += '</ul></div>'

            body += f"""
            <div style="margin-bottom: 40px; padding: 0; {border_style} border-radius: 8px; background-color: #ffffff; box-shadow: 0 4px 12px rgba(0,0,0,0.1); overflow: hidden;">
                {rec_html}
                <div style="padding: 20px;">
                    <h3 style="color: #2e7d32; margin-top: 0;">🌟 {title} {online_badge} {soon_badge}</h3>
                    <table style="width: 100%; border-collapse: collapse; margin-bottom: 15px;">
                        <tr><td style="padding: 5px 0; width: 120px;"><strong>🏷️ Loại:</strong></td><td>{type_info}</td></tr>
                        <tr><td style="padding: 5px 0;"><strong>📍 Địa điểm:</strong></td><td>{place}</td></tr>
                        <tr><td style="padding: 5px 0;"><strong>⏰ Bắt đầu:</strong></td><td>{start}</td></tr>
                        <tr><td style="padding: 5px 0;"><strong>🏁 Hạn đăng ký:</strong></td><td style="color: #d32f2f; font-weight: bold;">{deadline}</td></tr>
                    </table>
                    {criteria_html}
                    <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #eee;">
                        <strong style="display: block; margin-bottom: 10px; color: #555;">🔍 Chi tiết hoạt động:</strong>
                        <div style="font-size: 14px; color: #444; max-height: 200px; overflow-y: auto;">{desc_html}</div>
                    </div>
                    <div style="margin-top: 20px; text-align: center;">
                        <a href="https://ctsv.hust.edu.vn/#/hoat-dong/{activity.get('AId')}/chi-tiet" 
                           style="display: inline-block; padding: 12px 25px; background-color: #1976d2; color: #ffffff; text-decoration: none; border-radius: 4px; font-weight: bold;">
                            Xem chi tiết hoạt động
                        </a>
                    </div>
                </div>
            </div>
            """
        
        body += """
            <div style="text-align: center; color: #888; font-size: 12px; margin-top: 30px; border-top: 1px solid #eee; padding-top: 20px;">
                <p>Phân tích bởi OpenAI AI | Đã lọc hoạt động hết hạn | Ưu tiên Online</p>
            </div>
        </body>
        </html>
        """
        send_email(subject, body, to_email=config.TARGET_EMAIL, is_html=True)
    else:
        print("Không có hoạt động nào hợp lệ.")

if __name__ == "__main__":
    check_for_new_activities()
