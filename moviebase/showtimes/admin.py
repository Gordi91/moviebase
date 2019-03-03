from django.contrib import admin

from showtimes import models

admin.site.register(models.Cinema)
admin.site.register(models.Screening)
