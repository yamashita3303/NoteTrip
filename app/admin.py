from django.contrib import admin
from .models import CustomUser
from .models import Plan
from .models import Checklist

admin.site.register(CustomUser)
admin.site.register(Plan)
admin.site.register(Checklist)
