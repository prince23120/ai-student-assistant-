from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, StudentProfile, TeacherProfile

class StudentProfileInline(admin.StackedInline):
    model = StudentProfile
    can_delete = False
    verbose_name_plural = 'Student Profile'

class TeacherProfileInline(admin.StackedInline):
    model = TeacherProfile
    can_delete = False
    verbose_name_plural = 'Teacher Profile'

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Platform Details', {'fields': ('role', 'avatar', 'phone_number', 'bio')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Platform Details', {'fields': ('role', 'email')}),
    )

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        if obj.role == User.Role.STUDENT:
            return [StudentProfileInline(self.model, self.admin_site)]
        elif obj.role == User.Role.TEACHER:
            return [TeacherProfileInline(self.model, self.admin_site)]
        return []

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'student_id', 'college_name', 'degree', 'semester', 'attendance_target')
    search_fields = ('user__username', 'user__email', 'student_id', 'college_name')
    list_filter = ('semester', 'degree')

@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'designation', 'office_location')
    search_fields = ('user__username', 'user__email', 'department')
    list_filter = ('department',)
