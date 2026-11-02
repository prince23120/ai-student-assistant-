from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from accounts.models import User
from study_planner.models import Subject, StudyTask, StudySession, Exam
from attendance.models import AttendanceRecord
from dashboard.models import AIStudyRecommendation
from dashboard.utils import calculate_study_streak, get_attendance_metrics

class DashboardTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            username='dashboardstudent',
            email='dashboard@example.com',
            password='Password123!',
            role=User.Role.STUDENT,
            first_name='Dash',
            last_name='Student'
        )
        self.subject = Subject.objects.create(
            student=self.student,
            name='Algorithms',
            code='CS101'
        )

    def test_streak_calculation(self):
        today = timezone.localdate()
        # Create session today and yesterday
        StudySession.objects.create(student=self.student, session_date=today, duration_minutes=60)
        StudySession.objects.create(student=self.student, session_date=today - timedelta(days=1), duration_minutes=45)
        streak = calculate_study_streak(self.student)
        self.assertEqual(streak, 2)

    def test_attendance_calculation(self):
        today = timezone.localdate()
        # 3 present, 1 absent -> 75%
        for i in range(3):
            AttendanceRecord.objects.create(
                student=self.student,
                subject=self.subject,
                date=today - timedelta(days=i),
                status=AttendanceRecord.Status.PRESENT
            )
        AttendanceRecord.objects.create(
            student=self.student,
            subject=self.subject,
            date=today - timedelta(days=4),
            status=AttendanceRecord.Status.ABSENT
        )
        metrics = get_attendance_metrics(self.student)
        self.assertEqual(metrics['total_classes'], 4)
        self.assertEqual(metrics['present_classes'], 3)
        self.assertEqual(metrics['overall_percentage'], 75.0)

    def test_student_dashboard_authenticated(self):
        self.client.login(username='dashboardstudent', password='Password123!')
        response = self.client.get(reverse('dashboard:student'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dash')
        self.assertContains(response, 'Algorithms')

    def test_task_toggle_ajax(self):
        self.client.login(username='dashboardstudent', password='Password123!')
        task = StudyTask.objects.create(
            student=self.student,
            subject=self.subject,
            title='Test Task',
            is_completed=False
        )
        url = reverse('dashboard:toggle_task', kwargs={'task_id': task.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        task.refresh_from_db()
        self.assertTrue(task.is_completed)

    def test_recommendation_dismiss_ajax(self):
        self.client.login(username='dashboardstudent', password='Password123!')
        rec = AIStudyRecommendation.objects.create(
            student=self.student,
            title='Test Recommendation',
            content='Revise chapter 1',
            is_dismissed=False
        )
        url = reverse('dashboard:dismiss_recommendation', kwargs={'rec_id': rec.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        rec.refresh_from_db()
        self.assertTrue(rec.is_dismissed)
