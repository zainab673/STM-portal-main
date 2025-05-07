from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from .models import UserProfile, Teacher  # Import the Teacher model
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Timetable
from openpyxl import Workbook
from django.http import HttpResponse, FileResponse
import os
from django.conf import settings
import platform
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect  # Correct import
import json
import requests
from django.http import JsonResponse
from .models import ContactMessage
from django.core.paginator import Paginator
from django.db.models import Q, F
from django.db.models.functions import Length
from .forms import TeacherForm  # You'll need to create this form

# Hardcoded verification codes for each role
VERIFICATION_CODES = {
    "student": "STUDENT123",
    "teacher": "TEACHER456",
    "admin": "ADMIN789",
}


def index(request):
    # Check if the role is passed in the URL
    role = request.GET.get('role', None)
    if role:
        # Store the role in the session
        request.session['role'] = role
        print(f"Role stored in session: {role}")
        return redirect('signup')  # Redirect to signup page
    return render(request, 'index.html')



def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Get role from POST or fallback to GET
        selected_role = request.POST.get('role') or request.GET.get('role') or ''
        selected_role = selected_role.lower().strip()

        print(f"🔍 Role from POST: {request.POST.get('role')}")
        print(f"🔍 Role from GET: {request.GET.get('role')}")
        print(f"✅ Final selected_role: {selected_role}")

        try:
            user_obj = UserProfile.objects.get(username=username)
        except UserProfile.DoesNotExist:
            return render(request, 'login.html', {
                'error': 'User not found. Please create an account.',
                'role': selected_role
            })

        user = authenticate(request, username=username, password=password)

        if user is not None:
            print(f"✅ User role from DB: {user.role.lower()}")
            if user.role.lower().strip() != selected_role:
                return render(request, 'login.html', {
                    'error': 'Role mismatch. Please select the correct role.',
                    'role': selected_role
                })

            login(request, user)
            request.session['role'] = user.role
            print(f"🔓 Logged in as: {user.username}, Role: {user.role}")

            # Redirect by role
            if user.role.lower() == 'student':
                return redirect('student_panel')
            elif user.role.lower() == 'teacher':
                return redirect('teacher_panel')
            elif user.role.lower() == 'admin':
                return redirect('admin_panel')
        else:
            return render(request, 'login.html', {
                'error': 'Incorrect password. Please try again.',
                'role': selected_role
            })

    # Handle GET request
    role = request.GET.get('role', '').lower()
    return render(request, 'login.html', {'role': role})



def signup_view(request):
    print(f"🔍 Session Data: {dict(request.session)}")
    role = request.session.get('role', None)

    if not role:
        role = request.POST.get('role', '').lower()  # Fetch role from POST if not in session
        if role:
            request.session['role'] = role  # Store the role in session for future requests
        else:
            print("No role found! Redirecting to index...")
            return redirect('index')

    print(f"Fetched role from session or POST: {role}")

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        verification_code = request.POST['verification_code']

        expected_code = VERIFICATION_CODES.get(role, '')
        print(f"Expected Code: {expected_code}, Received: {verification_code}")

        # Check if the verification code is correct
        if verification_code != expected_code:
            print("Invalid verification code!")
            messages.error(request, 'Invalid verification code! Please enter the correct code.')  # Error message
            return render(request, 'signup.html', {'role': role})

        if UserProfile.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists. Please choose another one.')  # Error for existing username
            return render(request, 'signup.html', {'role': role})

        # Create user and assign role
        try:
            user = UserProfile.objects.create_user(username=username, email=email, password=password)
            user.role = role
            user.save()
            print(f"User {username} created successfully!")

             # After signup, log the user in
            login(request, user)
            print(f"🔍 User {user.username} logged in with ID: {request.session.get('_auth_user_id')}")
            print(f"🔍 Role assigned: {user.role}")
            messages.success(request, '🎉 Account created successfully!')

            if role == 'teacher':
                Teacher.objects.create(user=user, verification_code=verification_code)  # Create Teacher record
                print(f"Teacher profile created for user: {username}")
        except Exception as e:
             messages.error(request, f'An error occurred during signup: {e}')
             return render(request, 'signup.html', {'role': role})

        # After signup, log the user in
        login(request, user)
        print(f"🔍 User {username} logged in with ID: {request.session.get('_auth_user_id')}")
        print(f"🔍 Role assigned: {user.role}")
        messages.success(request, '🎉 Account created successfully!')

        # Check the role and redirect to the correct dashboard
        if user.role == 'student':
            print("Redirecting to student dashboard.")
            return redirect('student_panel')
        elif user.role == 'teacher':
            return redirect('teacher_panel')
        elif user.role == 'admin':
            return redirect('admin_panel')
    return render(request, 'signup.html', {'role': role})



def student_panel(request):
    return render(request, "studentpanel.html")



def teacher_panel(request):
    return render(request, "teacherpanel.html")


def admin_panel(request):
    unread_messages = ContactMessage.objects.filter(is_read=False).order_by('-timestamp')
    unread_messages_count = unread_messages.count()
    context = {
        'unread_messages': unread_messages,
        'unread_messages_count': unread_messages_count,
    }
    return render(request, "adminpanel.html", context)



def select_semester(request):
    return render(request, 'selectsem.html')
# EXCEL SHEET FOR ATTENDANCE
def open_attendance(request):
    if request.method == "POST":
        semester = request.POST.get("semester")
        subject = request.POST.get("subject")

        if not semester or not subject:
            return HttpResponse("Please select both semester and subject.")

        # File name and folder
        file_name = f"{subject.replace(' ', '_')}_Semester{semester}.xlsx"
        folder_path = os.path.join(settings.MEDIA_ROOT, "attendance_files")
        file_path = os.path.join(folder_path, file_name)

        # Ensure folder exists
        os.makedirs(folder_path, exist_ok=True)

        # If file doesn't exist, create it
        if not os.path.exists(file_path):
            wb = Workbook()
            ws = wb.active
            ws.title = "Attendance"

            # Write only Semester and Subject
            ws['A1'] = f"Semester: {semester}"
            ws['A2'] = f"Subject: {subject}"

            wb.save(file_path)

        # If the teacher wants to download the file
        if 'download' in request.POST:
            if os.path.exists(file_path):
                try:
                    # Serve the file using FileResponse
                    response = FileResponse(open(file_path, 'rb'),
                                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
                    return response
                except Exception as e:
                    return HttpResponse(f"Error occurred while trying to serve the file: {str(e)}")
            else:
                return HttpResponse("File does not exist. Please try again later.")

        # If the teacher wants to open the file (for Windows only)
        if platform.system() == "Windows":
            os.startfile(file_path)
            return HttpResponse("Excel file opened successfully!")

        # For non-Windows systems
        return HttpResponse("File created. Please open it manually (non-Windows system).")

    return HttpResponse("Invalid request method.")
# TIMETABLE FOR ALL SEMESTERS
def timetable_view(request):
    semester = request.GET.get('semester', '1')  # Default to Semester 1 if nothing is passed

    # Query the database to get the timetable for the selected semester
    timetable = Timetable.objects.filter(semester=semester)

    # Pass the timetable data to the template
    context = {
        'semester': semester,
        'timetable': timetable
    }

    return render(request, 'timetable.html', context)


def show_timetable(request, semester):
    timetable = Timetable.objects.filter(semester=semester).order_by('day', 'timing')
    return render(request, 'timetable.html', {
        'timetable': timetable,
        'semester': semester,
    })
# Edit Timetable
def edit_timetable(request, lecture_id):
    # Get the lecture object to edit
    lecture = get_object_or_404(Timetable, id=lecture_id)

    if request.method == 'POST':
        subject = request.POST.get('subject')
        instructor = request.POST.get('instructor')
        timing = request.POST.get('timing')
        classroom = request.POST.get('classroom')

        if not subject or not instructor or not timing or not classroom:
            return render(request, 'edit_timetable.html', {
                'lecture': lecture,
                'semester': lecture.semester,
                'error_message': 'All fields are required.'
            })

        # Update
        lecture.subject = subject
        lecture.instructor = instructor
        lecture.timing = timing
        lecture.classroom = classroom
        lecture.save()

        return redirect('show_timetable', semester=lecture.semester)

    return render(request, 'edit_timetable.html', {
        'lecture': lecture,
        'semester': lecture.semester
    })
# Delete Timetable
def delete_timetable(request, lecture_id):
    # Get the lecture object to delete
    lecture = get_object_or_404(Timetable, id=lecture_id)

    if request.method == 'POST':
        semester = lecture.semester  # save before deleting
        lecture.delete()
        return redirect('show_timetable', semester=semester)

    return render(request, 'delete_timetable.html', {
        'lecture': lecture,
        'semester': lecture.semester
    })


def chatbot(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get("message", "")

            api_key = "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"  # Replace with your API key

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8000/",  # If you are testing locally
                "X-Title": "Scholar Sphere Chatbot"  # Your project title
            }

            body = {
                "model": "openai/gpt-3.5-turbo",  # 📢 Make sure model name is correct
                "messages": [
                    {"role": "system",
                     "content": "You are an educational assistant helping students and staff."},
                    {"role": "user", "content": message}
                ]
            }

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=body
            )

            # Log the response for debugging
            result = response.json()

            if response.status_code == 200:
                answer = result['choices'][0]['message']['content'].strip()
                return JsonResponse({'response': answer})
            else:
                return JsonResponse({'error': 'API error', 'details': result}, status=500)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
def submit_contact_form(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        if name and email and message:
            ContactMessage.objects.create(name=name, email=email, message=message)
            return HttpResponse("success")
        else:
            return HttpResponse("error", status=400)
    else:
        return redirect('index')



def read_message(request, message_id):
    message = get_object_or_404(ContactMessage, id=message_id)
    message.is_read = True
    message.save()
    return redirect('admin_panel')


@csrf_protect
def delete_message(request, message_id):
    if request.method == 'POST':
        message = get_object_or_404(ContactMessage, id=message_id)
        message.delete()
    return redirect('admin_panel')
from django.shortcuts import render, redirect, get_object_or_404
from .models import Teacher
from .forms import TeacherForm  # You'll need to create this form

from django.core.paginator import Paginator
from django.shortcuts import render
from django.db.models import Q, F, Value, Case, When, IntegerField  # Import When as well
from django.db.models.functions import Length
from .models import Teacher
from .forms import TeacherForm

def teacher_list(request):
    teachers = Teacher.objects.all()

    # Search
    search_term = request.GET.get('search')
    if search_term:
        teachers = teachers.filter(
            Q(user__username__icontains=search_term) |
            Q(user__email__icontains=search_term) |
            Q(subject_taught__icontains=search_term) |
            Q(department__icontains=search_term)
        )
        # Annotate with a 'relevance' score.  Prioritize username matches.
        teachers = teachers.annotate(
            relevance=Case(
                When(user__username__icontains=search_term, then=Value(10)),  # High priority
                When(user__email__icontains=search_term, then=Value(5)),      # Medium priority
                default=Value(1),
                output_field=IntegerField(),
            ),
            name_length=Length('user__username')
        ).order_by('-relevance', 'name_length')

    # Sorting
    sort_by = request.GET.get('sort')
    if sort_by:
        if sort_by == 'username':
            teachers = teachers.order_by('user__username')
        elif sort_by == 'email':
            teachers = teachers.order_by('user__email')
        elif sort_by == 'department':
            teachers = teachers.order_by('department')
        else:
            teachers = teachers.order_by('id')  # Default ordering

    # Pagination
    paginator = Paginator(teachers, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_term': search_term,
        'sort_by': sort_by,
    }
    return render(request, 'admin_teachers.html', context)

def teacher_edit(request, teacher_id):
    teacher = get_object_or_404(Teacher, pk=teacher_id)
    if request.method == 'POST':
        form = TeacherForm(request.POST, instance=teacher)
        if form.is_valid():
            form.save()
            return redirect('teacher_list')
    else:
        form = TeacherForm(instance=teacher)
    return render(request, 'admin_teacher_form.html', {'form': form, 'teacher': teacher})


import logging
from django.shortcuts import render, redirect, get_object_or_404
from .models import Teacher
from django.contrib import messages
from django.urls import reverse
from django.http import Http404

logger = logging.getLogger(__name__)

def teacher_delete(request, pk):
    try:
        teacher = get_object_or_404(Teacher, pk=pk)
        teacher_username = "this teacher"  # Default username if no related user
        if teacher.user:
            teacher_username = teacher.user.username

        if request.method == 'GET':
            teacher.delete()
            messages.success(request, f"Teacher '{teacher_username}' deleted successfully.")
            return redirect(reverse('teacher_list'))
        return redirect(reverse('teacher_list'))
    except Http404:
        logger.error(f"Teacher with pk={pk} not found for deletion.")
        messages.error(request, "Deleted Successfully.")
        return redirect(reverse('teacher_list'))
