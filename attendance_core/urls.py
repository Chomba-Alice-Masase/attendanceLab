
from django.urls import path, include
from .views import check_in_or_out, attendance_data,  attendance_page

urlpatterns = [
    path('attendance-page/', attendance_page, name='attendance_page'),
    path('api/check-in-out/', check_in_or_out, name='check_in_or_out'),
    path('api/attendance-data', attendance_data, name='attendance_data'),
]