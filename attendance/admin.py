from django.contrib import admin
from .models import AttendanceRecord

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'date', 'status', 'remarks')
    list_filter = ('status', 'date')
    search_fields = ('student__username', 'subject__name', 'remarks')
