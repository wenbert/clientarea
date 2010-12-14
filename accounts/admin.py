from django.db import models
from django.contrib import admin
from accounts.models import *

admin.site.register(UserProfile)
admin.site.register(UserLogin)

