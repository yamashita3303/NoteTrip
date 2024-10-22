from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    path('cost_home/', views.cost_home, name='cost_home'),
    path('cost_list/', views.cost_list, name='cost_list'),
    path('cost_form/', views.cost_create, name='cost_form'),
]