from django.urls import path
from . import views



urlpatterns = [
    
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    # path('select_role/<str:role>/',views.select_role, name='select_role'), 
    path('teacherpanel/', views.teacher_panel, name='teacher_panel'),
    path('studentpanel/', views.student_panel, name='student_panel'),
    path('adminpanel/',   views.admin_panel, name='admin_panel'),
    path('selectsem/', views.select_semester, name='selectsem'),
    path('open_attendance/', views.open_attendance, name='open_attendance'),
    path('timetable/<int:semester>/', views.show_timetable, name='show_timetable'),
    path('edit/<int:lecture_id>/', views.edit_timetable, name='edit_timetable'),
    path('delete/<int:lecture_id>/', views.delete_timetable, name='delete_timetable'),
    path('chatbot/', views.chatbot, name='chatbot'),
    path('submit_contact_form/', views.submit_contact_form, name='submit_contact_form'), # Add this line
    path('read_message/<int:message_id>/', views.read_message, name='read_message'),
    path('delete_message/<int:message_id>/', views.delete_message, name='delete_message'),
    path('teachers/', views.teacher_list, name='teacher_list'),
    path('teachers/edit/<int:teacher_id>/', views.teacher_edit, name='teacher_edit'),
    path('teachers/delete/<int:pk>/', views.teacher_delete, name='teacher_delete'),
 
]


