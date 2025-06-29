# student_management_app/context_processors.py
def user_role_processor(request):
    user_role = None
    if request.user.is_authenticated:
        user_role = request.user.role
    return {'user_role': user_role}