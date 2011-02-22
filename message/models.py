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
    slug = models.SlugField(max_length=250, unique=True)
    body = models.TextField()
    published = models.DateTimeField(default=datetime.now)
    category = models.ForeignKey(Category)
    group = models.ForeignKey(Group)
    
    def __unicode__(self):
        return self.title
        
    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify( self.title )
    
        super(Post, self).save(*args, **kwargs)
    