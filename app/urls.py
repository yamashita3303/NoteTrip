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
    path('application/', views.applicationView, name='application'),
    path('application_complete/', views.application_completeView, name='application_complete'),
    path('approve/<int:application_id>/', views.approve_applicationView, name='approve_application'),
    path('reject/<int:application_id>/', views.reject_applicationView, name='reject_application'),
    path('application_cancel/<int:application_id>/', views.application_cancelView, name='application_cancel'),
    path('application/form/', views.add_spot, name='add_spot'),
    path('application/form/confirmation/', views.add_spot_confirmation, name='add_spot_confirmation'),
    path('application/form/success/', views.add_spot_success, name='add_spot_success'),
]
