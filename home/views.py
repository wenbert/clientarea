import os,sys,tempfile, zipfile, time
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
    path = settings.APPLICATION_STORAGE
    data = {}
    files = []
    directories= []
    
    url_dir = request.GET.get('dir')
    
    #check if group of request.user
    custgroup = Group.objects.get(name=groupname)
    if custgroup not in request.user.groups.all():
         return render_to_response('404.html')
    else:
        pass

    #complete path of the directory with the groupname
    grouppath = os.path.join(path, str(groupname)) 
    
    if url_dir:
        grouppath = os.path.join(grouppath,str(url_dir))
        if settings.APPLICATION_STORAGE not in grouppath: 
            #make sure that grouppath is inside the APPLICATION_STORAGE
            return render_to_response('404.html')
        elif "../" in grouppath: 
            #make sure not to allow relative paths, etc.
            return render_to_response('404.html')

    if os.path.exists(str(grouppath)):
        contents = os.listdir(str(grouppath)) #contents of the current directory
        for i in contents:
            complete_filepath = os.path.join(grouppath, i)
            
            #check if URL has a directory specified. 
            #If directory is set, join it with "i"
            if url_dir:
                    temp_path = os.path.join(url_dir,i)
            else:
                temp_path = i
            
            if os.path.isfile(complete_filepath):                    
                #get current readme for each file displayed
                readme_file = "%s%s"%(complete_filepath,settings.README_FILE_EXT)
               
                if (readme_file):
                #if str(os.path.splitext(i)[0][-1])==str(settings.README_FILE_EXT):
                    readme = os.path.join(grouppath, i)
                    if os.path.exists(str(readme_file)):
                        readme = open(readme_file).read()
                    else:
                        readme = 'File has no description.'
                else:
                    pass
                        
                
                #append to file[], but do not include README
                if i != settings.README_FILE and os.path.splitext(i)[-1] != settings.README_FILE_EXT:
                    files.append({'name':i,\
                                  'path':temp_path,\
                                  'size':
                                        convert_bytes (
                                            os.path.getsize(complete_filepath)\
                                        ),\
                                  'last_modified': \
                                        pretty_date(\
                                            os.path.getctime(complete_filepath)\
                                        ),\
                                  'group':groupname,
                                  'readme':readme,
                                })
                              
            if os.path.isdir(complete_filepath):
                #get current readme for each directory displayed
                readme = os.path.join(grouppath, settings.README_FILE)
                if os.path.exists(str(readme)):
                    readme = open(readme).read()
                else:
                    readme = 'Directory has no description.'
                    
                #append to directories
                directories.append({'name':i,\
                               'path':temp_path,\
                               'size':
                                    convert_bytes (
                                        os.path.getsize(complete_filepath)\
                                    ),\
                                'last_modified': \
                                    pretty_date(\
                                        os.path.getctime(complete_filepath)\
                                    ),\
                               'group':groupname,
                               'readme':readme,
                            })
    
    """
    Breadcrumbs
    """
    url_pieces = str(url_dir).split(os.sep)
    crumbs = []
    for i in range(len(url_pieces)):
        crumbs.append({\
                'name':url_pieces[i],
                'path':str(url_pieces[0:i+1]) \
                      .replace(" ","")\
                      .replace("[","")\
                      .replace("]","")\
                      .replace("'","")\
                      .replace(",","/")
                })
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
    filepath = os.path.join(path,filename)
    filename = filepath
    wrapper = FileWrapper(file(filename))
    
    response = HttpResponse(wrapper, mimetype='application/force-download')
    
    response['Content-Length'] = os.path.getsize(filename)
    response['Content-Disposition'] = 'attachment; filename=%s' \
                                       % smart_str(filename)

    return response

def convert_bytes(bytes):
    bytes = float(bytes)
    if bytes >= 1099511627776:
        terabytes = bytes / 1099511627776
        size = '%.2f Tb' % terabytes
    elif bytes >= 1073741824:
        gigabytes = bytes / 1073741824
        size = '%.2f Gb' % gigabytes
    elif bytes >= 1048576:
        megabytes = bytes / 1048576
        size = '%.2f Mb' % megabytes
    elif bytes >= 1024:
        kilobytes = bytes / 1024
        size = '%.2f Kb' % kilobytes
    else:
        size = '%.2f bytes' % bytes
    return size

def pretty_date(time=False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    http://stackoverflow.com/questions/1551382/python-user-friendly-time-format
    """
    from datetime import datetime
    now = datetime.now()
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif not time:
        diff = now - now
    else:
        diff = now - datetime.fromtimestamp(time)
        
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return  "a minute ago"
        if second_diff < 3600:
            return str( second_diff / 60 ) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str( second_diff / 3600 ) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 31:
        return str(day_diff/7) + " weeks ago"
    if day_diff < 365:
        return str(day_diff/30) + " months ago"
    return str(day_diff/365) + " years ago"
    
def show_time(time_in_seconds_from_epoc):
    t = time.localtime(time_in_seconds_from_epoc)
    return time.strftime(settings.TIME_FORMAT, t)
    