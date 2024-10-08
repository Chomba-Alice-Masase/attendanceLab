from django.contrib import admin

from attendance_core.models import Student, Attendance

# Register your models here.

admin.site.register(Student)
admin.site.register(Attendance)
