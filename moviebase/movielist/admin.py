from django.contrib import admin
from movielist import models

admin.site.register(models.Movie)
admin.site.register(models.Person)