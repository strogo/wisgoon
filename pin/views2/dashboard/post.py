from django.shortcuts import render


def home(request):
    return render(request, 'dashboard/post/home.html')


def reported(request):
    return render(request, 'dashboard/post/reported.html')
