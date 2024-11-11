from django.urls import path
from .views import index, schedule_create, schedule_detail, schedule_edit, schedule_delete

app_name = 'app'

urlpatterns = [
    path('',index, name='index'),
    path('schedule/<int:schedule_id>/', schedule_detail, name='schedule_detail'),
    path('schedule/create/<int:day>/', schedule_create, name='schedule_create'),
    path('schedule/edit/<int:schedule_id>/', schedule_edit, name='schedule_edit'),
    path('schedule/delete/<int:schedule_id>/', schedule_delete, name='schedule_delete'),
    path('schedule/<int:pk>/detail/',schedule_detail,name='schedule_detail'),
]