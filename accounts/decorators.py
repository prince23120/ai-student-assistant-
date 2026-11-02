from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def role_required(allowed_roles):
    """Decorator ensuring that authenticated user has one of the specified roles."""
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if request.user.role in allowed_roles or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            messages.error(request, "You do not have permission to access that area.")
            return redirect('dashboard:home')
        return _wrapped_view
    return decorator

def student_required(view_func):
    return role_required(['STUDENT'])(view_func)

def teacher_required(view_func):
    return role_required(['TEACHER'])(view_func)

def admin_required(view_func):
    return role_required(['ADMIN'])(view_func)
