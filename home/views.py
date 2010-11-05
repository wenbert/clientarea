from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse, Http404
from django.core.exceptions import ObjectDoesNotExist
from django.template import Context, loader, RequestContext
from django.conf import settings
import os,sys

def home(request):
    data = {}    
    return render_to_response("home/home.html",
                          data, context_instance=RequestContext(request))
    
def browse_files(request):
    data = {}
    path = settings.APPLICATION_STORAGE

    contents = os.listdir(path) #contents of the current directory
    files = []
    directories= []
    
    for i in contents:
        #files.append(i)
        """
        os.path.isfile(i) does not work properly?
        Reading path: /home/subsea/application/../application/home 
            ['__init__.py', '__init__.pyc']
        """
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