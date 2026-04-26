from ..utils.api_fetcher import APIFetcher
from ..utils.data_tracker import DataTracker
from ..utils.email_sender import send_email
from .. import config
from datetime import datetime
import json

def check_timetable_changes():
    """
    Check for timetable changes (new classes) and absent reports from QLĐT.
    """
    fetcher = APIFetcher(base_url='https://student.hust.edu.vn')
    # Set cookies for QLĐT
    fetcher.set_auth('cookies', config.QLDT_COOKIES)
    
    endpoint = '/api/v2/timetables/query-student-timetable-in-range'
    
    # Payload provided by user
    payload = {
        "fromTime": 1774803600000, 
        "toTime": 1777827599999, 
        "semester": "20252", 
        "weeks": [30, 31, 32, 33, 34]
    }

    data = fetcher.fetch(
        endpoint=endpoint,
        method='POST',
        headers=config.QLDT_HEADERS,
        body=payload
    )

    if data and isinstance(data, list):
        print(f"Timetable fetched successfully. Found {len(data)} courses.")
        
        # 1. Track New Classes
        class_tracker = DataTracker(data_file='data/hust_timetable_classes.json', unique_key='id')
        new_classes = class_tracker.get_new_items(data)
        
        if new_classes:
            print(f"New classes detected: {len(new_classes)}")
            # For simplicity, we can notify about new classes, but the priority is absent reports
        
        # 2. Track Absent/Replacement Reports
        all_absent_reports = []
        for course in data:
            course_name = course.get('courseName')
            class_id = course.get('classId')
            reports = course.get('_absentReport') or []
            
            for report in reports:
                # Enrich report with course info for tracking and notification
                report['_courseName'] = course_name
                report['_classId'] = class_id
                all_absent_reports.append(report)
        
        # Use report 'id' as unique key
        absent_tracker = DataTracker(data_file='data/hust_timetable_absent.json', unique_key='id')
        new_reports = absent_tracker.get_new_items(all_absent_reports)

        if new_reports:
            print(f"New absent/replacement reports detected: {len(new_reports)}")
            send_timetable_notification(new_reports)
        else:
            print("Không có thông báo báo nghỉ/dạy bù mới.")
    else:
        print("Không thể lấy dữ liệu Thời khóa biểu từ API QLĐT.")

def send_timetable_notification(reports):
    """
    Send an email notification about new absent/replacement reports.
    """
    subject = f"⚠️ Thông báo Báo nghỉ/Dạy bù mới ({len(reports)})"
    
    body = """
    <html>
    <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; max-width: 850px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #c62828; border-bottom: 2px solid #c62828; padding-bottom: 10px;">📅 Thông báo Thay đổi Lịch học (QLĐT)</h2>
        <p>Hệ thống vừa phát hiện thông tin báo nghỉ hoặc dạy bù mới từ giảng viên:</p>
    """
    
    for report in reports:
        course_name = report.get('_courseName', 'N/A')
        class_id = report.get('_classId', 'N/A')
        teacher = report.get('teacherName', 'Chưa cập nhật')
        reason = report.get('absentReason', 'Không có lý do cụ thể')
        
        # Absent info
        absent_date = report.get('absentDateStr', 'N/A')
        absent_time = f"Tiết {report.get('absentFrom', '?')} - {report.get('absentTo', '?')}"
        absent_place = report.get('absentPlace', 'N/A')
        
        # Replacement info
        replaced_date = report.get('replacedDateStr', 'N/A')
        replaced_from = report.get('replacedFrom')
        replaced_to = report.get('replacedTo')
        replaced_place = report.get('replacedPlace', 'Chưa có địa điểm')
        
        # Status color
        status = report.get('status')
        status_text = "Đã phê duyệt" if status == 1 else "Đang chờ" if status == 0 else "Từ chối"
        status_color = "#2e7d32" if status == 1 else "#f57c00" if status == 0 else "#d32f2f"

        body += f"""
        <div style="margin-bottom: 30px; border: 1px solid #e0e0e0; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.08);">
            <div style="background-color: #f5f5f5; padding: 15px; border-bottom: 1px solid #e0e0e0;">
                <h3 style="margin: 0; color: #1565c0;">📘 {course_name} (Lớp: {class_id})</h3>
                <p style="margin: 5px 0 0 0; font-size: 14px;"><strong>👨‍🏫 Giảng viên:</strong> {teacher}</p>
            </div>
            
            <div style="padding: 20px;">
                <div style="display: flex; gap: 20px; flex-wrap: wrap;">
                    <div style="flex: 1; min-width: 250px; background: #fff5f5; padding: 15px; border-radius: 8px; border-left: 5px solid #d32f2f;">
                        <h4 style="margin-top: 0; color: #c62828;">❌ Lịch báo nghỉ</h4>
                        <p style="margin: 5px 0;"><strong>Ngày:</strong> {absent_date}</p>
                        <p style="margin: 5px 0;"><strong>Thời gian:</strong> {absent_time}</p>
                        <p style="margin: 5px 0;"><strong>Phòng:</strong> {absent_place}</p>
                        <p style="margin: 10px 0 0 0; font-style: italic; color: #555;"><strong>Lý do:</strong> {reason}</p>
                    </div>
                    
                    <div style="flex: 1; min-width: 250px; background: #e8f5e9; padding: 15px; border-radius: 8px; border-left: 5px solid #2e7d32;">
                        <h4 style="margin-top: 0; color: #2e7d32;">✅ Lịch dạy bù / Thay đổi</h4>
                        <p style="margin: 5px 0;"><strong>Ngày:</strong> {replaced_date or 'N/A'}</p>
                        <p style="margin: 5px 0;"><strong>Thời gian:</strong> {f"Tiết {replaced_from} - {replaced_to}" if replaced_from else 'Chưa cập nhật'}</p>
                        <p style="margin: 5px 0;"><strong>Phòng:</strong> <span style="font-weight: bold; color: #1b5e20;">{replaced_place}</span></p>
                        <p style="margin: 10px 0 0 0;"><strong>Trạng thái:</strong> <span style="color: {status_color}; font-weight: bold;">{status_text}</span></p>
                    </div>
                </div>
            </div>
        </div>
        """
    
    body += f"""
        <div style="text-align: center; color: #999; font-size: 12px; margin-top: 40px; border-top: 1px solid #eee; padding-top: 20px;">
            <p>Hệ thống giám sát tự động student.hust.edu.vn | {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
        </div>
    </body>
    </html>
    """
    
    send_email(subject, body, to_email=config.TARGET_EMAIL, is_html=True)

if __name__ == "__main__":
    check_timetable_changes()
