from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.dashboard.urls')),
    path('torrents/', include('apps.torrents.urls')),
    path('search/', include('apps.search.urls')),
    path('mediahub/', include('apps.mediahub.urls')),
    path('passwords/', include('apps.passwordmanager.urls')),
    path('accounts/', include('apps.accounts.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

