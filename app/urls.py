from django.urls import path
from . import views
from .views import create_plan, edit_plan, delete_plan, home, plan_detail, get_events
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.loginView, name='login'),
    path('signup/', views.signupView, name='signup'),
    path('password_reset/', views.password_resetView, name='password_reset'),
    path('logout/', views.logoutView, name='logout'),
    path('home/', home, name='home'),
    path('password_reset/', views.password_resetView, name='password_reset'),
    path('password_reset_confirm/<uidb64>/<token>/', views.password_reset_confirmView, name='password_reset_confirm'),
    path('password_reset/done/', views.password_reset_doneView, name='password_reset_done'),
    path('create/', create_plan, name='create_plan'),
    path('edit/<int:plan_id>/', edit_plan, name='edit_plan'),
    path('delete/<int:plan_id>/', delete_plan, name='delete_plan'),
    path('detail/<int:plan_id>/', plan_detail, name='plan_detail'),
    path('get-events/', get_events, name='get-events'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

