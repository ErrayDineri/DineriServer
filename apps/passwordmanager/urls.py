# passwordmanager/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add_entry, name='add_entry'),
    path('import/', views.import_csv, name='import_csv'),
    path('', views.vault, name='vault'),
]
