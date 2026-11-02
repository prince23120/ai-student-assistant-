from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .forms import LoginForm, RegisterForm, UserUpdateForm, StudentProfileUpdateForm
from .models import User, StudentProfile

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to AI Student Assistant, {user.first_name or user.username}! Your academic workspace is ready.")
            return redirect('dashboard:home')
        else:
            messages.error(request, "Please correct the errors below to create your account.")
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            remember_me = form.cleaned_data.get('remember_me')
            login(request, user)

            if remember_me:
                request.session.set_expiry(1209600)  # 2 weeks
            else:
                request.session.set_expiry(0)  # browser close

            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('dashboard:home')
        else:
            messages.error(request, "Invalid login credentials. Please try again.")
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "You have been successfully signed out.")
    return redirect('accounts:login')


@login_required
def profile_view(request):
    user = request.user
    student_profile = getattr(user, 'student_profile', None)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, request.FILES, instance=user)
        profile_form = StudentProfileUpdateForm(request.POST, instance=student_profile) if student_profile else None

        if user_form.is_valid() and (profile_form is None or profile_form.is_valid()):
            user_form.save()
            if profile_form:
                profile_form.save()
            messages.success(request, "Your profile details have been successfully updated.")
            return redirect('accounts:profile')
        else:
            messages.error(request, "Please check the form for errors.")
    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = StudentProfileUpdateForm(instance=student_profile) if student_profile else None

    return render(request, 'accounts/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'user_obj': user,
    })


@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep user logged in
            messages.success(request, "Your password was successfully updated!")
            return redirect('accounts:profile')
        else:
            messages.error(request, "Please correct the password errors below.")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'accounts/change_password.html', {'form': form})
