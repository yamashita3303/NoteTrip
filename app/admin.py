from django.contrib import admin
from .models import CustomUser, Application, Spot

admin.site.register(CustomUser)
admin.site.register(Application)
admin.site.register(Spot)
