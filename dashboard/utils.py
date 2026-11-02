from datetime import date, timedelta
from django.db.models import Sum, Count, Q
from django.utils import timezone
from study_planner.models import StudySession, StudyTask, Exam, Subject
from attendance.models import AttendanceRecord

def calculate_study_streak(user):
    """
    Calculates consecutive active study days up to today or yesterday.
    """
    today = timezone.localdate()
    # Get distinct session dates for this user ordered descending
    session_dates = set(
        StudySession.objects.filter(student=user)
        .values_list('session_date', flat=True)
    )

    if not session_dates:
        return 0

    streak = 0
    current_check = today

    # If student didn't study today yet, check if they studied yesterday to keep streak alive
    if current_check not in session_dates:
        current_check = today - timedelta(days=1)
        if current_check not in session_dates:
            return 0

    while current_check in session_dates:
        streak += 1
        current_check -= timedelta(days=1)

    return streak


def get_weekly_study_chart_data(user):
    """
    Returns days and hours for the past 7 days for Chart.js
    """
    today = timezone.localdate()
    labels = []
    hours_data = []

    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_name = day.strftime('%a')  # Mon, Tue, etc.
        labels.append(day_name)

        total_mins = StudySession.objects.filter(
            student=user,
            session_date=day
        ).aggregate(total=Sum('duration_minutes'))['total'] or 0

        hours_data.append(round(total_mins / 60.0, 1))

    return {
        'labels': labels,
        'hours': hours_data,
        'total_weekly_hours': round(sum(hours_data), 1)
    }


def get_attendance_metrics(user):
    """
    Calculates overall attendance and subject-wise breakdown.
    """
    records = AttendanceRecord.objects.filter(student=user)
    total_classes = records.count()
    present_classes = records.filter(status=AttendanceRecord.Status.PRESENT).count()

    overall_percentage = round((present_classes / total_classes * 100), 1) if total_classes > 0 else 0.0

    target = 75.0
    if hasattr(user, 'student_profile'):
        target = user.student_profile.attendance_target

    # Classes needed calculation if below target
    classes_needed = 0
    if total_classes > 0 and overall_percentage < target:
        # formula: (target*total - 100*present) / (100 - target)
        if target < 100:
            numerator = (target * total_classes) - (100 * present_classes)
            denominator = 100 - target
            classes_needed = max(0, int(round(numerator / denominator + 0.49)))

    # Subject breakdown
    subjects_data = []
    user_subjects = Subject.objects.filter(student=user)
    for subj in user_subjects:
        sub_records = records.filter(subject=subj)
        sub_total = sub_records.count()
        sub_present = sub_records.filter(status=AttendanceRecord.Status.PRESENT).count()
        pct = round((sub_present / sub_total * 100), 1) if sub_total > 0 else 0.0
        subjects_data.append({
            'subject': subj,
            'total': sub_total,
            'present': sub_present,
            'percentage': pct,
            'is_low': pct < target if sub_total > 0 else False
        })

    return {
        'total_classes': total_classes,
        'present_classes': present_classes,
        'overall_percentage': overall_percentage,
        'target_percentage': target,
        'classes_needed': classes_needed,
        'subjects_data': subjects_data
    }
