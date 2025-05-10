# streaming/views.py
import os
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView

from .forms import ScrapingForm
from scraper import scrape_all_magnets
from torrent import (
    downloadTorrent,
    getAllTorrentsSerialized,
    pauseTorrent,
    resumeTorrent,
    forceStartTorrent,
    deleteTorrent
)
from .utils import clean_title
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


class VideoListView(View):
    def get(self, request):
        videos_dir = os.path.join(settings.MEDIA_ROOT, 'videos')
        video_files = []
        if os.path.exists(videos_dir):
            for f in os.listdir(videos_dir):
                if f.lower().endswith(('.mkv', '.mp4')):
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
            start_str, end_str = range_header.replace('bytes=', '').split('-')
            start = int(start_str)
            end = int(end_str) if end_str else file_size - 1
            length = end - start + 1
            with open(video_path, 'rb') as f:
                f.seek(start)
                data = f.read(length)
            response = HttpResponse(data, status=206, content_type=content_type)
            response['Content-Range'] = f'bytes {start}-{end}/{file_size}'
            response['Content-Length'] = str(length)
            response['Accept-Ranges'] = 'bytes'
            return response

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

class TorrentStatusJSON(View):
    PAGE_SIZE = 20

    def get(self, request):
        page = int(request.GET.get('page', 1))
        all_torrents = getAllTorrentsSerialized()
        start = (page - 1) * self.PAGE_SIZE
        end = start + self.PAGE_SIZE
        chunk = all_torrents[start:end]
        return JsonResponse({'torrents': chunk})

class TorrentStatusView(View):
    def get(self, request):
        return render(request, 'torrents_status.html')

# Action endpoints
class PauseTorrent(View):
    def post(self, request):
        h = request.POST.get('hash')
        if not h:
            return JsonResponse({'error': 'Missing hash'}, status=400)
        pauseTorrent(h)
        return JsonResponse({'status': 'paused', 'hash': h})

class ResumeTorrent(View):
    def post(self, request):
        h = request.POST.get('hash')
        if not h:
            return JsonResponse({'error': 'Missing hash'}, status=400)
        resumeTorrent(h)
        return JsonResponse({'status': 'resumed', 'hash': h})

class ForceStartTorrent(View):
    def post(self, request):
        h = request.POST.get('hash')
        if not h:
            return JsonResponse({'error': 'Missing hash'}, status=400)
        forceStartTorrent(h)
        return JsonResponse({'status': 'forced', 'hash': h})

class DeleteTorrent(View):
    def post(self, request):
        h = request.POST.get('hash')
        delete_files = request.POST.get('delete_files') == 'true'
        if not h:
            return JsonResponse({'error': 'Missing hash'}, status=400)
        deleteTorrent(h, delete_files)
        return JsonResponse({'status': 'deleted', 'hash': h, 'deleted_files': delete_files})
