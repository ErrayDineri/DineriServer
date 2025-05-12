import os
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView
from django.urls import reverse

from .forms import ScrapingForm
from .scraper import scrape_all_magnets
from torrenting.torrent import downloadTorrent
from utils import clean_title

class ScraperView(View):
    def get(self, request):
        form = ScrapingForm()
        return render(request, 'scraper.html', {'form': form})

    def post(self, request):
        form = ScrapingForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['link']
            magnets = scrape_all_magnets(url)

            # If no magnets found, add a non-field error & timed refresh back here
            if not magnets:
                form.add_error(None, "No magnet links found on that page.")
                resp = render(request, 'scraper.html', {'form': form})
                # after 2s, reload this same scraper page
                resp['Refresh'] = f'2;url={reverse("scraper-page")}'
                return resp

            # Otherwise enqueue and redirect
            for magnet in magnets:
                downloadTorrent(magnet)
            return redirect('torrent-status')

        # If form invalid (bad URL or domain), re-render with errors:
        return render(request, 'scraper.html', {'form': form})