from django.contrib import admin
from .models import CustomUser
from .models import Plan
from .models import Schedule
from .models import Checklist

admin.site.register(CustomUser)
admin.site.register(Plan)
admin.site.register(Schedule)
admin.site.register(Checklist)
