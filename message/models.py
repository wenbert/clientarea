from django.db import models
from datetime import datetime
from django.contrib.auth.models import Group, User
from django.template.defaultfilters import slugify

class Category(models.Model):
    """
    class Car(models.Model):
        company_that_makes_it = models.ForeignKey(Manufacturer)
        # ...
    """
    
    name = models.CharField(max_length=120)
    group = models.ForeignKey(Group)
    
    def __unicode__(self):
        return self.name
 
class Post(models.Model):
    title = models.CharField(max_length=250)
    #slug = models.SlugField(max_length=250, unique=True)
    body = models.TextField()
    published = models.DateTimeField(default=datetime.now)
    category = models.ForeignKey(Category)
    group = models.ForeignKey(Group)
    user = models.ForeignKey(User)
    is_comment = models.BooleanField(default=0)
    
    def __unicode__(self):
        return self.title
        
    #def save(self, *args, **kwargs):
    #    if not self.id:
    #        self.slug = slugify( self.title )
    #    super(Post, self).save(*args, **kwargs)

class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comment_parent')
    comment = models.ForeignKey(Post)
    
    def __unicode__(self):
        return comment.title
    
class Unread(models.Model):
    """
    When a user posts a message:
    - Save to Unread model including to all the members of the group
    
    When a user reads a message:
    - Delete the item (user id + post id) from the Unread model 
    """
    user = models.ForeignKey(User)
    post = models.ForeignKey(Post)
    marked_unread_on = models.DateTimeField(null=True, blank=True)
    marked_read_on = models.DateTimeField(null=True, blank=True)