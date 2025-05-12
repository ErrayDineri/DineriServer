from django.urls import path
from .views import (
    ScraperView)

urlpatterns = [
    path('scraper/', ScraperView.as_view(), name='scraper-page'),
]
