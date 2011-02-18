import os,sys,tempfile, zipfile, time, re
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse, Http404
from django.core.exceptions import ObjectDoesNotExist
from django.utils.encoding import smart_str
from django.template import Context, loader, RequestContext
from django.conf import settings
from django.core.servers.basehttp import FileWrapper
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from home.forms import *
from django.core.exceptions import ObjectDoesNotExist
import datetime
from home.models import *
from contextlib import closing
from zipfile import ZipFile, ZIP_DEFLATED
import simplejson as json
from home.models import *
from user import *
from django.utils.html import strip_tags

@login_required  
def home(request):
    data = {}    
    return render_to_response("home/home.html",
                          data, context_instance=RequestContext(request))
@login_required
def directories(request):
    data = {}    
    return render_to_response("home/directories.html",
                        data, context_instance=RequestContext(request))  

@login_required    
def browse_files(request,groupname):
    """
    Browse a directory. This can go browse the sub-directories using the
    ?dir=/path/to/subdirectory
    """
    path = settings.APPLICATION_STORAGE
    prev_location = ""
    readme_last_modified = ""
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
    
    #if dir in the URL is set, append the dir from the GET to the grouppath
    if url_dir:
        grouppath = os.path.join(grouppath,str(url_dir))
        
        #check if grouppath string contains the APPLICATION_STORAGE string
        #if so, then trim it
        #grouppath = grouppath.replace(path,"xxx")
        
        #some security checks so that users will not be able 
        #to "navigate" out of their folders
        if settings.APPLICATION_STORAGE not in grouppath: 
            #make sure that grouppath is inside the APPLICATION_STORAGE
            return render_to_response('404.html')
        elif "../" in grouppath: 
            #make sure not to allow relative paths, etc.
            return render_to_response('404.html')
            
        prev_location = "/home/browse_files/%s/?dir=%s"\
                        % (groupname,"/".join(url_dir.split("/")[0:-1]))
    
    if os.path.exists(str(grouppath)):
        #look for README for the current directory
        readme_for_current_dir = ""
        readme_for_current_dir_path = os.path.join(grouppath,"README")
        if os.path.exists(str(readme_for_current_dir_path)):
            readme_for_current_dir = open(readme_for_current_dir_path).read()
        else:
            readme_for_current_dir = "This directory has no description."
        
        #contents of the current directory. If there was a path dir in the 
        #dir varialbe in GET, grouppath should now contain that path
        contents = os.listdir(str(grouppath)) 
        
        count = 0
        for i in contents:
            complete_filepath = os.path.join(grouppath, i)
            
            #check if URL has a directory specified. 
            #If directory is set, join it with "i"
            if url_dir:
                    temp_path = os.path.join(url_dir,i)
            else:
                temp_path = i
            
            #check if "i" is a file
            if os.path.isfile(complete_filepath):             
                #get current readme for each file displayed
                readme_file = "%s%s"\
                              %(complete_filepath,settings.README_FILE_EXT)
                              
                if (readme_file):
                    desc_file_editedby = ''
                    readme = os.path.join(grouppath, i)
                    if os.path.exists(str(readme_file)):
                        readme = open(readme_file).read()
                        readme_last_modified = pretty_date(os.path.getmtime(readme_file))
                        try:
                            pass
                            #Desclog = Desclogs(groupname=groupname,file_path=complete_filepath).latest('datetime').user
                        except ObjectDoesNotExist:
                            pass
                            #desc_file_editedby = '%s %s'%(groupname,complete_filepath)
                            #desc_file_editedby = '-'
                    else:
                        readme = '-'
                else:
                    pass
                    
                #file extension and icon
                file_icon = ""
                file_extension = complete_filepath.split(".")[-1]
                file_icon = get_icon(file_extension)
                        
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
                                  'extension':file_extension,
                                  'file_icon':file_icon,
                                  'id':count,
                                  'readme_last_modified': readme_last_modified,
                                  'desc_file_editedby': desc_file_editedby,
                                })
            
            #check if "i" is a directory                  
            if os.path.isdir(complete_filepath):
                #get current readme for each directory displayed
                readme = os.path.join(complete_filepath, settings.README_FILE)
                if os.path.exists(str(readme)):
                    readme = open(readme).read()
                else:
                    readme = '-'
                    
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
                                'id':count,
                                  'readme_last_modified': readme_last_modified,
                                  'desc_file_editedby': desc_file_editedby,
                            })
                            
            count += 1
    else:
        pass
        
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
        "current_directory": os.path.basename(grouppath),
        "groupname": groupname,
        "url_pieces": url_pieces,
        "crumbs": crumbs,
        "readme_for_current_dir": readme_for_current_dir,
        "test": readme_for_current_dir_path,
        "prev_location": prev_location,
        "form": EditDescForm(),
    }
    
    return render_to_response("home/browse_files.html",
                          data, context_instance=RequestContext(request))

@login_required
def save_readme(request):
    """
    create or edit the .README file
    """
    success = False
    error = None
    filelines = ''
    
    if request.method == 'POST' and request.is_ajax():
        
        
        form = EditDescForm(request.POST)
        if form.is_valid():
            
            dialog_desc = form.cleaned_data['dialog_desc']
            groupname = form.cleaned_data['dialog_groupname']
            filename = form.cleaned_data['dialog_filename']
            
            custgroup = Group.objects.get(name=groupname)
            if custgroup not in request.user.groups.all():
                 return render_to_response('404.html')
            else:
                pass 
            
            path = settings.APPLICATION_STORAGE
            grouppath = os.path.join(path, str(groupname)) 
            grouppath = os.path.join(grouppath,str(filename))
            check_access_to_grouppath(grouppath)
            readme_for_current_path = ""
            
            #look for README for the current file
            readme_current = ""
            
            if os.path.isfile(grouppath):
                readme_for_current_path = "%s%s"%(grouppath,settings.README_FILE_EXT)
            else:
                readme_for_current_path = "%s/%s"%(grouppath,settings.README_FILE)
            try:
                readme_current = open(readme_for_current_path, 'r')
                #filelines = "%s by: %s"%(strip_tags(dialog_desc),request.user)
                filelines = "%s"%(strip_tags(dialog_desc))
                desc_logs = Desclogs(
                    groupname = groupname,
                    file_path = grouppath,
                    user = request.user,
                    old_desc = readme_current.read(),
                )
                desc_logs.save()
                readme_current.close()
                readme_current = open(readme_for_current_path, 'w')
                readme_current.truncate()
                readme_current.write(filelines)
                readme_current.close()
                success = True
            except IOError as (errno, strerror):
                error = "I/O error({0}): {1}".format(errno, strerror)    
            except:
                error =  "Unexpected error:", sys.exc_info()[0]
                raise
                
    else:
        pass
            
    if success:
        if request.is_ajax():
            results = {
                "readme_for_current_path": readme_for_current_path,
                "groupname": groupname,
                "grouppath": grouppath,
                "dialog_desc":filelines, 
                "filename":filename,
                "status":"success",
                "message": "Saved.",
            }
            data = json.dumps(results)
            return HttpResponse(data)
    else:
        data = json.dumps({"status":"failed", "error":error, "data":request.POST, 'grouppath': grouppath})
        return HttpResponse(data)
        
@login_required
def add_comment(request,groupname,filename):
    """
    add file path to model
    """
    custgroup = Group.objects.get(name=groupname)
    if custgroup not in request.user.groups.all():
         return render_to_response('404.html')
    else:
        pass 
        
    fc = Filecomments(
        groupname = groupname,
        file_path = filename,
    )
    fc.save()
    data = {
        "file_id" : fc.id,
        "file_path": filename,
        "groupname": groupname,
    }
    return render_to_response("home/file_comment.html",
                          data, context_instance=RequestContext(request))
    
@login_required
def download(request,groupname,filename):
    """
    Download a file
    """
    custgroup = Group.objects.get(name=groupname)
    if custgroup not in request.user.groups.all():
         return render_to_response('404.html')
    else:
        pass 
        
    path = settings.APPLICATION_STORAGE
    filename = os.path.join(groupname,filename)
    filepath = os.path.join(path,filename)
    filename = filepath
    
    response = HttpResponse(mimetype='application/force-download') 
    response['Content-Disposition']='attachment;filename="%s"'\
                                    %smart_str(filename)
    response["X-Sendfile"] = filename
    response['Content-length'] = os.stat(filename).st_size
    
    log_action(request,filepath,os.stat(filename).st_size)   
    return response
    
    """
    wrapper = FileWrapper(file(filename))
    response = HttpResponse(wrapper, mimetype='application/force-download')
    
    response['Content-Length'] = os.path.getsize(filename)
    response['Content-Disposition'] = 'attachment; filename=%s' \
                                       % smart_str(filename)
    return response
    """
    
@login_required
def download_dir_as_zip(request,groupname):
    """
    Download a directory or a file as zip.
    This is disabled for now. Will have to confirm if Python creates a zipfile
    in the memory. The ideal thing would be to create a temp zip file and
    pass the "path" of that zip through x-sendfile.
    
    THIS IS CURRENTLY DISABLED
    """
    return False
    
    path = settings.APPLICATION_STORAGE    
    url_dir = request.GET.get('dir')    
    #check if group of request.user
    custgroup = Group.objects.get(name=groupname)
    if custgroup not in request.user.groups.all():
         return render_to_response('404.html')
    else:
        pass
        
    #complete path of the directory with the groupname
    grouppath = os.path.join(path, str(groupname)) 
    
    #if dir in the URL is set, append the dir from the GET to the grouppath
    if url_dir:
        grouppath = os.path.join(grouppath,str(url_dir))
        #some security checks so that users will not be able 
        #to "navigate" out of their folders
        if settings.APPLICATION_STORAGE not in grouppath: 
            #make sure that grouppath is inside the APPLICATION_STORAGE
            return render_to_response('404.html')
        elif "../" in grouppath: 
            #make sure not to allow relative paths, etc.
            return render_to_response('404.html')
            
    temp = tempfile.TemporaryFile()
    archivename = os.path.basename(grouppath) + ".zip" # archive in the curdir
    #zipdir(grouppath, archivename)
    assert os.path.isdir(grouppath)
    with closing(ZipFile(temp, "w", ZIP_DEFLATED)) as z:
        for root, dirs, files in os.walk(grouppath):
            #NOTE: ignore empty directories
            for fn in files:
                absfn = os.path.join(root, fn)
                zfn = absfn[len(grouppath)+len(os.sep):] #XXX: relative path
                z.write(absfn, zfn)

    wrapper = FileWrapper(temp)
    response = HttpResponse(wrapper, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=' + archivename
    response['Content-Length'] = temp.tell()
    temp.seek(0)
    return response


@login_required
def download_file_as_zip(request,groupname,filename):
    """
    Download a file as zipfile.
    This is disabled for now. Will have to confirm if Python creates a zipfile
    in the memory. The ideal thing would be to create a temp zip file and
    pass the "path" of that zip through x-sendfile.
    
    THIS IS CURRENTLY DISABLED
    """
    return False
    
    custgroup = Group.objects.get(name=groupname)
    if custgroup not in request.user.groups.all():
         return render_to_response('404.html')
    else:
        pass
    
    path = settings.APPLICATION_STORAGE
    filename = os.path.join(groupname,filename)
    filepath = os.path.join(path,filename)
    
    temp = tempfile.TemporaryFile()
    archive = zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED)
    archive.write(filepath, os.path.basename(filename))
    archive.close()
    
    wrapper = FileWrapper(temp)
    response = HttpResponse(wrapper, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=%s.zip'\
                                      %(os.path.basename(filename))
    response['Content-Length'] = temp.tell()
    temp.seek(0)
    return response

def convert_bytes(bytes):
    """
    Convert file sizes to human readable ones.
    I forgot to credit the author of this code. I forgot where I found it.
    If you know, then please email me. wenbert[at]gmail[dot]com
    """
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
            return str(second_diff) + " second(s) ago"
        if second_diff < 120:
            return  "a minute ago"
        if second_diff < 3600:
            return str( second_diff / 60 ) + " minute(s) ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str( second_diff / 3600 ) + " hour(s) ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " day(s) ago"
    if day_diff < 31:
        return str(day_diff/7) + " week(s) ago"
    if day_diff < 365:
        return str(day_diff/30) + " month(s) ago"
    return str(day_diff/365) + " year(s) ago"
    
def show_time(time_in_seconds_from_epoc):
    t = time.localtime(time_in_seconds_from_epoc)
    return time.strftime(settings.TIME_FORMAT, t)
    
def get_icon(file_extension):
    """
    Using Silk Icons
    http://www.famfamfam.com/lab/icons/silk/
    
    Returns page_white.png as the default icon.
    """
    file_icon = "page_white.png"
    if file_extension == "zip" or file_extension == "rar"\
        or file_extension == "gz" or file_extension == "7z":
        file_icon = "compress.png"
    elif file_extension == "pdf":
        file_icon = "page_white_acrobat.png"
    elif file_extension == "doc" \
        or file_extension == "docx" \
        or file_extension == "rtf":
        file_icon = "page_word.png"
    elif file_extension == "ppt" or file_extension == "pptx":
        file_icon = "page_white_powerpoint.png"
    elif file_extension == "html" \
        or file_extension == "htm":
        file_icon = "page_world.png"
    elif file_extension == "xls" \
        or file_extension == "xlsx":
        file_icon = "page_white_excel.png"
    elif file_extension == "png"\
        or file_extension == "jpg" or file_extension == "jpeg"\
        or file_extension == "gif"\
        or file_extension == "tif" or file_extension == "tiff":
        file_icon = "picture.png"
    elif file_extension == "cad" or file_extension == "dxf":
        file_icon = "map.png"
    elif file_extension == "pds" or file_extension == "all":
        file_icon == "bricks.png"
    elif file_extension == "txt"\
        or file_extension == "csv"\
        or file_extension == "asc"\
        or file_extension == "tab":
        file_icon = "page_white_text.png"
    elif file_extension == "rln" or file_extension == "rlx":
        file_icon = "chart_line.png"
    elif file_extension == "xyz":
        file_icon = "script_gear.png"
    else:
        file_icon = "page_white.png"
        
    return file_icon
    
def check_access_to_grouppath(grouppath):
    if settings.APPLICATION_STORAGE not in grouppath: 
        #make sure that grouppath is inside the APPLICATION_STORAGE
        return render_to_response('404.html')
    elif "../" in grouppath: 
        #make sure not to allow relative paths, etc.
        return render_to_response('404.html')

def log_action(request,target,log_size):
    """
    Logs a file download.
    """
    try:
        log = Log(
            user            = request.user,
            log_target      = target,
            log_ip          = request.META['REMOTE_ADDR'],
            log_size        = log_size,
            log_user_agent  = request.META['HTTP_USER_AGENT'],
            log_ref         = request.META['HTTP_REFERER'],
            log_lang        = request.META['HTTP_ACCEPT_LANGUAGE'],
        )
        log.save()
    except NameError, e:
        raise e