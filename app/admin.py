from django.contrib import admin
from .models import CustomUser
from .models import Cost, Payment, Budget

admin.site.register(CustomUser)
admin.site.register(Cost)
admin.site.register(Payment)
admin.site.register(Budget)
