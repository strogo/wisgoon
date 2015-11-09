from django.shortcuts import render


def home(request):
    return render(request, 'angular/home.html')


def latest(request):
    # get date from http://wisgoon.com/api/v6/post/latest/
    return render(request, 'angular/latest.html')
