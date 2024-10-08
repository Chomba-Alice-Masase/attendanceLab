from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Student, Attendance
from django.utils.timezone import now
from django.shortcuts import render
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)


def attendance_page(request):
    return render(request, 'attendance.html')  # Ensure 'attendance.html' is the correct path to your template


@api_view(['POST'])
def check_in_or_out(request):
    logger.info(f"Request data: {request.data}")  # Log the request data
    rfid_uid = request.data.get('rfid_uid')

    # If no RFID UID is present in the request data, respond with a 400 Bad Request
    if not rfid_uid:
        logger.error("RFID UID is missing in the request")
        return Response({'error': 'RFID UID is required'}, status=400)

    try:
        # Attempt to find the student by RFID UID
        student = Student.objects.get(rfid_uid=rfid_uid)
        attendance, created = Attendance.objects.get_or_create(student=student, check_out_time__isnull=True)

        if created:
            # Student is checking in
            attendance.check_in_time = now()
            attendance.save()
            logger.info(f"Checked in: {student.first_name}")
            return Response({
                'status': 'checked_in',
                'student': {
                    'first_name': student.first_name,
                    'last_name': student.last_name,
                    'check_in_time': attendance.check_in_time.strftime("%Y-%m-%d %H:%M:%S")
                }
            }, status=200)
        else:
            # Student is checking out
            attendance.check_out_time = now()
            attendance.save()
            logger.info(f"Checked out: {student.first_name}")
            return Response({
                'status': 'checked_out',
                'student': {
                    'first_name': student.first_name,
                    'last_name': student.last_name,
                    'check_out_time': attendance.check_out_time.strftime("%Y-%m-%d %H:%M:%S")
                }
            }, status=200)

    except Student.DoesNotExist:
        # If the student is not found, prompt for first and last name
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')

        # If names are provided, create a new student profile
        if first_name and last_name:
            # Create new student
            new_student = Student.objects.create(first_name=first_name, last_name=last_name, rfid_uid=rfid_uid)
            attendance = Attendance(student=new_student, check_in_time=now(), check_out_time=None)
            attendance.save()
            logger.info(f"Created new student profile: {new_student.first_name}")
            return Response({
                'status': 'created',
                'student': {
                    'first_name': new_student.first_name,
                    'last_name': new_student.last_name,
                    'check_in_time': attendance.check_in_time.strftime("%Y-%m-%d %H:%M:%S")
                }
            }, status=201)

        logger.error(f"RFID UID not found: {rfid_uid}, but no name provided for new student")
        return Response({'error': 'RFID UID not found and no name provided for new student'}, status=404)

    except Exception as e:
        # Log any other exceptions and return a 500 Internal Server Error response
        logger.error(f"Unexpected error: {str(e)}")
        return Response({'error': 'An unexpected error occurred'}, status=500)


@api_view(['GET'])
def attendance_data(request):
    attendance_records = Attendance.objects.select_related('student').all()
    data = [
        {
            'student': {
                'first_name': record.student.first_name,
                'last_name': record.student.last_name,
            },
            'check_in_time': record.check_in_time.strftime("%Y-%m-%d %H:%M:%S") if record.check_in_time else None,
            'check_out_time': record.check_out_time.strftime("%Y-%m-%d %H:%M:%S") if record.check_out_time else None,
        }
        for record in attendance_records
    ]
    return JsonResponse(data, safe=False)
