import schedule
import time
from . import config
from .monitors.scholarship import check_for_new_scholarships
from .monitors.activity import check_for_new_activities
from .monitors.training_points import check_training_points
from .monitors.award import check_for_new_awards

def main():
    """
    Main entry point for the HUST monitoring system.
    """
    # Schedule tasks based on config
    schedule.every(config.SCHOLARSHIP_INTERVAL).hours.do(check_for_new_scholarships)
    schedule.every(config.ACTIVITY_INTERVAL).hours.do(check_for_new_activities)
    schedule.every(config.AWARD_INTERVAL).hours.do(check_for_new_awards)
    schedule.every(config.TRAINING_POINTS_INTERVAL).hours.do(check_training_points, force=True)

    print("🚀 Hệ thống monitoring HUST đã sẵn sàng!")
    print(f"  - Học bổng (CTSV): Mỗi {config.SCHOLARSHIP_INTERVAL} giờ")
    print(f"  - Hoạt động (CTSV): Mỗi {config.ACTIVITY_INTERVAL} giờ")
    print(f"  - Học bổng/Giải thưởng (QLĐT): Mỗi {config.AWARD_INTERVAL} giờ")
    print(f"  - Điểm rèn luyện: Mỗi {config.TRAINING_POINTS_INTERVAL} giờ")

    # Run immediately for the first check
    print("\n[First Run] Checking all modules...")
    check_for_new_scholarships()
    check_for_new_activities()
    check_for_new_awards()
    check_training_points(force=True)
    print("[First Run] Completed. Entering scheduler loop...\n")

    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
