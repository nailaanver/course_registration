from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('admin', 'Admin'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)

    def __str__(self):
        return self.user.username
     
class Course(models.Model):
    DURATION_CHOICE = [
        ('1 Month', '1 Month'),
        ('3 Months', '3 Months'),
        ('6 Months', '6 Months'),
    ]
    course_name = models.CharField(max_length=100)
    duration = models.CharField(max_length=20,choices=DURATION_CHOICE)
    description = models.TextField()
    course_image = models.ImageField(upload_to='course_images/', blank=True, null=True)

    
    def __str__(self):
        return self.course_name
    
class Registration(models.Model):
    student_name = models.CharField(max_length=100)
    course = models.ForeignKey(Course,on_delete=models.CASCADE, related_name='registration')
    date_registered = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.student_name} - {self.course.course_name}"