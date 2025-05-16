from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
import json

from .services.search import searchAll, searchBySource, availableSources
from apps.torrents.services.utils import downloadTorrent


def search_view(request):
    # Get query parameter if it exists (for navbar search)
    query = request.GET.get('query', '').strip()
    filter_source = request.GET.get('filterSource', 'all')
    
    # Pass available sources into template context
    sources = availableSources  # e.g. ['SiteA', 'SiteB', ...]
    return render(request, 'search/search.html', {
        'sources': sources, 
        'initial_query': query,
        'filter_source': filter_source
    })

@require_GET
def search_api(request):
    query         = request.GET.get('query', '').strip()
    source_filter = request.GET.get('filterSource', 'all')

    if not query:
        return JsonResponse({'results': []})

    # Dispatch based on pre-selected source
    if source_filter != 'all' and source_filter in availableSources:
        results = searchBySource(query, source_filter)
    else:
        results = searchAll(query)

    payload = []
    for r in results:
        payload.append({
            'title'   : r['title'],
            'link'    : r['link'],
            'seeders' : r['seeders'],
            'leechers': r['leechers'],
            'source'  : r['source'],
            'size'    : r['size'],
        })
    return JsonResponse({'results': payload})

@csrf_exempt
@require_POST
def download_selected(request):
    data = json.loads(request.body)
    for item in data.get('torrents', []):
        downloadTorrent(item['link'])
    return JsonResponse({'status': 'ok'})
