from django.urls import path
from .views import checklist_view, add_item_view

urlpatterns = [
    path('', checklist_view, name='checklist'),
    path('add/', add_item_view, name='add_item'),
]
