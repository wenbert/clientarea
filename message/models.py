from django.db import models
from datetime import datetime
from django.contrib.auth.models import Group, User

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
    categories = models.ManyToManyField(Category)
    
    def __unicode__(self):
        return self.title