from django.shortcuts import render
from .services.utils import (
    getAllTorrentsSerialized,
    pauseTorrent,
    resumeTorrent,
    forceStartTorrent,
    deleteTorrent
)
from django.http import  JsonResponse
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
        return render(request, 'torrents/torrent.html')

# Action endpoints
class PauseTorrent(View):
    def post(self, request):
        try:
            h = request.POST.get('hash')
            if not h:
                return JsonResponse({'error': 'Missing hash parameter'}, status=400)
            
            pauseTorrent(h)
            return JsonResponse({'status': 'paused', 'hash': h})
        except Exception as e:
            import traceback
            return JsonResponse({
                'error': str(e),
                'traceback': traceback.format_exc()
            }, status=500)

class ResumeTorrent(View):
    def post(self, request):
        try:
            h = request.POST.get('hash')
            if not h:
                return JsonResponse({'error': 'Missing hash parameter'}, status=400)
            
            resumeTorrent(h)
            return JsonResponse({'status': 'resumed', 'hash': h})
        except Exception as e:
            import traceback
            return JsonResponse({
                'error': str(e),
                'traceback': traceback.format_exc()
            }, status=500)

class ForceStartTorrent(View):
    def post(self, request):
        try:
            h = request.POST.get('hash')
            if not h:
                return JsonResponse({'error': 'Missing hash parameter'}, status=400)
            
            forceStartTorrent(h)
            return JsonResponse({'status': 'forced', 'hash': h})
        except Exception as e:
            import traceback
            return JsonResponse({
                'error': str(e),
                'traceback': traceback.format_exc()
            }, status=500)

class DeleteTorrent(View):
    def post(self, request):
        try:
            h = request.POST.get('hash')
            if not h:
                return JsonResponse({'error': 'Missing hash parameter'}, status=400)
            
            delete_files = request.POST.get('delete_files') == 'true'
            deleteTorrent(h, delete_files)

            # Tell the client to refresh the page
            return JsonResponse({
                'status': 'deleted',
                'hash': h,
                'deleted_files': delete_files,
                'refresh': True
            })
        except Exception as e:
            import traceback
            return JsonResponse({
                'error': str(e),
                'traceback': traceback.format_exc()
            }, status=500)
