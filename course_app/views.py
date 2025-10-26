from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import Profile, Course,Registration
from .forms import RegistrationForm, LoginForm,CourseForm
from django.contrib.auth.decorators import login_required



def index(request):
    # If user is logged in, redirect based on role
    # if request.user.is_authenticated:
    #     if request.user.is_superuser:
    #         return redirect('admin_dashboard')
    #     elif hasattr(request.user, 'profile') and request.user.profile.role == 'student':
    #         return redirect('student_dashboard')

    # If not logged in, show top 3 courses on index page
    courses = Course.objects.all()[:3]
    return render(request, 'index.html', {'courses': courses})

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            profile_photo = form.cleaned_data.get('profile_photo')
            profile = Profile.objects.create(user=user, role='student')
            if profile_photo:
                profile.profile_photo = profile_photo
                profile.save()

            messages.success(request, "Registration successful! Please login.")
            return redirect('login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome, {user.username}!")

                # Redirect logic
                if user.is_superuser:
                    return redirect('admin_dashboard')
                else:
                    return redirect('student_dashboard')
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')


@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('student_dashboard')

    total_students = Profile.objects.filter(role='student').count()
    total_courses = Course.objects.count()
    total_registrations = Registration.objects.count()

    registrations = Registration.objects.select_related('course').all()

    context = {
        'total_students': total_students,
        'total_courses': total_courses,
        'total_registrations': total_registrations,
        'registrations': registrations,
    }
    return render(request, 'admin_dashboard.html', context)

@login_required
def student_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.is_superuser:
        return redirect('admin_dashboard')

    courses = Course.objects.all()
    search_query = request.GET.get('q')
    duration_filter = request.GET.get('duration')

    if search_query:
        courses = courses.filter(course_name__icontains=search_query)
    if duration_filter:
        courses = courses.filter(duration=duration_filter)

    return render(request, 'student_dashboard.html', {'courses': courses})

@login_required
def add_course(request):
    if not request.user.is_superuser:
        return redirect('student_dashboard')

    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Course added successfully!")
            return redirect('admin_dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CourseForm()

    return render(request, 'add_course.html', {'form': form})

def register_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    if request.method == 'POST':
        Registration.objects.create(
            student_name=request.user.username,  # use username or any name
            course=course
        )
        return redirect('student_dashboard')

    return render(request, 'register_course.html', {'course': course})


def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    return render(request, 'course_detail.html', {'course': course})