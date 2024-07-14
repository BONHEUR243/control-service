from django.contrib import admin
from django.urls import path,include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('Custom_user.urls')),
    path('',include('students_admins.urls')),
]
