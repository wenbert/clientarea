from django.contrib.auth.models import User, Group
from django.db import models, signals
from registration import signals
from django.db.models.signals import post_save
from django.conf import settings
from django.dispatch import dispatcher
import os,sys

class UserProfile(models.Model):
    user = models.OneToOneField(User, unique=True)
    is_client = models.BooleanField(default=1, help_text="If a user is marked as a client, the user will not have access to Messages, etc.")
    #firstname       = models.CharField(max_length=250, verbose_name="First Name",blank=True, null=True)
    #lastname        = models.CharField(max_length=250, verbose_name="Last Name",blank=True, null=True)
    #email           = models.EmailField(verbose_name="Email",blank=True, null=True)
    #address1        = models.CharField(max_length=250, verbose_name="Address 1",blank=True, null=True)
    #address2        = models.CharField(max_length=250, verbose_name="Address 2", blank=True, null=True)
    #city            = models.CharField(max_length=250, verbose_name="City",blank=True, null=True)
    #province        = models.CharField(max_length=250, verbose_name="Province / State",blank=True, null=True)
    #country         = models.CharField(max_length=250, verbose_name="Country",blank=True, null=True)
    #zipcode         = models.CharField(max_length=10, verbose_name="Zipcode",blank=True,null=True)

    def __unicode__(self):
        return self.user.username

    def get_absolute_url(self):
        return ('profiles_profile_detail', (), {'username': self.user.username})
    get_absolute_url = models.permalink(get_absolute_url)
    
class UserLogin(models.Model):
    """Represent users' logins, one per record"""        
    user        = models.ForeignKey(User)
    timestamp   = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return "%s at %s" % (self.user,self.timestamp)

def user_post_save(sender, instance, **kwargs):
    """
    Creates a default profile when adding a user in the Admin panel.
    """
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


def user_login_save(sender, instance, **kwargs):
    if instance.last_login:
        old = instance.__class__.objects.get(pk=instance.pk)
        if instance.last_login != old.last_login:
            instance.userlogin_set.create(timestamp=instance.last_login)
            
#signals.user_registered.connect(create_user_profile)
models.signals.post_save.connect(user_post_save, sender=User)
post_save.connect(create_dir, sender=Group)
models.signals.post_save.connect(user_login_save,  sender=User)
