from django.contrib import admin
from .models import CustomUser
from .models import Plan

admin.site.register(CustomUser)
admin.site.register(Plan)
