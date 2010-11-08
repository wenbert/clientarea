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
def browse_files(request,groupname):
    data = {}
    user = request.user
    
    url_dir = request.GET.get('dir')
    
    path = settings.APPLICATION_STORAGE

    files = []
    directories= []
    
        
    custgroup = Group.objects.get(name=groupname)
    if custgroup not in request.user.groups.all():
         return render_to_response('404.html')
    else:
        pass

    grouppath = os.path.join(path, str(groupname)) #join group
    
    if request.GET.get('dir'):
        grouppath = os.path.join(grouppath,str(url_dir))
        if settings.APPLICATION_STORAGE not in grouppath: #make sure that grouppath is inside the APPLICATION_STORAGE
            return render_to_response('404.html')
        elif "../" in grouppath: #make sure not to allow relative paths, etc.
            return render_to_response('404.html')

    if os.path.exists(str(grouppath)):
        contents = os.listdir(str(grouppath)) #contents of the current directory
        for i in contents:
            if os.path.isfile(os.path.join(grouppath, i)):
                if request.GET.get('dir'):
                    files.append({'name':i,'path':os.path.join(url_dir,i),'group':groupname})
                else:
                    files.append({'name':i,'path':i,'group':groupname})
            if os.path.isdir(os.path.join(grouppath, i)):
                if request.GET.get('dir'):
                    directories.append({'name':i,'path':os.path.join(url_dir,i),'group':groupname})
                else:
                    directories.append({'name':i,'path':i,'group':groupname})
    
    """
    Split URL pieces using the "os.path.seperator-thingy"
    There should be something like that...
    """
    url_pieces = str(url_dir).split(os.sep)
    crumbs = []
    for i in range(len(url_pieces)):
        #url_pieces[i] += str(url_pieces[i-1]),str(os.pathsep),str(url_pieces[i])
        crumbs.append({'name':url_pieces[i],'path':str(url_pieces[0:i]).replace(" ","").replace("[","").replace("]","").replace("'","").replace(",","/")})
        #crumbs.append({'path': url_pieces[0:i]})
    
    data = {
        "location": path,
        "url_dir": url_dir,
        "files": files,
        "directories": directories,
        "grouppath": grouppath,
        "groupname": groupname,
        "url_pieces": url_pieces,
        "crumbs": crumbs,
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