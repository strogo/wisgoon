# Create your views here.
from django.shortcuts import render_to_response
from pin.forms import PinForm
from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponseBadRequest, Http404,\
    HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf.global_settings import MEDIA_ROOT

def home(request):
    return render_to_response('pin/home.html',context_instance=RequestContext(request))

@login_required
def send(request):
    if request.method == "POST":
        form = PinForm(request.POST)
        if form.is_valid():
            model = form.save(commit=False)
            model.user = request.user
            model.save()
            
            return HttpResponseRedirect('/pin/')
    else:
        form = PinForm()
    return render_to_response('pin/send.html',{'form': form}, context_instance=RequestContext(request))


def save_upload( uploaded, filename, raw_data ):
    ''' raw_data: if True, upfile is a HttpRequest object with raw post data
        as the file, rather than a Django UploadedFile from request.FILES '''
    try:
        from io import FileIO, BufferedWriter
        with BufferedWriter( FileIO( "feedreader/media/pin/%s" % ( filename), "wb" ) ) as dest:

            if raw_data:
                foo = uploaded.read( 1024 )
                while foo:
                    dest.write( foo )
                    foo = uploaded.read( 1024 ) 
            # if not raw, it was a form upload so read in the normal Django chunks fashion
            else:
                for c in uploaded.chunks( ):
                    dest.write( c )
            return 1
    except IOError:
        # could not open the file most likely
        return 0

@csrf_exempt
def upload(request):
    if request.method == "POST":    
    # AJAX Upload will pass the filename in the querystring if it is the "advanced" ajax upload
        if request.is_ajax( ):
            # the file is stored raw in the request
            upload = request
            is_raw = True
            try:
                filename = request.GET[ 'qqfile' ]
            except KeyError: 
                return HttpResponseBadRequest( "AJAX request not valid" )
        # not an ajax upload, so it was the "basic" iframe version with submission via form
        else:
            is_raw = False
            if len( request.FILES ) == 1:
                # FILES is a dictionary in Django but Ajax Upload gives the uploaded file an
                # ID based on a random number, so it cannot be guessed here in the code.
                # Rather than editing Ajax Upload to pass the ID in the querystring, note that
                # each upload is a separate request so FILES should only have one entry.
                # Thus, we can just grab the first (and only) value in the dict.
                upload = request.FILES.values( )[ 0 ]
            else:
                raise Http404( "Bad Upload" )
            filename = upload.name
         
        # save the file
        success = save_upload( upload, filename, is_raw )
            
        import json
        ret_json = success
        return HttpResponse( json.dumps( ret_json ) )
        
    