from django.shortcuts import render

def dash_example(request):
    return render(request, 'template/test.html')
