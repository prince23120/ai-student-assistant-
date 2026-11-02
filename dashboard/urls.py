from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('student/', views.student_dashboard_view, name='student'),
    path('teacher/', views.teacher_dashboard_view, name='teacher'),
    path('admin/', views.admin_dashboard_view, name='admin'),
    path('tasks/<int:task_id>/toggle/', views.toggle_task_status, name='toggle_task'),
    path('recommendations/<int:rec_id>/dismiss/', views.dismiss_recommendation, name='dismiss_recommendation'),
    path('study/quick-log/', views.quick_log_study, name='quick_log_study'),
]
