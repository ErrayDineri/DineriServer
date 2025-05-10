from django.shortcuts import render
from torrenting.torrent import (
    getAllTorrentsSerialized,
    pauseTorrent,
    resumeTorrent,
    forceStartTorrent,
    deleteTorrent
)
from django.http import HttpResponse, JsonResponse
from django.views import View
# Create your views here.
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
