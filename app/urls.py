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

]
