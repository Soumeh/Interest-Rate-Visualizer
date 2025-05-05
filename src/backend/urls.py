"""
https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path
from src.backend import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dash-example/', views.dash_example, name='dash_example'),
]
