from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('teacherpanel/', views.teacher_panel, name='teacher_panel'),
    path('studentpanel/', views.student_panel, name='student_panel'),
    path('adminpanel/', views.admin_panel, name='admin_panel'),
    path('selectsem/', views.select_semester, name='selectsem'),
    path('open_attendance/', views.open_attendance, name='open_attendance'),
    path('chatbot/', views.chatbot, name='chatbot'),
    path('submit_contact_form/', views.submit_contact_form, name='submit_contact_form'),  # Add this line
    path('read_message/<int:message_id>/', views.read_message, name='read_message'),
    path('delete_message/<int:message_id>/', views.delete_message, name='delete_message'),
    path('teachers/', views.teacher_list, name='teacher_list'),
    path('students/', views.student_list, name='student_list'), # Corrected line
    path('students/edit/<int:pk>/', views.student_edit, name='student_edit'),
    path('students/delete/<int:pk>/', views.student_delete, name='student_delete'),
    path('teachers/edit/<int:teacher_id>/', views.teacher_edit, name='teacher_edit'),
    path('teachers/delete/<int:pk>/', views.teacher_delete, name='teacher_delete'),
    path('adminpanel/timetable/', views.admin_timetable, name='admin_timetable'),
    path('adminpanel/courses/', views.admin_courses, name='admin_courses'), # Corrected name
    path('studentpanel/timetable/', views.student_timetable, name='student_timetable'),
    path('teacherpanel/timetable/', views.teacher_timetable, name='teacher_timetable'),
    path('students/', views.student_list, name='student_list'),
    path('teacher_dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('api/notifications/', views.get_notifications, name='get_notifications'),
    path('api/notifications/mark_read/', views.mark_notifications_read, name='mark_notifications_read'),
]
