from django.urls import path
from . import views
from .admin import admin_site
from .views import create_plan, edit_plan, delete_plan, home, plan_detail, get_events, member, share, approve_view, checklist_view, add_item_view, schedule, schedule_create, schedule_detail, schedule_edit, schedule_delete
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',views.top, name='top'),
    path('admin/', admin_site.urls),  # カスタム管理者サイトのURL設定
    path('admin_login/', views.admin_loginView, name='admin_login'),
    path('login', views.loginView, name='login'),
    path('signup/', views.signupView, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', home, name='home'),
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
    path('create/', create_plan, name='create_plan'),
    path('edit/<int:plan_id>/', edit_plan, name='edit_plan'),
    path('delete/<int:plan_id>/', delete_plan, name='delete_plan'),
    path('detail/<int:plan_id>/', plan_detail, name='plan_detail'),
    # path('detail/<int:plan_id>/member/', member, name='member'),
    path('detail/<int:plan_id>/share/', share, name='share'),
    path('approve/<int:plan_id>/<str:uid>/<str:token>/', approve_view, name='approve'),
    path('schedule/<int:plan_id>/',schedule, name='schedule'),
    path('schedule/<int:plan_id>/<int:schedule_id>/', schedule_detail, name='schedule_detail'),
    path('schedule/create/<int:plan_id>/<int:day>/', schedule_create, name='schedule_create'),
    path('schedule/edit/<int:plan_id>/<int:schedule_id>/', schedule_edit, name='schedule_edit'),
    path('schedule/delete/<int:plan_id>/<int:schedule_id>/', schedule_delete, name='schedule_delete'),
    path('checklist/<int:plan_id>/', checklist_view, name='checklist'),
    path('checklist/<int:plan_id>/add/', add_item_view, name='add_item'),# チェックリスト追加用URL
    path('checklist/<int:plan_id>/delete/<int:item_id>/', views.delete_item_view, name='delete_item'),  # チェックリスト削除用URL
    path('get-events/', get_events, name='get-events'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
