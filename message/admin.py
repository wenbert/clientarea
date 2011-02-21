from django.db import models
from django.contrib import admin
from message.models import *

class PostAdmin(admin.ModelAdmin):
    filter_horizontal = ('categories',)
    list_display = ('title', 'published')
    prepopulated_fields = {"slug": ("title",)}

admin.site.register(Category)
admin.site.register(Post)