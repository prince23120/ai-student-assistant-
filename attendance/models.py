from django.db import models
from django.conf import settings
from django.utils import timezone

class AttendanceRecord(models.Model):
    class Status(models.TextChoices):
        PRESENT = 'PRESENT', 'Present'
        ABSENT = 'ABSENT', 'Absent'
        CANCELLED = 'CANCELLED', 'Cancelled'

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )
    subject = models.ForeignKey(
        'study_planner.Subject',
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )
    date = models.DateField(default=timezone.now)
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.PRESENT
    )
    remarks = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        unique_together = ('student', 'subject', 'date')

    def __str__(self):
        return f"{self.student.username} - {self.subject.name} - {self.date} ({self.status})"
