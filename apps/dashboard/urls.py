from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='dashboard_home'),
    path('api/system-stats/', views.SystemStatsAPIView.as_view(), name='system_stats_api'),
]
