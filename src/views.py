from django.shortcuts import render
from django_plotly_dash import DjangoDash

def dash_example(request):
    return render(request, 'dash_app/dash_example.html')