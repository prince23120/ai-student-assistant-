from django.contrib import admin
from .models import RecentActivity, AIStudyRecommendation

@admin.register(RecentActivity)
class RecentActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'description', 'user__username')

@admin.register(AIStudyRecommendation)
class AIStudyRecommendationAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'priority', 'is_dismissed', 'created_at')
    list_filter = ('priority', 'is_dismissed')
    search_fields = ('title', 'content', 'student__username')
