import os,sys,tempfile, zipfile, time, re
from django.shortcuts import render_to_response, redirect, get_object_or_404, get_list_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.utils.encoding import smart_str
from django.template import Context, loader, RequestContext
from django.conf import settings
from django.core.servers.basehttp import FileWrapper
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from home.forms import *
from message.forms import *
from django.core.exceptions import ObjectDoesNotExist
import datetime
from home.models import *
from contextlib import closing
from zipfile import ZipFile, ZIP_DEFLATED
import simplejson as json
from home.models import *
from message.models import *
from user import *
from django.utils.html import strip_tags
from django.contrib.auth.decorators import permission_required
from django.contrib import messages

@login_required  
def allmessages(request):
    data = {}    
    return render_to_response("message/dashboard.html",
                          data, context_instance=RequestContext(request))
                          
                                                
def post_message(request, groupid):
    path = settings.APPLICATION_STORAGE
    data = {}
    success = False
    
    #check if user is member of group
    custgroup = Group.objects.get(id=groupid)
    if custgroup not in request.user.groups.all():
        return render_to_response('404.html')
    else:
        pass
        
    if request.method == 'POST':
        form = AddMessageForm(request.POST,
                    initial={'groupname': custgroup.name,'groupid': groupid}
               )
        
        form.fields['category'].choices = \
                [(x.id, x.name) for x in Category.objects.filter(group=groupid)]
        
        if form.is_valid():
            title = form.cleaned_data['title']
            body = form.cleaned_data['body']
            groupid = form.cleaned_data['groupid']
            category = Category.objects.get(id=form.cleaned_data['category'])
            user =  request.user
            post = Post(
                    title=title, 
                    body=body, 
                    group=custgroup, 
                    category=category,
                    user=user)
            post.save()
            success = True
            
    else:
        form = AddMessageForm(
                initial={'groupname': custgroup.name,'groupid': groupid},
            )
            
        form.fields['category'].choices = \
                [(x.id, x.name) for x in Category.objects.filter(group=groupid)]

    data = {
            "groupid": groupid,
            "groupname": custgroup.name,
            "form": form,
        }
        
    if success:
        messages.add_message(request, messages.SUCCESS, 'Message was successfuly posted.')
        #return HttpResponseRedirect('/message/dashboard') 
        #return HttpResponseRedirect("/message/view/%s" % (post.id),data, context_instance=RequestContext(request)) 
        return HttpResponseRedirect("/message/view/%s" % (post.id)) 
        
    else:
        return render_to_response("message/post_message.html",
                          data, context_instance=RequestContext(request))

@login_required            
def view(request, messageid):
    """
    View a message.
    """
    
    error = None
    message = get_object_or_404(Post, id=messageid)
    custgroup = Group.objects.get(id=message.group_id)
    if custgroup not in request.user.groups.all():
         return render_to_response('404.html')
    else:
        pass 
        
    data = {
            'message':message,
        }
    return render_to_response('message/view_message.html', data,context_instance=RequestContext(request))
    
@login_required
def by_group(request, groupid):
    """
    Displays messages by group.
    """
    data = {}
    success = False
    
    #check if user is member of group
    custgroup = Group.objects.get(id=groupid)
    if custgroup not in request.user.groups.all():
        return render_to_response('404.html')
    else:
        pass
        
    #posts = get_list_or_404(Post, group=groupid)
    posts = Post.objects.filter(group=groupid)
    data = {
            'groupname':custgroup.name,
            'posts':posts,
    }
    return render_to_response('message/by_group.html', data,context_instance=RequestContext(request))
    
@login_required
def by_category(request,groupid ,categoryid):
    """
    Displays messages by category.
    """
    data = {}
    success = False
    
    #check if user is member of group
    custgroup = Group.objects.get(id=groupid)
    if custgroup not in request.user.groups.all():
        return render_to_response('404.html')
    else:
        pass
        
    #posts = get_list_or_404(Post, category=categoryid)
    posts = Post.objects.filter(category=categoryid)
    data = {
            'groupname':custgroup.name,
            'posts':posts,
    }
    return render_to_response('message/by_category.html', data,context_instance=RequestContext(request))
    