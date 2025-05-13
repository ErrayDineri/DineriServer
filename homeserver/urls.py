from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.dashboard.urls')),
    path('torrents/', include('apps.torrents.urls')),
    path('search/', include('apps.search.urls')),
]

