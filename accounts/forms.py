from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, StudentProfile, TeacherProfile

class LoginForm(forms.Form):
    username_or_email = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition',
            'placeholder': 'Enter your username or email',
            'autocomplete': 'username',
        }),
        label="Username or Email"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition',
            'placeholder': '••••••••',
            'autocomplete': 'current-password',
        }),
        label="Password"
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-indigo-600 bg-slate-100 border-slate-300 rounded focus:ring-indigo-500 dark:focus:ring-indigo-600 dark:ring-offset-slate-800 focus:ring-2 dark:bg-slate-700 dark:border-slate-600',
        }),
        label="Remember this device"
    )

    def clean(self):
        cleaned_data = super().clean()
        username_or_email = cleaned_data.get('username_or_email')
        password = cleaned_data.get('password')

        if username_or_email and password:
            # Check if input is email or username
            user = None
            if '@' in username_or_email:
                try:
                    user_obj = User.objects.get(email__iexact=username_or_email)
                    user = authenticate(username=user_obj.username, password=password)
                except User.DoesNotExist:
                    user = None
            else:
                user = authenticate(username=username_or_email, password=password)

            if not user:
                raise forms.ValidationError("Invalid credentials. Please verify your username/email and password.")
            if not user.is_active:
                raise forms.ValidationError("This account has been deactivated. Please contact support.")
            cleaned_data['user'] = user

        return cleaned_data


class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition',
            'placeholder': 'Create a secure password',
            'autocomplete': 'new-password',
        }),
        label="Password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition',
            'placeholder': 'Re-enter your password',
            'autocomplete': 'new-password',
        }),
        label="Confirm Password"
    )
    degree = forms.CharField(
        required=False,
        initial="B.Tech Computer Science",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition',
            'placeholder': 'e.g. B.Tech Computer Science, B.Sc, MBA',
        }),
        label="Degree / Major"
    )
    semester = forms.IntegerField(
        required=False,
        initial=5,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition',
            'placeholder': '1 - 8',
            'min': '1',
            'max': '12',
        }),
        label="Current Semester"
    )
    college_name = forms.CharField(
        required=False,
        initial="Apex University",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition',
            'placeholder': 'e.g. Apex Institute of Technology',
        }),
        label="University / College"
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'role']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition',
                'placeholder': 'e.g. Alex',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition',
                'placeholder': 'e.g. Sharma',
            }),
            'username': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition',
                'placeholder': 'alexsharma',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition',
                'placeholder': 'alex@example.com',
            }),
            'role': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 transition',
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email address already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password:
            if password != confirm_password:
                self.add_error('confirm_password', "Passwords do not match.")
            else:
                validate_password(password)
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            if user.role == User.Role.STUDENT and hasattr(user, 'student_profile'):
                profile = user.student_profile
                profile.degree = self.cleaned_data.get('degree') or profile.degree
                profile.semester = self.cleaned_data.get('semester') or profile.semester
                profile.college_name = self.cleaned_data.get('college_name') or profile.college_name
                profile.save()
        return user


class StudentProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = [
            'student_id', 'college_name', 'degree', 'semester',
            'academic_year', 'attendance_target', 'daily_study_target_minutes',
            'preferred_language', 'career_interest'
        ]
        widgets = {
            'student_id': forms.TextInput(attrs={'class': 'form-input-modern'}),
            'college_name': forms.TextInput(attrs={'class': 'form-input-modern'}),
            'degree': forms.TextInput(attrs={'class': 'form-input-modern'}),
            'semester': forms.NumberInput(attrs={'class': 'form-input-modern', 'min': 1, 'max': 12}),
            'academic_year': forms.TextInput(attrs={'class': 'form-input-modern'}),
            'attendance_target': forms.NumberInput(attrs={'class': 'form-input-modern', 'step': '0.5', 'min': 50, 'max': 100}),
            'daily_study_target_minutes': forms.NumberInput(attrs={'class': 'form-input-modern', 'min': 30, 'max': 720}),
            'preferred_language': forms.Select(attrs={'class': 'form-input-modern'}),
            'career_interest': forms.TextInput(attrs={'class': 'form-input-modern'}),
        }


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'avatar', 'phone_number', 'bio']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input-modern'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input-modern'}),
            'email': forms.EmailInput(attrs={'class': 'form-input-modern'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-input-modern'}),
            'bio': forms.Textarea(attrs={'class': 'form-input-modern', 'rows': 3}),
        }
