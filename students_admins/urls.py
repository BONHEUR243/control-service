from django.contrib import admin
from django.urls import path
from .import views
from django.conf import settings
from django.conf.urls.static import static
from .views import  exam_status_admin, exam_status_student,claim, view_claims, reply_claim,check_rfid,learnUse
from Custom_user.views import get_options, get_sessions, get_intakes, get_levels

urlpatterns = [
    
    path('profile',views.profile,name='profile'),
    
    path('schedule', views.schedule, name='schedule'),
    path('add_schedule', views.add_schedule, name='add_schedule'),
    path('modify_schedule/<int:exam_id>/', views.modify_schedule, name='modify_schedule'),
    path('schedule/grouped/', views.schedule, name='schedule'), 
    
    path('manage_students/', views.manage_students, name='manage_students'),
    path('manage_reference_amounts/', views.manage_reference_amounts, name='manage_reference_amounts'),
    path('manage_student_details/<int:student_id>/', views.manage_student_details, name='manage_student_details'),
    path('upload_profile_picture/', views.upload_profile_picture, name='upload_profile_picture'),
    
    path('claim/', claim, name='claim'),
    path('claims/', view_claims, name='view_claims'),
    path('claims/reply/<int:message_id>/', reply_claim, name='reply_claim'),
    

    path('exam_status_admin/', exam_status_admin, name='exam_status_admin'),
    path('exam_status_student/', exam_status_student, name='exam_status_student'),
    path('check_rfid/', check_rfid, name='check_rfid'),
    
    path('learnUse/',learnUse,name='learnUse'),
    
    #pour js
    path('get_options/<int:departement_id>/', get_options, name='get_options'),
    path('get_sessions/<int:option_id>/', get_sessions, name='get_sessions'),
    path('get_intakes/<int:session_id>/', get_intakes, name='get_intakes'),
    path('get_levels/<int:intake_id>/', get_levels, name='get_levels'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)