import os,sys,tempfile, zipfile
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse, Http404
from django.core.exceptions import ObjectDoesNotExist
from django.utils.encoding import smart_str
from django.template import Context, loader, RequestContext
from django.conf import settings
from django.core.servers.basehttp import FileWrapper
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group

def home(request):
    data = {}    
    return render_to_response("home/home.html",
                          data, context_instance=RequestContext(request))

@login_required    
def browse_files(request):
    data = {}
    user = request.user
    
    path = settings.APPLICATION_STORAGE

    files = []
    directories= []
    
    ugroups = user.groups.all()
    
    for ugroup in ugroups:
        grouppath = os.path.join(path, str(ugroup)) #join group
        if request.GET.get('dir'):
            grouppath = os.path.join(grouppath,request.GET.get('dir'))
    
        
        contents = os.listdir(grouppath) #contents of the current directory
        for i in contents:
            #files.append(i)
            if os.path.isfile(os.path.join(grouppath, i)):
            #if os.path.isfile(i):
                if request.GET.get('dir'):
                    files.append(os.path.join(request.GET.get('dir'),i))
                else:
                    files.append(i)
            #elif os.path.isdir(i):
            if os.path.isdir(os.path.join(grouppath, i)):
                if request.GET.get('dir'):
                    directories.append(os.path.join(request.GET.get('dir'),i))
                else:
                    directories.append(i)
            
    data = {
        "location": path,
        "files": files,
        "directories": directories,
        "groups": ugroups,
    }
    
    return render_to_response("home/browse_files.html",
                          data, context_instance=RequestContext(request))
    
@login_required
def download(request,groupname,filename):
    custgroup = Group.objects.get(name=groupname)
    if custgroup not in request.user.groups.all():
         return render_to_response('404.html')
    else:
        pass
    
    path = settings.APPLICATION_STORAGE
    filename = os.path.join(groupname,filename)
    filepath = os.path.join(path,filename)# Select your file here. 
    filename = filepath # Select your file here.                                
    wrapper = FileWrapper(file(filename))
    
    #response = HttpResponse()
    response = HttpResponse(wrapper, mimetype='application/force-download')
    
    response['Content-Length'] = os.path.getsize(filename)
    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(filename)

    return response