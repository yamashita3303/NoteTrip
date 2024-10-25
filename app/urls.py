from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    # path('cost_home/', views.cost_home, name='cost_home'),
    path('cost_home/<str:payer_name>/', views.cost_home, name='cost_home'),  # URLに支払者名を追加
    path('cost_list/', views.cost_list, name='cost_list'),
    path('cost_form/', views.cost_create, name='cost_form'),
    path('cost_budget/', views.cost_budget, name='cost_budget'),
]