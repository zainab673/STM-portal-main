from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings  # Import settings for AUTH_USER_MODEL

# Custom User Model
class UserProfile(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')

    def __str__(self):
        return f"{self.username} ({self.role})"

# Course Model
class Course(models.Model):
    SEMESTER_CHOICES = [
        (1, 'Semester 1'),
        (2, 'Semester 2'),
        (3, 'Semester 3'),
        (4, 'Semester 4'),
        (5, 'Semester 5'),
        (6, 'Semester 6'),
        (7, 'Semester 7'),
        (8, 'Semester 8'),
    ]
    course_name = models.CharField(max_length=100, default="Untitled Course")
    course_code = models.CharField(max_length=100, unique=True, default='CS101')
    teacher = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role': 'teacher'}
    )
    semester_number = models.PositiveIntegerField(choices=SEMESTER_CHOICES, default=1)

    def __str__(self):
        return f"{self.course_name} ({self.course_code})"

# Student Model (Changed to StudentProfile)
class StudentProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile'  # Added related name
    )
    semester = models.IntegerField(
        choices=[(i, f'Semester {i}') for i in range(1, 9)]
    )
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    cnic = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.user.username


# Attendance Model
class Attendance(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE) # Changed to StudentProfile
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    attendance_date = models.DateTimeField(default=timezone.now)
    status = models.BooleanField()  # True for present, False for absent

    def __str__(self):
        return f"Attendance of {self.student.user.username} for {self.course.course_name} on {self.attendance_date}"


# Attendance Report Model (removed redundant semester_number)
class AttendanceReport(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE) # Changed to StudentProfile
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    # Removed semester_number since it's already part of Course and Students models
    def __str__(self):
        return f"Report for {self.student.user.username} in {self.course.course_name}"

# Timetable Model
class Timetable(models.Model):
    SEMESTER_CHOICES = [
        (1, 'Semester 1'),
        (2, 'Semester 2'),
        (3, 'Semester 3'),
        (4, 'Semester 4'),
        (5, 'Semester 5'),
        (6, 'Semester 6'),
        (7, 'Semester 7'),
        (8, 'Semester 8'),
    ]

    DAY_CHOICES = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]

    day = models.CharField(max_length=10, choices=DAY_CHOICES, default='Monday')  # 👈 ye line add ki gayi
    semester = models.IntegerField(choices=SEMESTER_CHOICES)
    subject = models.CharField(max_length=100)
    instructor = models.CharField(max_length=100)
    timing = models.CharField(max_length=50)
    classroom = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.subject} - Semester {self.semester} ({self.day})"

    def clean(self):
        # Check if a class is already scheduled in the same classroom at the same time and day
        conflicting_timetable = Timetable.objects.filter(
            day=self.day,
            timing=self.timing,
            classroom=self.classroom
        ).exclude(id=self.id)  # Exclude current instance if updating

        if conflicting_timetable.exists():
            raise ValidationError(
                f"A class is already scheduled in {self.classroom} on {self.day} at {self.timing}.")



class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)  # To track if the admin has read the message

    def __str__(self):
        return f"Message from {self.name} ({self.email})"

# Teacher Model
class Teacher(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE, primary_key=True)
    verification_code = models.CharField(max_length=100, blank=True, null=True)
    cnic = models.CharField(max_length=15, blank=True, null=True)
    subject_taught = models.CharField(max_length=100, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    contact_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.user.username


# Notification Model
class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    related_semester = models.IntegerField(
        null=True, blank=True
    )  # Optional: Semester the notification pertains to

    def __str__(self):
        return f"Notification for {self.user.username} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['-timestamp']  # Order by most recent first
# student_management_app/models.py


class Assignment(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateTimeField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assignments_given')
    upload = models.FileField(upload_to='assignments/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title