# views.py
from django.http import StreamingHttpResponse, HttpResponse, JsonResponse
from django.views import View
import os
from django.conf import settings
from django.shortcuts import render
from django.views.generic import TemplateView
from .forms import ScrapingForm
from scraper import scrape_all_magnets
from torrent import downloadTorrent, getAllTorrentsSerialized
from .utils import clean_title

class VideoListView(View):
    def get(self, request):
        videos_dir = os.path.join(settings.MEDIA_ROOT, 'videos')
        video_files = []

        if os.path.exists(videos_dir):
            for f in os.listdir(videos_dir):
                if f.endswith('.mkv') or f.endswith('.mp4'):  # You can support more formats here
                    video_files.append(clean_title(f))

        return render(request, 'video_list.html', {'videos': video_files})

class VideoStreamView(View):
    def get(self, request, filename):
        video_path = os.path.join(settings.MEDIA_ROOT, 'videos', filename)

        if not os.path.exists(video_path):
            return HttpResponse(status=404)

        file_size = os.path.getsize(video_path)
        range_header = request.headers.get('Range', '').strip()
        content_type = 'video/mp4'

        if range_header:
            range_match = range_header.replace('bytes=', '').split('-')
            start = int(range_match[0])
            end = int(range_match[1]) if range_match[1] else file_size - 1
            length = end - start + 1

            with open(video_path, 'rb') as f:
                f.seek(start)
                data = f.read(length)

            response = HttpResponse(data, status=206, content_type=content_type)
            response['Content-Range'] = f'bytes {start}-{end}/{file_size}'
            response['Content-Length'] = str(length)
            response['Accept-Ranges'] = 'bytes'
            return response

        # If no Range header: return entire file
        with open(video_path, 'rb') as f:
            data = f.read()
        response = HttpResponse(data, content_type=content_type)
        response['Content-Length'] = str(file_size)
        return response


class HomeView(TemplateView):
    template_name = 'home.html'

class ScraperView(View):
    def get(self, request):
        form = ScrapingForm()
        return render(request, 'scraper.html', {'form': form})

    def post(self, request):
        form = ScrapingForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            magnets = scrape_all_magnets(url)
            for magnet in magnets:
                downloadTorrent(magnet)
            return TorrentStatusView().get(request)
        return render(request, 'scraper.html', {'form': form})

def torrent_status_json(request):
    torrents = getAllTorrentsSerialized()
    return JsonResponse({'torrents': torrents})

class TorrentStatusView(View):
    def get(self, request):
        torrents = getAllTorrentsSerialized()
        return render(request, 'torrents_status.html', {'torrents': torrents})