from django.db import models
from django.conf import settings
from django.utils import timezone

class Subject(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subjects'
    )
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=30, blank=True)
    color = models.CharField(max_length=20, default="#6366F1")  # Indigo default
    instructor_name = models.CharField(max_length=100, blank=True)
    credits = models.PositiveSmallIntegerField(default=3)
    target_hours_per_week = models.FloatField(default=6.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        unique_together = ('student', 'name')

    def __str__(self):
        return f"{self.name} ({self.code})" if self.code else self.name


class Topic(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='topics')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    difficulty = models.CharField(
        max_length=20,
        choices=[('EASY', 'Easy'), ('MEDIUM', 'Medium'), ('HARD', 'Hard')],
        default='MEDIUM'
    )
    is_completed = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.subject.name} - {self.title}"


class StudyTask(models.Model):
    class Priority(models.TextChoices):
        LOW = 'LOW', 'Low'
        MEDIUM = 'MEDIUM', 'Medium'
        HIGH = 'HIGH', 'High'

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='study_tasks'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    due_date = models.DateField(null=True, blank=True)
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['is_completed', 'due_date', '-priority']

    def __str__(self):
        return f"[{self.priority}] {self.title}"


class StudySession(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='study_sessions'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='study_sessions'
    )
    duration_minutes = models.PositiveIntegerField(default=30)
    session_date = models.DateField(default=timezone.now)
    topics_covered = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-session_date', '-created_at']

    def __str__(self):
        return f"{self.student.username} - {self.duration_minutes}m on {self.session_date}"


class Exam(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='exams'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='exams'
    )
    title = models.CharField(max_length=200)
    exam_date = models.DateField()
    exam_time = models.TimeField(null=True, blank=True)
    venue = models.CharField(max_length=150, blank=True, default="Exam Hall 1")
    syllabus = models.TextField(blank=True)
    total_marks = models.FloatField(default=100.0)
    score = models.FloatField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['exam_date', 'exam_time']

    def __str__(self):
        return f"{self.subject.name} - {self.title} on {self.exam_date}"
