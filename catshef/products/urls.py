from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^product/(?P<slug>[\w-]+)/$',
        views.product_detail, name='product_detail'),
    url(r'^product/related/(?P<slug>[\w-]+)/$', views.product_related,name='product_related'),
    url(r'^category/(?P<slug>[\w-]+)/$', views.category, name='category'),
]