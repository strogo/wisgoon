from django.shortcuts import render

from models import Post

def home(request):
	post_pending = Post.objects.filter(status=0).count()
	print "post pending ", post_pending
	return render(request, 'dashboard/home.html', {"post_pending": post_pending})

def photos(request):
	return render(request, 'dashboard/photos.html')

def home_base(request):
	return render(request, 'dashboard/home.html')