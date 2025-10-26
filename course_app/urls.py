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
    path('course_detail/<int:course_id>/', views.course_detail, name='course_detail')


]

