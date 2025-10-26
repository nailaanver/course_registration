from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    path('add_course/', views.add_course, name='add_course'),
    path('register_course/<int:course_id>/', views.register_course, name='register_course'),
    path('course_detail/<int:course_id>/', views.course_detail, name='course_detail'),
    path('export_registrations/', views.export_registrations, name='export_registrations'),  # ✅ Add this line
    path('registration_detail/<int:registration_id>/', views.registration_detail, name='registration_detail'),  # ✅ Add this line
    path('delete_registration/<int:registration_id>/', views.delete_registration, name='delete_registration'),  # ✅ Add this line
    path('report_active_courses/', views.report_active_courses, name='report_active_courses'),  # ✅ Add this
    path('report_registrations_last_30/', views.report_registrations_last_30, name='report_registrations_last_30'),  # ✅ Add this
    path('site-settings/', views.site_settings, name='site_settings'),
    path('course/edit/<int:course_id>/', views.edit_course, name='edit_course'),  # <-- add this
    path('course/delete/<int:course_id>/', views.delete_course, name='delete_course'),  # <-- Add this




]

