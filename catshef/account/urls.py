from django.conf.urls import url, include
from django.contrib import admin
from account import views

urlpatterns = [
    url(r'^profile/$', views.edit_profile, name='edit_profile'),
    url(r'^$', views.profile, name='profile'),
    url(r'^', include('allauth.urls')), 
]