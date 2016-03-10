from django.shortcuts import render


def home(request):
    return render(request, 'dashboard/post/home.html')


def reported(request):
    return render(request, 'dashboard/post/reported.html')


def user_activity(request):
    return render(request, 'dashboard/post/user_activity.html')


def logs(request):
    return render(request, 'dashboard/post/logs.html')


def ads(request):
    return render(request, 'dashboard/post/ads.html')


def catregory(request):
    return render(request, 'dashboard/post/category.html')
