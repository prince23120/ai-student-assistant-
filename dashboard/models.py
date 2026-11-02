from django.db import models
from django.conf import settings

class RecentActivity(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='activities'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='activity')  # Lucide icon identifier
    category = models.CharField(max_length=50, default='GENERAL')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}: {self.title}"


class AIStudyRecommendation(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ai_recommendations'
    )
    title = models.CharField(max_length=255)
    content = models.TextField()
    priority = models.CharField(
        max_length=20,
        choices=[('HIGH', 'High'), ('MEDIUM', 'Medium'), ('LOW', 'Low')],
        default='MEDIUM'
    )
    action_label = models.CharField(max_length=100, blank=True, default="Take Action")
    action_url = models.CharField(max_length=255, blank=True, default="#")
    is_dismissed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-priority', '-created_at']

    def __str__(self):
        return f"AI Recommendation for {self.student.username}: {self.title}"
