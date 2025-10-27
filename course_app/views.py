from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import Profile, Course,Registration
from .forms import RegistrationForm, LoginForm,CourseForm
from django.contrib.auth.decorators import login_required
from datetime import timedelta, date


from django.http import HttpResponse
import csv


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


from django.shortcuts import render
from .models import Course, Registration
from django.contrib.auth.decorators import login_required

@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('student_dashboard')

    # --- Filtering ---
    q = request.GET.get('q', '')
    duration = request.GET.get('duration', '')

    courses = Course.objects.all()
    if q:
        courses = courses.filter(course_name__icontains=q)
    if duration:
        courses = courses.filter(duration__iexact=duration)

    registrations = Registration.objects.select_related('course').all()

    students = User.objects.filter(is_superuser=False).order_by('-date_joined')

    context = {
        'courses': courses,
        'registrations': registrations,
        'students': students, 
        'total_courses': courses.count(),
        'total_students': students.count(),  
        'total_registrations': registrations.count(),
    }
    return render(request, 'admin_dashboard.html', context)



@login_required
def student_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.is_superuser:
        return redirect('admin_dashboard')

    # Fetch all courses
    courses = Course.objects.all()

    # Apply filters
    search_query = request.GET.get('q')
    duration_filter = request.GET.get('duration')

    if search_query:
        courses = courses.filter(course_name__icontains=search_query)
    if duration_filter:
        courses = courses.filter(duration=duration_filter)

    # Fetch registered courses for this student
    registered_courses = Registration.objects.filter(student_name=request.user.username)
    registered_course_ids = registered_courses.values_list('course_id', flat=True)

    return render(request, 'student_dashboard.html', {
        'courses': courses,
        'registered_courses': registered_courses,
        'registered_course_ids': registered_course_ids,  # ✅ new context
    })



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
    
    if Registration.objects.filter(student_name=request.user.username, course=course).exists():
        messages.warning(request,f"you have already registered for {course.course_name}.")
        return redirect('student_dashboard')
    

    Registration.objects.create(
        student_name = request.user.username,
        course=course
    )
    
    messages.success(request, f"you have successfully registered for {course.course_name}!")
    
    return redirect('student_dashboard')
    # if request.method == 'POST':
    #     Registration.objects.create(
    #         student_name=request.user.username,  # use username or any name
    #         course=course
    #     )
    #     return redirect('student_dashboard')

    # return render(request, 'register_course.html', {'course': course})


def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    return render(request, 'course_detail.html', {'course': course})

def export_registrations(request):
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="registrations.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Name', 'Email', 'Course'])

    for reg in Registration.objects.all():
        writer.writerow([reg.id, reg.name, reg.email, reg.course])

    return response

def registration_detail(request, registration_id):
    registration = get_object_or_404(Registration, id=registration_id)
    return render(request, 'registration_detail.html', {'registration': registration})

def delete_registration(request, registration_id):
    registration = get_object_or_404(Registration, id=registration_id)
    registration.delete()
    return redirect('admin_dashboard')

def report_active_courses(request):
    # Filter courses that are active (assuming a boolean field named 'is_active')
    active_courses = Course.objects.filter(is_active=True)
    return render(request, 'report_active_courses.html', {'active_courses': active_courses})

def report_registrations_last_30(request):
    today = date.today()
    last_30_days = today - timedelta(days=30)
    recent_registrations = Registration.objects.filter(created_at__gte=last_30_days)

    return render(request, 'report_registrations_last_30.html', {'recent_registrations': recent_registrations})

def site_settings(request):
    return render(request, 'site_settings.html')

def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        course_name = request.POST.get('course_name')
        duration = request.POST.get('duration')
        description = request.POST.get('description')

        course.course_name = course_name
        course.duration = duration
        course.description = description
        course.save()

        messages.success(request, 'Course updated successfully.')
        return redirect('admin_dashboard')

    return render(request, 'edit_course.html', {'course': course})

def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Course deleted successfully.')
        return redirect('admin_dashboard')
    
    # Optional: If someone visits the URL via GET, just redirect
    return redirect('admin_dashboard')

@login_required
def student_profile(request, student_id):
    student = get_object_or_404(Profile, user__id=student_id)
    return render(request, 'student_profile.html', {'student': student})

@login_required
def deactivate_user(request, user_id):
    if not request.user.is_superuser:
        return redirect('student_dashboard')
    
    user = get_object_or_404(User, id=user_id)
    user.is_active = False  # deactivate the account
    user.save()
    
    messages.success(request, f"{user.username} has been deactivated.")
    return redirect('admin_dashboard')

@login_required
def edit_student(request, student_id):
    if not request.user.is_superuser:
        return redirect('student_dashboard')
    student = get_object_or_404(User, id=student_id)
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        if full_name:
            parts = full_name.split()
            student.first_name = parts[0]
            student.last_name = ' '.join(parts[1:]) if len(parts) > 1 else ''
        student.email = email
        student.save()
        messages.success(request, f"{student.username}'s details updated successfully!")
    return redirect('admin_dashboard')


@login_required
def delete_student(request, student_id):
    if not request.user.is_superuser:
        return redirect('student_dashboard')
    student = get_object_or_404(User, id=student_id)
    student.delete()
    messages.success(request, "Student deleted successfully.")
    return redirect('admin_dashboard')
