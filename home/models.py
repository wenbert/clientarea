from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Log(models.Model):
    """
    Log user activity when clicking links
    """
    user            = models.ForeignKey(User)
    log_target      = models.CharField(max_length=500, verbose_name='Target')
    log_ip          = models.IPAddressField(verbose_name='IP Address')
    log_datetime    = models.DateTimeField(auto_now=True, auto_now_add=True,\
                                            verbose_name='Datetime')
    