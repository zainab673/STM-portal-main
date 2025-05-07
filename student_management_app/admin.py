# from django.contrib import admin

# # Register your models here.
# from .models import Timetable  # Timetable model ko import karte hain

# class TimetableAdmin(admin.ModelAdmin):
#     list_display = ('semester', 'subject', 'instructor', 'timing', 'classroom','day')  # Admin panel mein yeh fields dikhayein
#     search_fields = ('subject', 'instructor')  # Yeh search enable karega subject aur instructor ke liye

# # Timetable model ko admin panel mein register karna
# admin.site.register(Timetable, TimetableAdmin)
# # admin.py

# from .models import UserProfile

# admin.site.register(UserProfile)
from django.contrib import admin

# Register your models here.
from .models import Timetable  # Timetable model ko import karte hain

class TimetableAdmin(admin.ModelAdmin):
    list_display = ('semester', 'subject', 'instructor', 'timing', 'classroom','day')  # Admin panel mein yeh fields dikhayein
    search_fields = ('subject', 'instructor')  # Yeh search enable karega subject aur instructor ke liye

# Timetable model ko admin panel mein register karna
admin.site.register(Timetable, TimetableAdmin)
# admin.py

from .models import UserProfile

admin.site.register(UserProfile)
