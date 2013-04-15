from contactus.forms import FeedbackFrom
from django.shortcuts import render_to_response
from django.template.context import RequestContext

def home(request):
    form_saved = 0
    if request.method=="POST":
        form = FeedbackFrom(request.POST)
        if form.is_valid():
            form.save()
            form_saved = 1
    else:
        form = FeedbackFrom()
    
    return render_to_response('feedback.html',{'form':form, 'form_saved': form_saved}, context_instance=RequestContext(request))
