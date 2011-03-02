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
    is_comment = False
    categoryid = request.GET.get('categoryid')
    postid= request.GET.get('postid')
    
    #check if user is member of group
    custgroup = Group.objects.get(id=groupid)
    if custgroup not in request.user.groups.all():
        return render_to_response('404.html')
    else:
        pass
    
    #check if category is allowed for user
    try:
        cat = Category.objects.get(id=categoryid)
        if cat.group not in request.user.groups.all():
            return render_to_response('404.html')
        else:
            pass
    except ObjectDoesNotExist:
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
                    
            #check if postid exists
            try:
                message = Post.objects.get(id=postid)
                post = Post(
                    title=title, 
                    body=body, 
                    group=custgroup, 
                    category=category,
                    user=user,
                    is_comment = 1
                    )
                is_comment = True
            except ObjectDoesNotExist:
                post = Post(
                    title=title, 
                    body=body, 
                    group=custgroup, 
                    category=category,
                    user=user,)
            
            post.save()
            
            if is_comment:
                comment = Comment(post=message,comment=post)
                comment.save()                    
            else:
                pass
                
            """
            Get all users in the group an save to Unread model
            """
            groupusers = User.objects.filter(groups__name=custgroup.name)
            for g in groupusers:
                unread = Unread(
                         user = g,
                         post = post,
                         category = category,
                         marked_read_on = datetime.now().replace(microsecond=0).isoformat(' '),
                        )
                unread.save()
            success = True
            
    else:
        form = AddMessageForm(
                initial={'groupname': custgroup.name,'groupid': groupid},
            )
        
        if(categoryid):
            form.fields['category'].choices = \
                [(x.id, x.name) for x in Category.objects.filter(id=categoryid)]
        else:
            form.fields['category'].choices = \
                [(x.id, x.name) for x in Category.objects.filter(group=groupid)]

    data = {
            "groupid": groupid,
            'categoryid': categoryid,
            "groupname": custgroup.name,
            "form": form,
        }
        
    if success:
        messages.add_message(request, messages.SUCCESS, 'Message was successfuly posted.')
        #return HttpResponseRedirect('/message/dashboard') 
        #return HttpResponseRedirect("/message/view/%s" % (post.id),data, context_instance=RequestContext(request)) 
        if is_comment:
            return HttpResponseRedirect("/message/view/%s" % (message.id)) 
        else:
            return HttpResponseRedirect("/message/view/%s" % (post.id)) 
        
    else:
        if postid:
            #return HttpResponseRedirect("/message/view/%s?error=1" % (postid)) 
            return render_to_response("message/view_message.html",
                          data, context_instance=RequestContext(request))
        else:    
            return render_to_response("message/post_message.html",
                          data, context_instance=RequestContext(request))

@login_required            
def view(request, messageid):
    """
    View a message.
    """
    
    error = None
    """
    not really an error but from the ?error=1
    1 => "Please fill out all the required fields."
    """
    error_passed = request.GET.get('error')
    if error_passed == "1":
        messages.add_message(request, messages.ERROR, 'Please fill out all the required fields.')
    
    message = get_object_or_404(Post, id=messageid)
    custgroup = Group.objects.get(id=message.group_id)
    
    if custgroup not in request.user.groups.all():
         return render_to_response('404.html')
    else:
        pass 
    
    unread = get_object_or_404(Unread, user=request.user, post=message)
    if not unread.marked_read_on:
        unread.marked_read_on = datetime.now().replace(microsecond=0).isoformat(' ')
        unread.save()
    
    commentform = AddCommentForm(
            initial={'postid': message.id,
                    'groupname': custgroup.name,
                    'groupid': message.group_id,
                    'category': message.category_id,
                }
        )
        
    comments = Comment.objects.filter(post=message).order_by('-comment__published')
    #comments = Unread.objects.filter(post=message)
    all_comments = []
    """
    for c in comments:
       all_comments += [(x.id, x.marked_read_on, c.comment) \
                        for x in c.post.unread_set.filter(post=c.id,user=request.user)]
    """
    for c in comments:
        all_comments += [(c.id, c.comment.id, c.comment.title, c.comment.user, \
                        c.comment.published, c.comment.body, \
                        Unread.objects.get(user=c.comment.user, post=c.comment).marked_read_on)]
     
       
    data = {
            'commentform': commentform,
            'message': message,
            'comments': comments,
            'all_comments': all_comments,
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
    #posts = Post.objects.filter(group=groupid)
    posts = Post.objects.filter(group=groupid)
    
    all_posts = []
   
    for p in posts:
        all_posts += [(x.id, x.marked_read_on, p) for x in p.unread_set.filter(post=p.id)]
    
    data = {
            'groupname':custgroup.name,
            #'posts':posts,
            'posts': all_posts,
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
    
    category = Category.objects.get(id=categoryid)    
    #posts = get_list_or_404(Post, category=categoryid)
    posts = Post.objects.filter(category=categoryid,is_comment=0).order_by('-published')
    all_posts = []
   
    for p in posts:
        all_posts += [(x.id, x.marked_read_on, p, \
                        Unread.objects.filter(marked_read_on__isnull=True, post=p, category=p.category_id, user=request.user, post__is_comment=1), \
                        Unread.objects.filter(category=p.category_id, user=request.user, post__is_comment=1).count(), \
                    ) \
                    for x in p.unread_set.filter(post=p.id,user=request.user)]
    
    data = {
            'groupid':custgroup.id,
            'groupname':custgroup.name,
            'categoryid':category.id,
            'categoryname':category.name,
            'posts':all_posts,
    }
    return render_to_response('message/by_category.html', data,context_instance=RequestContext(request))
    