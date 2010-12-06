from django.db import models
from django.contrib.auth.models import User, Group
from registration import signals
from django.db.models.signals import post_save
from django.conf import settings
from django.dispatch import dispatcher
import os,sys

class UserProfile(models.Model):
    user = models.OneToOneField(User, unique=True)
    firstname       = models.CharField(max_length=250, verbose_name="First Name",blank=True, null=True)
    lastname        = models.CharField(max_length=250, verbose_name="Last Name",blank=True, null=True)
    email           = models.EmailField(verbose_name="Email",blank=True, null=True)
    address1        = models.CharField(max_length=250, verbose_name="Address 1",blank=True, null=True)
    address2        = models.CharField(max_length=250, verbose_name="Address 2", blank=True, null=True)
    city            = models.CharField(max_length=250, verbose_name="City",blank=True, null=True)
    province        = models.CharField(max_length=250, verbose_name="Province / State",blank=True, null=True)
    country         = models.CharField(max_length=250, verbose_name="Country",blank=True, null=True)
    zipcode         = models.CharField(max_length=10, verbose_name="Zipcode",blank=True,null=True)

    def __unicode__(self):
        return self.user.username

    def get_absolute_url(self):
        return ('profiles_profile_detail', (), {'username': self.user.username})
    get_absolute_url = models.permalink(get_absolute_url)

"""
def create_user_profile(sender, **kwargs):
    '''Create a user profile for the user after registering'''
    user = kwargs['user']
    request = kwargs['request']
    first_name = request.POST['first_name']
    last_name = request.POST['last_name']
    address2 = request.POST['address2']
    address1 = request.POST['address1']
    city = request.POST['city']
    province = request.POST['province']
    zipcode = request.POST['zipcode']
    profile = UserProfile(user=user,address1=address1, address2=address2,
                          city=city, province=province,
                          zipcode=zipcode)
    user.first_name = first_name
    user.last_name = last_name
    user.save()
    profile.save()
"""

def user_post_save(sender, instance, **kwargs):
    profile, new = UserProfile.objects.get_or_create(user=instance)
    

def create_dir(sender, **kwargs):
    """
    Creates a directory when the admin creates a group. The name of the directory
    is the same as the name of the group that was created.
    """
    instance = kwargs['instance']
    path_to_create = '%s/%s' % (settings.APPLICATION_STORAGE,instance.name)
    if not os.path.isdir(path_to_create):
        os.mkdir(path_to_create)
    
#signals.user_registered.connect(create_user_profile)
models.signals.post_save.connect(user_post_save, sender=User)
post_save.connect(create_dir, sender=Group)
