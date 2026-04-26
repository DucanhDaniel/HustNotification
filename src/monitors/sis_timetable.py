import requests
import re
import json
import os
from ..utils.data_tracker import DataTracker
from ..utils.email_sender import send_email
from .. import config
from datetime import datetime

def check_sis_timetable():
    """
    Fetch and parse the SIS timetable table from ctt-sis.hust.edu.vn.
    """
    url = "https://ctt-sis.hust.edu.vn/Students/Timetables.aspx"
    
    try:
        response = requests.get(url, cookies=config.HUST_COOKIES, headers=config.HUST_HEADERS, timeout=30)
        response.raise_for_status()
        html_content = response.text
    except Exception as e:
        print(f"Error fetching SIS timetable: {e}")
        return

    # Extract the main table content using regex
    # We look for rows with id matching DXDataRow[0-9]+
    row_pattern = re.compile(r'<tr id="[^"]+_DXDataRow\d+"[^>]*>(.*?)</tr>', re.DOTALL)
    cell_pattern = re.compile(r'<td[^>]*>(.*?)</td>', re.DOTALL)
    
    rows = row_pattern.findall(html_content)
    if not rows:
        print("No timetable data found on SIS page.")
        return

    timetable_data = []
    
    for row_html in rows:
        cells = cell_pattern.findall(row_html)
        # Clean tags and &nbsp;
        cleaned_cells = []
        for cell in cells:
            # Remove HTML tags
            clean = re.sub(r'<.*?>', '', cell)
            # Replace &nbsp; and trim
            clean = clean.replace('&nbsp;', '').strip()
            cleaned_cells.append(clean)
        
        if len(cleaned_cells) >= 11:
            item = {
                "time": cleaned_cells[0],
                "weeks": cleaned_cells[1],
                "room": cleaned_cells[2],
                "class_id": cleaned_cells[3],
                "type": cleaned_cells[4],
                "group": cleaned_cells[5],
                "course_id": cleaned_cells[6],
                "course_name": cleaned_cells[7],
                "note": cleaned_cells[8],
                "mode": cleaned_cells[9],
                "teacher": cleaned_cells[10],
                # Unique key for tracking changes (Class ID + Time + Room)
                "id": f"{cleaned_cells[3]}_{cleaned_cells[0]}_{cleaned_cells[2]}"
            }
            timetable_data.append(item)

    if timetable_data:
        print(f"SIS Timetable fetched. Found {len(timetable_data)} entries.")
        
        tracker = DataTracker(data_file='data/sis_timetable.json', unique_key='id')
        new_items = tracker.get_new_items(timetable_data)
        
        if new_items:
            print(f"Detected {len(new_items)} schedule changes/additions.")
            send_sis_timetable_notification(new_items)
        else:
            print("Thời khóa biểu SIS không có thay đổi mới.")
    else:
        print("Dữ liệu Thời khóa biểu SIS trống hoặc không thể phân tích.")

def send_sis_timetable_notification(items):
    """
    Send an email notification about new schedule items.
    """
    subject = f"📅 Cập nhật Thời khóa biểu SIS ({len(items)})"
    
    body = """
    <html>
    <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; max-width: 900px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #8C1515; border-bottom: 2px solid #8C1515; padding-bottom: 10px;">📅 Cập nhật Thời khóa biểu SIS</h2>
        <p>Hệ thống phát hiện các thay đổi hoặc lớp học mới trong thời khóa biểu của bạn trên trang SIS:</p>
        
        <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
            <thead>
                <tr style="background-color: #8C1515; color: white; text-align: left;">
                    <th style="padding: 12px; border: 1px solid #ddd;">Học phần / Lớp</th>
                    <th style="padding: 12px; border: 1px solid #ddd;">Thời gian / Tuần</th>
                    <th style="padding: 12px; border: 1px solid #ddd;">Phòng / GV</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for item in items:
        body += f"""
                <tr>
                    <td style="padding: 12px; border: 1px solid #ddd;">
                        <strong style="color: #8C1515;">{item['course_name']}</strong><br/>
                        <span style="font-size: 13px; color: #666;">Mã HP: {item['course_id']} | Lớp: {item['class_id']} ({item['type']})</span>
                    </td>
                    <td style="padding: 12px; border: 1px solid #ddd;">
                        <strong>{item['time']}</strong><br/>
                        <span style="font-size: 13px; color: #666;">Tuần: {item['weeks']}</span>
                    </td>
                    <td style="padding: 12px; border: 1px solid #ddd;">
                        <span style="font-weight: bold; color: #2e7d32;">{item['room']}</span><br/>
                        <span style="font-size: 13px; color: #666;">{item['teacher']}</span>
                    </td>
                </tr>
        """
    
    body += f"""
            </tbody>
        </table>
        <div style="text-align: center; color: #999; font-size: 12px; margin-top: 40px; border-top: 1px solid #eee; padding-top: 20px;">
            <p>Hệ thống giám sát tự động ctt-sis.hust.edu.vn | {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
        </div>
    </body>
    </html>
    """
    
    send_email(subject, body, to_email=config.TARGET_EMAIL, is_html=True)

if __name__ == "__main__":
    # Test
    check_sis_timetable()
