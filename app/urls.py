from django.urls import path
from . import views
from .views import create_plan, edit_plan, delete_plan, home, plan_detail, get_events, member, share, approve_view, checklist_view, add_item_view, schedule, schedule_create, schedule_detail, schedule_edit, schedule_delete
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
    path('detail/<int:plan_id>/member/', member, name='member'),
    path('detail/<int:plan_id>/member/share/', share, name='share'),
    path('approve/<int:plan_id>/<str:uid>/<str:token>/', approve_view, name='approve'),
    path('schedule/',schedule, name='schedule'),
    path('schedule/<int:schedule_id>/', schedule_detail, name='schedule_detail'),
    path('schedule/create/<int:day>/', schedule_create, name='schedule_create'),
    path('schedule/edit/<int:schedule_id>/', schedule_edit, name='schedule_edit'),
    path('schedule/delete/<int:schedule_id>/', schedule_delete, name='schedule_delete'),
    path('schedule/<int:pk>/detail/',schedule_detail,name='schedule_detail'),
    path('checklist/', checklist_view, name='checklist'),
    path('checklist/add/', add_item_view, name='add_item'),
    path('get-events/', get_events, name='get-events'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
