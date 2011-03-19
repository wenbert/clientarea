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
from django.db.models import Avg,Count
from django.db import connection

@login_required  
def allmessages(request):
    data = {}    
    return render_to_response("message/dashboard.html",
                          data, context_instance=RequestContext(request))
                          
                                                
def post_message(request, groupid):
    """
    I created a mess and I need to clean this up. 
    """
    
    """ do not show a message to a client"""
    if request.user.userprofile.is_client:
        return render_to_response('404.html')
        
    path = settings.APPLICATION_STORAGE
    data = {}
    success = False
    is_comment = False
    error = False
    
    categoryid = request.GET.get('categoryid')
    postid= request.GET.get('postid')
    edit = request.GET.get('edit')
    userlist = []
    message_body = ''
    target_id = 0
    update_only = False
    create_new = False
    
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
        
        """user list for this group"""
        form.fields['users'].choices = \
            [(x.id, x) for x in User.objects.filter(groups__name=custgroup.name,userprofile__is_client=0)]    
        
        if form.is_valid():
            title = form.cleaned_data['title']
            body = form.cleaned_data['body']
            groupid = form.cleaned_data['groupid']
            category = Category.objects.get(id=form.cleaned_data['category'])
            user =  request.user
                
            
            """check if postid exists"""
            try:    
                """the POST postid is from the edit form :P"""
                if request.POST.get('postid') == 'None':
                    target_id = 0
                else:
                    target_id = request.POST.get('postid')
                
                """
                we try to check if target_id really exists
                but we also make sure that POST is_comment is not 1 - because comments have parent ids!
                """
                if request.POST.get('is_comment') != '1':
                    post = Post.objects.get(id=target_id)
                    post.title = title
                    post.body = body
                    post.group = custgroup
                    post.category = category
                    post.user = user
                    post.updated = datetime.now()
                    update_only = True
                else:
                    pass
                        
                """gikan ni sa comment"""
                if update_only is False:
                    """get the parent for the comment"""
                    message = Post.objects.get(id=postid)            
                    post = Post(
                        title='test', 
                        body=body, 
                        group=custgroup, 
                        category=category,
                        user=user,
                        is_comment = 1
                    )
                    post.is_comment = 1
                    is_comment = True
                    create_new = True #kay new comment then we need to associate the new comments to the users
                    
                post.save()    
            except ObjectDoesNotExist:
                """a normal post message"""
                post = Post(
                    title=title, 
                    body=body, 
                    group=custgroup, 
                    category=category,
                    user=user,)
                is_comment = False
                create_new = True
                post.save()
            
            if is_comment:
                comment = Comment(post=message,comment=post)
                comment.save()                    
            else:
                pass
            
            """
            User IDs that are selected in the form
            This must be a "post message"?
            """
            if is_comment:
                userlist = [(x.user_id) for x in Unread.objects.filter(post=message)]
                #userlist = [1]
            else:
                userlist = request.POST.getlist('users')    
            
            """this means that edit ni. yes i know we need to do a better job of determining asa gikan ang post"""
            if create_new is True:    
                for u in userlist:
                    if custgroup not in Group.objects.filter(user=u):
                        return render_to_response('404.html')
                    else:
                        pass
                        
                    unread = Unread()
                    unread.user = User.objects.get(id=u)
                    unread.post = post
                    unread.category = category
                    
                    if request.user.id == u:
                        unread.marked_read_on = datetime.now().replace(microsecond=0).isoformat(' ')
                        
                    if is_comment:
                        unread.comment = comment
                        
                    unread.save()
            else:
                """
                not a new entry. userlist came from the Checkboxes in the form
                Add anything in userlist (POST) not existing in Unread
                Delete anything in Unread not found in userlist (POST)
                """
                for u in userlist:
                    if custgroup not in Group.objects.filter(user=u):
                        return render_to_response('404.html')
                    else:
                        pass
                        
                currently_subscribed_users = [(x.user_id) for x in Unread.objects.filter(post=post)]
                
                
                """loop Unread and if not found in userlist, delete from Unread"""
                for ux in currently_subscribed_users:
                    if ux is not None and ux not in userlist:
                        #if ux not in userlist:
                        userx=User.objects.get(id=ux)
                        unreadx = Unread.objects.filter(post=post, user=userx)
                        #unread.user = User.objects.get(id=ux)
                        unreadx.delete()
                        
                """loop userlist and if not in Unread, add to Unread"""
                for u in userlist:
                    if u not in currently_subscribed_users:
                        unread = Unread()
                        unread.user = User.objects.get(id=u)
                        unread.post = post
                        unread.category = category
                        
                        if request.user.id == u:
                            unread.marked_read_on = datetime.now().replace(microsecond=0).isoformat(' ')
                            
                        if is_comment:
                            unread.comment = comment
                            
                        unread.save()
                
                
                        
            success = True
        else:
            """form is not valid"""
            userlist = request.POST.getlist('users')
            success = False
            error = True
            
    else:
        """Not a POST, show the forms!"""
        
        if postid and edit=='1':
            try:
                target_message = Post.objects.get(id=postid)
                form = AddMessageForm(
                    initial={'groupname': custgroup.name,
                            'groupid': groupid,
                            "users": [(x.id) for x in User.objects.filter(groups__name=custgroup.name,userprofile__is_client=0)],
                            "title": target_message.title,
                            "body":target_message.body,
                            'category': target_message.category_id,    
                        },
                )
            except ObjectDoesNotExist:
                pass
        else:
            form = AddMessageForm(
                    initial={'groupname': custgroup.name,
                            'groupid': groupid,
                            "users": [(x.id) for x in User.objects.filter(groups__name=custgroup.name,userprofile__is_client=0)],
                        },
                )
            
        """user list for this group"""
        form.fields['users'].choices = \
            [(x.id, x) for x in User.objects.filter(groups__name=custgroup.name,userprofile__is_client=0)]
        
            
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
            "userlist":userlist,
            "edit":edit,
            "postid":postid,
        }
        
    if success:
        messages.add_message(request, messages.SUCCESS, 'Message was successfuly posted.')
        if is_comment:
            return HttpResponseRedirect("/message/view/%s" % (message.id)) 
        else:
            return HttpResponseRedirect("/message/view/%s" % (post.id)) 
        
    else:
        if error:
            messages.add_message(request, messages.ERROR, 'An error occured. Form data was not valid.')
        
        if edit == '1' and postid:    
            
            return render_to_response("message/post_message.html",
                          data, context_instance=RequestContext(request))
                          
        if postid and edit != '1':
            
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
    * Do not allow "client" to view a message
    * Check if ?error=1
    * Get the message
    * Check if logged in user is member of group
    * Get users subscribed, etc.
    * Get all comments. If has unread items, also get the marked_read_on field
    """
    
    """ do not show a message to a client"""
    if request.user.userprofile.is_client:
        return render_to_response('404.html')
    
    error = None
    
    """
    not really an error but from the ?error=1
    1 => "Please fill out all the required fields."
    """
    error_passed = request.GET.get('error')
    if error_passed == "1":
        messages.add_message(request, messages.ERROR, 'Please fill out all the required fields.')
    
    message = get_object_or_404(Post, id=messageid)
    no_unread = True
    
    custgroup = Group.objects.get(id=message.group_id)
    if custgroup not in request.user.groups.all():
         return render_to_response('404.html')
    else:
        pass 
    
    try:
        unread = Unread.objects.get(user=request.user, post=message)
        if not unread.marked_read_on:
            unread.marked_read_on = datetime.now().replace(microsecond=0).isoformat(' ')
            unread.save()
            
        no_unread = False
    except ObjectDoesNotExist:
        pass
            
    subscribed_users = []
    userchoices = [(x.id, x) for x in User.objects.filter(groups__name=custgroup.name,userprofile__is_client=0)]    
    usersinunread = [(x.user_id) for x in Unread.objects.filter(post=message)]
    for u in usersinunread:
        subscribed_users.append(User.objects.get(id=u))
   
    commentform = AddCommentForm(
            initial={'postid': message.id,
                    'groupname': custgroup.name,
                    'groupid': message.group_id,
                    'category': message.category_id,
                    "users": usersinunread,
                }
        )
        
    commentform.fields['users'].choices = userchoices

    """Get groupmembers and make initial data from Unread model"""
    #groupmembersform = GroupMembersForm(initial={"users": [(x.id) for x in User.objects.filter(groups__name=custgroup.name)],})
    #groupmembersform = GroupMembersForm(initial={"users": [(x.user_id) for x in Unread.objects.filter(post=message)],})
    #groupmembersform = GroupMembersCheckboxForm(initial={"users": usersinunread,})
    groupmembersform = GroupMembersHiddenForm(initial={"users": usersinunread,})
    groupmembersform.fields['users'].choices = userchoices
                
    comments = Comment.objects.filter(post=message).order_by('-comment__published')
    #comments = Unread.objects.filter(post=message)
    all_comments = []
    
    if not no_unread:
        for c in comments:
            all_comments += [(c.id, c.comment.id, c.comment.title, c.comment.user, \
                            c.comment.published, c.comment.body, \
                            #Unread.objects.get(user=c.comment.user, post=c.comment).marked_read_on)]
                            Unread.objects.get(user=request.user, post=c.comment).marked_read_on)]
    else:
        for c in comments:
            all_comments += [(c.id, c.comment.id, c.comment.title, c.comment.user, \
                            c.comment.published, c.comment.body)]
    data = {
            'commentform': commentform,
            'message': message,
            'comments': comments,
            'all_comments': all_comments,
            'groupmembersform': groupmembersform,
            'subscribed_users': subscribed_users,
        }
    return render_to_response('message/view_message.html', data,context_instance=RequestContext(request))
    
@login_required
def by_group(request, groupid):
    """
    Displays messages by group.
    """
    data = {}
    success = False
    
    """ do not show a message to a client"""
    if request.user.userprofile.is_client:
        return render_to_response('404.html')
    
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
    * Do not show to client.
    * Check if logged in user is member of group.
    * Get posts based on current category
    * Iterate posts and get for each post the number of replies, unread, etc.
    ** Per user and per post
    ** Slow :-(
    """
    data = {}
    success = False
    
    """ do not show a message to a client"""
    if request.user.userprofile.is_client:
        return render_to_response('404.html')
    
    """check if user is member of group"""
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
        try:
            marked = p.unread_set.get(post=p.id,user=request.user)

        except ObjectDoesNotExist:
            marked = None
            
        all_posts += [(x.id,\
                        x.marked_read_on, \
                        p, \
                        Unread.objects.filter(marked_read_on__isnull=True, \
                                              user=request.user,comment__post=p.id).count(), \
                        Unread.objects.filter(user=request.user,comment__post=p.id).count(), \
                    ) \
                    #for x in Unread.objects.filter(post__id=p.id).values('post').order_by().annotate(post_count=Count('post'))]
                    #for x in Unread.objects.filter(post=p.id).values(post.id).order_by().annotate(Count('post'))]
                    #for x in p.unread_set.filter(post=p.id).values('unread__post__id').annotate(Count('post')).order_by('post')]
                    #for x in Unread.objects.filter(post=p.id).values(post_id).order_by().annotate(Count('post'))]
                    #for x in p.unread_set.filter(post=p.id).values(unread.id).order_by().annotate(Count('post'))]
                    #for x in p.unread_set.filter(post=p.id)]
                    #for x in p.unread_set.filter(post=p.id).annotate(Count('post__id')).order_by('post')]
                    for x in p.unread_set.filter(post=p.id,user=request.user)]
    
    data = {
            'groupid':custgroup.id,
            'groupname':custgroup.name,
            'categoryid':category.id,
            'categoryname':category.name,
            'posts':all_posts,
            'sql':connection.queries,
    }
    return render_to_response('message/by_category.html', data,context_instance=RequestContext(request))
    
def mark_message_unread(request):
    """
    Mark a single message/post as read.
    """
    success = False
    error = None
    
    """ do not show a message to a client"""
    if request.user.userprofile.is_client:
        return render_to_response('404.html')
    
    if request.method == 'POST' and request.is_ajax():
        form = CommentIdForm(request.POST)
        if form.is_valid():
            commentid = form.cleaned_data['commentid']
            
            post = get_object_or_404(Post, id=commentid,is_comment=1)
            
            unread = get_object_or_404(Unread, post=post,user=request.user)
            
            if not unread.marked_read_on:
                unread.marked_read_on = datetime.now().replace(microsecond=0).isoformat(' ')
                unread.save()
            success = True
            
        else:
            error = 'Form is not valid'
    else:
        pass

    if success:
        if request.is_ajax():
            results = {
                "status":"success",
                "message": "Saved.",
            }
            data = json.dumps(results)
            return HttpResponse(data)
        else:
            return HttpResponse('Request denied. Not AJAX.')
    else:
        if request.is_ajax():
            data = json.dumps({
                "status":"failed", "error":error, "data":request.POST})
            return HttpResponse(data)
        else:
            return HttpResponse('Request denied. Not AJAX.')
        