from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User, StudentProfile, TeacherProfile

class AccountsAuthTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.student_user = User.objects.create_user(
            username='teststudent',
            email='teststudent@example.com',
            password='Password123!',
            role=User.Role.STUDENT,
            first_name='Test',
            last_name='Student'
        )

    def test_user_roles(self):
        self.assertTrue(self.student_user.is_student)
        self.assertFalse(self.student_user.is_teacher)
        self.assertFalse(self.student_user.is_administrator)

    def test_student_profile_created(self):
        self.assertTrue(hasattr(self.student_user, 'student_profile'))
        self.assertEqual(self.student_user.student_profile.semester, 5)

    def test_login_flow(self):
        response = self.client.post(reverse('accounts:login'), {
            'username_or_email': 'teststudent',
            'password': 'Password123!'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'].is_authenticated)

    def test_login_with_email(self):
        response = self.client.post(reverse('accounts:login'), {
            'username_or_email': 'teststudent@example.com',
            'password': 'Password123!'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'].is_authenticated)

    def test_registration_flow(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'newstudent',
            'email': 'newstudent@example.com',
            'first_name': 'New',
            'last_name': 'Learner',
            'role': User.Role.STUDENT,
            'password': 'SecurePassword123!',
            'confirm_password': 'SecurePassword123!',
            'degree': 'B.Tech IT',
            'semester': 3,
            'college_name': 'Apex College'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username='newstudent').exists())
        new_u = User.objects.get(username='newstudent')
        self.assertEqual(new_u.student_profile.degree, 'B.Tech IT')
