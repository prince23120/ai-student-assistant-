from django.contrib import admin
from .models import Subject, Topic, StudyTask, StudySession, Exam

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'student', 'credits', 'target_hours_per_week')
    list_filter = ('credits',)
    search_fields = ('name', 'code', 'student__username')

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'difficulty', 'is_completed')
    list_filter = ('difficulty', 'is_completed')
    search_fields = ('title', 'subject__name')

@admin.register(StudyTask)
class StudyTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'subject', 'due_date', 'priority', 'is_completed')
    list_filter = ('priority', 'is_completed', 'due_date')
    search_fields = ('title', 'student__username', 'subject__name')

@admin.register(StudySession)
class StudySessionAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'duration_minutes', 'session_date')
    list_filter = ('session_date',)
    search_fields = ('student__username', 'subject__name')

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'student', 'exam_date', 'venue', 'is_completed', 'score')
    list_filter = ('is_completed', 'exam_date')
    search_fields = ('title', 'subject__name', 'student__username')
