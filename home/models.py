from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Desclogs(models.Model):
    """
    Logs for editting of the description or README files
    """
    groupname = models.CharField(max_length=250)
    file_path = models.CharField(max_length=500)
    user = models.ForeignKey(User)
    old_desc = models.TextField()
    datetime  = models.DateTimeField(auto_now=True, auto_now_add=True,\
                                            verbose_name='Datetime')

class Filecomments(models.Model):
    """
    Comments for a file
    """
    groupname = models.CharField(max_length=250)
    file_path = models.CharField(max_length=500)
    

class Log(models.Model):
    """
    Log user activity when clicking links
    """
    user            = models.ForeignKey(User)
    log_target      = models.CharField(max_length=500, verbose_name='Target')
    log_ip          = models.IPAddressField(verbose_name='IP Address')
    log_datetime    = models.DateTimeField(auto_now=True, auto_now_add=True,\
                                            verbose_name='Datetime')
    log_size        = models.FloatField()
    log_user_agent  = models.CharField(max_length=250)
    log_ref         = models.CharField(max_length=250)
    log_lang        = models.CharField(max_length=250)
    
    def __unicode__(self):
        return "%s: %s from %s at %s" % (self.user,self.log_target,self.log_ip,self.log_datetime)