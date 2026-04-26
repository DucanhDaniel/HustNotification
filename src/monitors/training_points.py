from ..utils.api_fetcher import APIFetcher
from ..utils.email_sender import send_email
from ..utils.ai_analyzer import AIAnalyzer
from .. import config
import os
import json
from datetime import datetime

def check_training_points(force=False):
    """
    Fetch and report training points. Send notification if points change or if force is True.
    """
    from .activity import get_analyzed_activities

    fetcher = APIFetcher(base_url='https://ctsv.hust.edu.vn')
    fetcher.set_auth('cookies', config.HUST_COOKIES)

    # Isolated headers for CTSV to mimic browser
    ctsv_headers = config.HUST_HEADERS.copy()
    ctsv_headers['Authorization'] = 'Bearer null'
    
    # Mirroring browser: Hust APIs sometimes check these in headers AND cookies
    for token_key in ['x-access-token', 'x-student-portal-token']:
        if token_key in config.HUST_COOKIES:
            ctsv_headers[token_key] = config.HUST_COOKIES[token_key]

    body = {
        "UserCode": config.USER_CODE,
        "Semester": config.CURRENT_SEMESTER,
        "UserName": config.USER_NAME,
        "TokenCode": config.HUST_COOKIES.get('TokenCode', '')
    }

    # Debug info to track session validity
    print(f"Debug - Cookies Available: {list(config.HUST_COOKIES.keys())}")
    if 'x-student-portal-token' not in config.HUST_COOKIES:
        print("Warning: x-student-portal-token is missing from HUST_COOKIES!")


    data = fetcher.fetch(
        endpoint='/api-t/Criteria/GetCriteriaTypeDetails',
        method='POST',
        headers=ctsv_headers,
        body=body
    )

    print(f"Debug - System Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (Timestamp: {int(datetime.now().timestamp())})")
    print(f"Debug - Request Body: {json.dumps(body)}")
    print(f"Debug - Response Data: {json.dumps(data, ensure_ascii=False)[:500]}...")

    details_file = 'data/training_points_details.json'
    criteria_list = []
    
    if data and isinstance(data, dict):
        criteria_list = data.get('CriteriaTypeDetailsLst', [])
        if criteria_list:
            # Save detailed data for future fallback
            os.makedirs('data', exist_ok=True)
            with open(details_file, 'w', encoding='utf-8') as f:
                json.dump(criteria_list, f, ensure_ascii=False, indent=4)
        else:
            print(f"Warning: CriteriaTypeDetailsLst is empty. RespCode: {data.get('RespCode')}, RespText: {data.get('RespText')}")

    # Fallback if fetch failed or returned empty
    if not criteria_list:
        if os.path.exists(details_file):
            print("Fetch failed or returned no data. Falling back to local cache...")
            try:
                with open(details_file, 'r', encoding='utf-8') as f:
                    criteria_list = json.load(f)
            except Exception as e:
                print(f"Error loading fallback data: {e}")
        else:
            print("No local cache found and fetch failed.")
            return # Exit if no data available at all

    print(f"Processing {len(criteria_list)} training point categories.")

    points_file = 'data/hust_training_points.json'
    previous_points = {}
    if os.path.exists(points_file):
        try:
            with open(points_file, 'r', encoding='utf-8') as f:
                previous_points = json.load(f)
        except:
            previous_points = {}

    current_points = {c.get('CTName'): c.get('CTPoint', 0.0) for c in criteria_list}
    total_points = sum(current_points.values())
    
    has_changed = False
    changes_html = ""
    
    if not previous_points:
        has_changed = True
    else:
        for name, point in current_points.items():
            prev_point = previous_points.get(name, 0.0)
            if point != prev_point:
                has_changed = True
                diff = point - prev_point
                color = "#2e7d32" if diff > 0 else "#d32f2f"
                changes_html += f"<li><strong>{name}:</strong> {prev_point} ➔ {point} (<span style='color: {color};'>{' + ' if diff > 0 else ''}{diff}</span>)</li>"

    if has_changed or force:
        print(f"Sending training points report (Changed: {has_changed}, Force: {force})")
        
        # --- AI Analysis for Strategy ---
        print("Fetching activities for AI Strategic Analysis...")
        activities, _ = get_analyzed_activities()
        
        user_profile = {}
        profile_path = 'data/user_profile.json'
        if os.path.exists(profile_path):
            try:
                with open(profile_path, 'r', encoding='utf-8') as f:
                    user_profile = json.load(f)
            except: pass

        # Build a more detailed summary for the AI
        detailed_summary = []
        for c in criteria_list:
            cat_info = {
                "name": c.get('CTName'),
                "current": c.get('CTPoint', 0.0),
                "max": c.get('CTMaxPoint', 0.0),
                "groups": []
            }
            for g in c.get('CriteriaGroupDetailsLst', []):
                cat_info["groups"].append({
                    "name": g.get('CGName'),
                    "current": g.get('CGPoint', 0.0),
                    "max": g.get('CGMaxPoint', 0.0)
                })
            detailed_summary.append(cat_info)
            
        analyzer = AIAnalyzer()
        strategy_html = analyzer.analyze_training_strategy(
            training_points_summary=detailed_summary,
            activities=activities,
            user_profile=user_profile
        )
        
        subject = f"📊 Báo cáo Điểm rèn luyện HUST - Tổng: {total_points}đ"
        
        table_rows = ""
        for c in criteria_list:
            name = c.get('CTName')
            point = c.get('CTPoint', 0.0)
            max_point = c.get('CTMaxPoint', 0.0)
            groups = c.get('CriteriaGroupDetailsLst', [])
            
            percent = (point / max_point * 100) if max_point != 0 else 0
            if max_point < 0: percent = (point / max_point * 100) if point != 0 else 0
            color = "#1976d2"
            if percent >= 80: color = "#2e7d32"
            elif percent < 50: color = "#f9a825"
            
            table_rows += f"""
            <tr style="background-color: #f8f9fa; font-weight: bold;">
                <td style="padding: 12px; border-bottom: 2px solid #dee2e6;">{name}</td>
                <td style="padding: 12px; border-bottom: 2px solid #dee2e6; text-align: center;">{point} / {max_point}</td>
                <td style="padding: 12px; border-bottom: 2px solid #dee2e6;">
                    <div style="width: 100%; background-color: #eee; border-radius: 10px; height: 12px;">
                        <div style="width: {min(max(percent, 0), 100)}%; background-color: {color}; border-radius: 10px; height: 12px;"></div>
                    </div>
                </td>
            </tr>
            """
            for g in groups:
                g_name = g.get('CGName')
                g_point = g.get('CGPoint', 0.0)
                g_max = g.get('CGMaxPoint', 0.0)
                items = g.get('UserCriteriaDetailsLst', [])
                
                table_rows += f"""
                <tr style="background-color: #fcfcfc;">
                    <td style="padding: 8px 8px 8px 30px; border-bottom: 1px solid #eee; font-size: 13px; color: #444;"><strong>• {g_name}</strong></td>
                    <td style="padding: 8px; border-bottom: 1px solid #eee; text-align: center; font-size: 13px;">{g_point} / {g_max}</td>
                    <td style="padding: 8px; border-bottom: 1px solid #eee;"></td>
                </tr>
                """
                for item in items:
                    i_name = item.get('CName')
                    i_point = item.get('UCPoint', 0.0)
                    i_max = item.get('CMaxPoint', 0.0)
                    table_rows += f"""
                    <tr>
                        <td style="padding: 5px 8px 5px 50px; border-bottom: 1px solid #f9f9f9; font-size: 11px; color: #888;">- {i_name}</td>
                        <td style="padding: 5px; border-bottom: 1px solid #f9f9f9; text-align: center; font-size: 11px; color: #888;">{i_point} / {i_max}</td>
                        <td style="padding: 5px; border-bottom: 1px solid #f9f9f9;"></td>
                    </tr>
                    """

        body_html = f"""
        <html>
        <body style="font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 700px; margin: 0 auto; padding: 20px;">
            <div style="text-align: center; margin-bottom: 30px;">
                <h2 style="color: #d32f2f; margin-bottom: 5px;">📊 BÁO CÁO ĐIỂM RÈN LUYỆN</h2>
                <p style="font-size: 18px; color: #555;">Học kỳ: {config.CURRENT_SEMESTER} | Tổng điểm: <strong style="color: #d32f2f; font-size: 24px;">{total_points}</strong></p>
            </div>

            <div style="background-color: #e3f2fd; padding: 20px; border-radius: 12px; border-left: 6px solid #1976d2; margin-bottom: 30px;">
                <h3 style="color: #1976d2; margin-top: 0;">🤖 Tư vấn Chiến lược từ AI:</h3>
                <div style="font-size: 15px; color: #0d47a1;">{strategy_html}</div>
            </div>

            {f'<div style="background-color: #fff9c4; padding: 15px; border-radius: 8px; margin-bottom: 25px;"><strong>🔔 Thay đổi gần đây:</strong><ul style="margin-top: 5px;">{changes_html}</ul></div>' if changes_html else ''}
            
            <table style="width: 100%; border-collapse: collapse; background-color: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <thead><tr style="background-color: #f5f5f5;"><th style="padding: 12px; text-align: left;">Hạng mục</th><th style="padding: 12px; text-align: center;">Điểm số</th><th style="padding: 12px; text-align: left; width: 150px;">Tiến độ</th></tr></thead>
                <tbody>{table_rows}</tbody>
            </table>
            <div style="margin-top: 30px; padding: 20px; background-color: #f8f9fa; border-radius: 8px; font-size: 14px; text-align: center; color: #888;">
                <p>Phân tích bởi AI Assistant | Dựa trên Điểm số, Hoạt động & Thời khóa biểu</p>
            </div>
        </body>
        </html>
        """
        send_email(subject, body_html, to_email=config.TARGET_EMAIL, is_html=True)
        with open(points_file, 'w', encoding='utf-8') as f:
            json.dump(current_points, f, ensure_ascii=False, indent=4)
    else:
        print("No change in training points.")


def get_training_points_data():
    """
    Fetch and return raw training points data.
    """
    fetcher = APIFetcher(base_url='https://ctsv.hust.edu.vn')
    fetcher.set_auth('cookies', config.HUST_COOKIES)
    
    ctsv_headers = config.HUST_HEADERS.copy()
    ctsv_headers['Authorization'] = 'Bearer null'
    for token_key in ['x-access-token', 'x-student-portal-token']:
        if token_key in config.HUST_COOKIES:
            ctsv_headers[token_key] = config.HUST_COOKIES[token_key]

    body = {
        "UserCode": config.USER_CODE,
        "Semester": config.CURRENT_SEMESTER,
        "UserName": config.USER_NAME,
        "TokenCode": config.HUST_COOKIES.get('TokenCode', '')
    }

    data = fetcher.fetch(
        endpoint='/api-t/Criteria/GetCriteriaTypeDetails',
        method='POST',
        headers=ctsv_headers,
        body=body
    )
    
    print(f"Debug (get_data) - Response Data: {json.dumps(data, ensure_ascii=False)[:200]}...")
    
    details_file = 'data/training_points_details.json'
    criteria_list = []
    
    if data and isinstance(data, dict):
        criteria_list = data.get('CriteriaTypeDetailsLst', [])
    
    if not criteria_list and os.path.exists(details_file):
        try:
            with open(details_file, 'r', encoding='utf-8') as f:
                criteria_list = json.load(f)
        except: pass

    summary = []
    for c in criteria_list:
        summary.append({
            "name": c.get('CTName'),
            "current": c.get('CTPoint', 0.0),
            "max": c.get('CTMaxPoint', 0.0)
        })
    return summary

if __name__ == "__main__":
    check_training_points()
