from rest_framework import serializers
from .models import Student, Attendance


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'first_name', 'last_name', 'rfid_uid']


class AttendanceSerializer(serializers.ModelSerializer):
    student = StudentSerializer()

    class Meta:
        model = Attendance
        fields = ['student', 'check_in_time', 'check_out_time']
