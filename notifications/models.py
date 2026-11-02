from django.db import models
from django.conf import settings

class Notification(models.Model):
    class Type(models.TextChoices):
        INFO = 'INFO', 'Information'
        EXAM = 'EXAM', 'Exam Reminder'
        TASK = 'TASK', 'Task Due'
        ATTENDANCE = 'ATTENDANCE', 'Attendance Alert'
        AI = 'AI', 'AI Recommendation'
        SYSTEM = 'SYSTEM', 'System Alert'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=20,
        choices=Type.choices,
        default=Type.INFO
    )
    is_read = models.BooleanField(default=False)
    link_url = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.notification_type}] {self.title} for {self.user.username}"
