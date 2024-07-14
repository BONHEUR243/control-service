from django.contrib import admin
from django.conf import settings
from django.urls import path,include
from django.conf.urls.static import static



urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('Custom_user.urls')),
    path('',include('students_admins.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)