from django.urls import path
from .views import create_plan, edit_plan, delete_plan, home,plan_detail
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('create/', create_plan, name='create_plan'),
    path('edit/<int:plan_id>/', edit_plan, name='edit_plan'),
    path('delete/<int:plan_id>/', delete_plan, name='delete_plan'),
    path('', home, name='home'),
    path('detail/<int:plan_id>/', plan_detail, name='plan_detail'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

