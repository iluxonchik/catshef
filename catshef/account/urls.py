from django.conf.urls import url, include
from django.contrib import admin
from account import views

urlpatterns = [
    url(r'^$', views.profile, name='profile'),
    url(r'^', include('allauth.urls')), 
]