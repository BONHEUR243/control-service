from django.contrib import admin
from django.urls import path,include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns



urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('Custom_user.urls')),
    path('',include('students_admins.urls')),
]

urlpatterns += staticfiles_urlpatterns()