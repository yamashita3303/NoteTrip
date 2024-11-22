from django.urls import path
from . import views
from .admin import admin_site

urlpatterns = [
    path('admin/', admin_site.urls),  # カスタム管理者サイトのURL設定
    path('', views.loginView, name='login'),
    path('admin_login/', views.admin_loginView, name='admin_login'),
    path('signup/', views.signupView, name='signup'),
    path('logout/', views.logoutView, name='logout'),
    path('home/', views.homeView, name='home'),
    path('dashboard/', views.dashboardView, name='dashboard'),
    path('password_reset/', views.password_resetView, name='password_reset'),
    path('password_reset_confirm/<uidb64>/<token>/', views.password_reset_confirmView, name='password_reset_confirm'),
    path('password_reset/done/', views.password_reset_doneView, name='password_reset_done'),
    path('application/', views.applicationView, name='application'),
    path('application_complete/', views.application_completeView, name='application_complete'),
    path('application/approve/<int:application_id>/', views.approve_application, name='approve_application'),
    path('application/reject/<int:application_id>/', views.reject_application, name='reject_application'),
    path('application/delete/<int:application_id>/', views.delete_application, name='delete_application'),
    path('application/form/<int:applicant_id>/', views.add_spot, name='add_spot'),
    path('application/form/confirmation/<int:applicant_id>', views.add_spot_confirmation, name='add_spot_confirmation'),
    path('application/form/success/<int:applicant_id>', views.add_spot_success, name='add_spot_success'),
    path('spot/delete/<int:spot_id>/', views.delete_spot, name='delete_spot'),
]
