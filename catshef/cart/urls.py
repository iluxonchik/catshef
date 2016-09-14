from django.conf.urls import url, include
from django.contrib import admin
from cart import views

urlpatterns = [
    url(r'^add/$', views.add_to_cart, name='cart_add'),
    url(r'^remove/$', views.remove_from_cart, name='cart_remove'),
    url(r'^clear/$', views.clear_cart, name='cart_clear'),
]
