from django.urls import path
from . import views

urlpatterns = [
    path('', views.loginView, name='login'),
    path('signup/', views.signupView, name='signup'),
    path('password_reset/', views.password_resetView, name='password_reset'),
    path('logout/', views.logoutView, name='logout'),
    path('home/', views.homeView, name='home'),
    path('password_reset/', views.password_resetView, name='password_reset'),
    path('password_reset_confirm/<uidb64>/<token>/', views.password_reset_confirmView, name='password_reset_confirm'),
    path('password_reset/done/', views.password_reset_doneView, name='password_reset_done'),
    path('cost_home/<str:payer_name>/', views.cost_home, name='cost_home'),  # URLに支払者名を追加
    path('cost_list/', views.cost_list, name='cost_list'),
    path('cost_form/', views.cost_create, name='cost_form'),
    path('cost_budget/', views.cost_budget, name='cost_budget'),
]