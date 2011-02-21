from message.models import *
from django.utils.html import strip_tags
from django.contrib.auth.decorators import permission_required
import os,sys,tempfile, zipfile, time, re
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse, Http404
from django.core.exceptions import ObjectDoesNotExist
from django.utils.encoding import smart_str
import datetime
from message.forms import *
from django.template import Context, loader, RequestContext
from django.conf import settings
from django.core.servers.basehttp import FileWrapper
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group

@login_required  
def dashboard(request):
    data = {}    
    return render_to_response("message/dashboard.html",
                          data, context_instance=RequestContext(request))
                          
def post_message(request, groupid):
    path = settings.APPLICATION_STORAGE
    data = {}
    
    #check if user is member of group
    custgroup = Group.objects.get(id=groupid)
    if custgroup not in request.user.groups.all():
        return render_to_response('404.html')
    else:
        pass
    
    form = AddMessageForm(
            initial={'groupname': custgroup.name},
        )
        
    form.fields['categories'].choices = \
            [(x.id, x.name) for x in Category.objects.filter(group=groupid)]
    
    data = {
        "groupid": groupid,
        "groupname": custgroup.name,
        "form": form,
    }
    return render_to_response("message/post_message.html",
                          data, context_instance=RequestContext(request))