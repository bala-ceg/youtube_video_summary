# example/urls.py
from django.urls import path

from render import views
from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path("", views.home, name= "home"),
    path('yt_show', views.yt_show, name= "yt_show")
]
