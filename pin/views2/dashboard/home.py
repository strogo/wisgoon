from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect


@login_required
def home(request):
    if not request.user.is_superuser:
        return HttpResponseRedirect('/')
    return render(request, 'dashboard/home.html')
