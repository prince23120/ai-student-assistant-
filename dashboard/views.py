import json
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Count, Q

from accounts.models import User, StudentProfile, TeacherProfile
from accounts.decorators import student_required, teacher_required, admin_required
from study_planner.models import Subject, StudyTask, StudySession, Exam
from attendance.models import AttendanceRecord
from .models import RecentActivity, AIStudyRecommendation
from .utils import calculate_study_streak, get_weekly_study_chart_data, get_attendance_metrics

@login_required
def home_view(request):
    """Routes the user to their role-specific dashboard."""
    if request.user.is_administrator:
        return redirect('dashboard:admin')
    elif request.user.is_teacher:
        return redirect('dashboard:teacher')
    return redirect('dashboard:student')


@login_required
@student_required
def student_dashboard_view(request):
    user = request.user
    today = timezone.localdate()

    # Total study hours all-time
    total_minutes = StudySession.objects.filter(student=user).aggregate(total=Sum('duration_minutes'))['total'] or 0
    total_study_hours = round(total_minutes / 60.0, 1)

    # Tasks stats
    all_tasks = StudyTask.objects.filter(student=user)
    total_tasks_count = all_tasks.count()
    completed_tasks_count = all_tasks.filter(is_completed=True).count()
    pending_tasks_count = all_tasks.filter(is_completed=False).count()
    task_completion_rate = round((completed_tasks_count / total_tasks_count * 100), 1) if total_tasks_count > 0 else 0

    # Today's tasks (due today or overdue or high priority)
    todays_tasks = all_tasks.filter(
        Q(due_date=today) | (Q(is_completed=False) & Q(priority=StudyTask.Priority.HIGH))
    )[:5]

    # Upcoming exams
    upcoming_exams = Exam.objects.filter(
        student=user,
        exam_date__gte=today,
        is_completed=False
    ).select_related('subject').order_by('exam_date')[:4]

    # Calculate days left for each exam
    for exam in upcoming_exams:
        exam.days_left = (exam.exam_date - today).days

    # Attendance metrics
    attendance_data = get_attendance_metrics(user)

    # Study Streak
    streak = calculate_study_streak(user)

    # Weekly study hours for chart
    weekly_chart = get_weekly_study_chart_data(user)

    # AI Recommendations
    ai_recommendations = AIStudyRecommendation.objects.filter(
        student=user,
        is_dismissed=False
    )[:3]

    # Recent activities
    recent_activities = RecentActivity.objects.filter(user=user).order_by('-created_at')[:6]

    # Subjects summary
    subjects = Subject.objects.filter(student=user)

    context = {
        'total_study_hours': total_study_hours,
        'weekly_study_hours': weekly_chart['total_weekly_hours'],
        'chart_labels_json': json.dumps(weekly_chart['labels']),
        'chart_hours_json': json.dumps(weekly_chart['hours']),
        'total_tasks_count': total_tasks_count,
        'completed_tasks_count': completed_tasks_count,
        'pending_tasks_count': pending_tasks_count,
        'task_completion_rate': task_completion_rate,
        'todays_tasks': todays_tasks,
        'upcoming_exams': upcoming_exams,
        'attendance': attendance_data,
        'streak': streak,
        'ai_recommendations': ai_recommendations,
        'recent_activities': recent_activities,
        'subjects': subjects,
        'today': today,
    }
    return render(request, 'dashboard/student_dashboard.html', context)


@login_required
@teacher_required
def teacher_dashboard_view(request):
    user = request.user
    students_count = User.objects.filter(role=User.Role.STUDENT).count()
    context = {
        'students_count': students_count,
    }
    return render(request, 'dashboard/teacher_dashboard.html', context)


@login_required
@admin_required
def admin_dashboard_view(request):
    total_users = User.objects.count()
    students_count = User.objects.filter(role=User.Role.STUDENT).count()
    teachers_count = User.objects.filter(role=User.Role.TEACHER).count()
    total_sessions = StudySession.objects.count()
    total_tasks = StudyTask.objects.count()
    recent_users = User.objects.order_by('-date_joined')[:8]

    context = {
        'total_users': total_users,
        'students_count': students_count,
        'teachers_count': teachers_count,
        'total_sessions': total_sessions,
        'total_tasks': total_tasks,
        'recent_users': recent_users,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


@login_required
@require_POST
def toggle_task_status(request, task_id):
    """Allows student to quickly toggle a task's completion directly from dashboard."""
    task = get_object_or_404(StudyTask, id=task_id, student=request.user)
    task.is_completed = not task.is_completed
    if task.is_completed:
        task.completed_at = timezone.now()
        RecentActivity.objects.create(
            user=request.user,
            title=f"Completed Task: {task.title}",
            category="TASK",
            icon="check-circle"
        )
    else:
        task.completed_at = None
    task.save()
    return JsonResponse({'status': 'ok', 'is_completed': task.is_completed})


@login_required
@require_POST
def dismiss_recommendation(request, rec_id):
    """Allows student to dismiss an AI recommendation."""
    rec = get_object_or_404(AIStudyRecommendation, id=rec_id, student=request.user)
    rec.is_dismissed = True
    rec.save()
    return JsonResponse({'status': 'ok'})


@login_required
@require_POST
def quick_log_study(request):
    """Quickly logs a study session from the dashboard modal."""
    subject_id = request.POST.get('subject_id')
    minutes = int(request.POST.get('minutes', 30))
    notes = request.POST.get('notes', '')

    subject = None
    if subject_id:
        subject = get_object_or_404(Subject, id=subject_id, student=request.user)

    session = StudySession.objects.create(
        student=request.user,
        subject=subject,
        duration_minutes=minutes,
        notes=notes,
        session_date=timezone.localdate()
    )

    RecentActivity.objects.create(
        user=request.user,
        title=f"Studied {subject.name if subject else 'General'} for {minutes} mins",
        category="STUDY",
        icon="book-open"
    )

    messages.success(request, f"Logged {minutes} minutes of study time! Keep up the momentum!")
    return redirect('dashboard:student')
