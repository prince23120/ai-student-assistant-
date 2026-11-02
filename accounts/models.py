from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = 'STUDENT', _('Student')
        TEACHER = 'TEACHER', _('Teacher')
        ADMIN = 'ADMIN', _('Administrator')

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
        help_text=_('User platform role')
    )
    email = models.EmailField(_('email address'), unique=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    @property
    def is_teacher(self):
        return self.role == self.Role.TEACHER

    @property
    def is_administrator(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=50, blank=True, help_text="University or College Roll No")
    college_name = models.CharField(max_length=200, blank=True, default="Apex University")
    degree = models.CharField(max_length=150, blank=True, default="B.Tech Computer Science")
    semester = models.PositiveSmallIntegerField(default=5)
    academic_year = models.CharField(max_length=20, default="2026-2027")
    attendance_target = models.FloatField(default=75.0, help_text="Minimum required attendance %")
    daily_study_target_minutes = models.PositiveIntegerField(default=180, help_text="Daily study target in minutes")
    preferred_language = models.CharField(
        max_length=10,
        choices=[('en', 'English'), ('hi', 'Hindi'), ('bilingual', 'Hinglish / Bilingual')],
        default='en'
    )
    career_interest = models.CharField(max_length=150, blank=True, default="Full Stack AI Engineer")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Student Profile: {self.user.username} - Sem {self.semester}"


class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    department = models.CharField(max_length=150, default="Computer Science & Engineering")
    designation = models.CharField(max_length=100, default="Assistant Professor")
    office_location = models.CharField(max_length=100, blank=True, default="Academic Block B, Room 304")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Teacher Profile: {self.user.username} ({self.department})"
