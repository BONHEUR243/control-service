from django.contrib import admin
from django.urls import path
from .import views
from .views import get_options, get_sessions, get_intakes, get_levels

urlpatterns = [
    path('', views.home,name='home'),
    path('register/',views.register,name='register'),
    path('login/',views.loginUser,name="loginUser"),
    path('logout/',views.logoutUser,name="logoutUser"),
    path('activate/<uidb64>/<token>/',views.activate,name='activate'),
    path('modify/',views.modify,name="modify"),
    path('reset/',views.reset,name="reset"),
    path('reset-confirm/<uidb64>/<token>/',views.resetConfirm,name="reset-confirm"),
    

    #pour js
    path('get_options/<int:departement_id>/', get_options, name='get_options'),
    path('get_sessions/<int:option_id>/', get_sessions, name='get_sessions'),
    path('get_intakes/<int:session_id>/', get_intakes, name='get_intakes'),
    path('get_levels/<int:intake_id>/', get_levels, name='get_levels'),




]