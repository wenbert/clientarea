import os,sys,tempfile, zipfile
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse, Http404
from django.core.exceptions import ObjectDoesNotExist
from django.utils.encoding import smart_str
from django.template import Context, loader, RequestContext
from django.conf import settings
from django.core.servers.basehttp import FileWrapper
from django.contrib.auth.decorators import login_required

def home(request):
    data = {}    
    return render_to_response("home/home.html",
                          data, context_instance=RequestContext(request))

@login_required    
def browse_files(request):
    data = {}
    path = settings.APPLICATION_STORAGE

    contents = os.listdir(path) #contents of the current directory
    files = []
    directories= []
    
    for i in contents:
        #files.append(i)
        if os.path.isfile(os.path.join(path, i)):
        #if os.path.isfile(i):
            files.append(i)
        #elif os.path.isdir(i):
        if os.path.isdir(os.path.join(path, i)):
            directories.append(i)
    data = {
        "location": path,
        "files": files,
        "directories": directories,
    }
    
    return render_to_response("home/browse_files.html",
                          data, context_instance=RequestContext(request))
                          
@login_required
def download(request, filename):
   
    path = settings.APPLICATION_STORAGE
    filepath = os.path.join(path,filename)# Select your file here. 
    filename = filepath # Select your file here.                                
    wrapper = FileWrapper(file(filename))
    
    #response = HttpResponse()
    response = HttpResponse(wrapper, mimetype='application/force-download')
    
    
    response['Content-Length'] = os.path.getsize(filename)
    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(filename)
    


    return response
    return response