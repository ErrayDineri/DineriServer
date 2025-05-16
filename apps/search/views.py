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
    filter_sources = request.GET.getlist('filterSource', ['all'])
    
    # Pass available sources into template context
    sources = availableSources  # e.g. ['SiteA', 'SiteB', ...]
    return render(request, 'search/search.html', {
        'sources': sources, 
        'initial_query': query,
        'filter_sources': filter_sources
    })

@require_GET
def search_api(request):
    query = request.GET.get('query', '').strip()
    sources = request.GET.getlist('filterSource', ['all'])

    if not query:
        return JsonResponse({'results': []})

    # Dispatch based on selected sources
    if 'all' not in sources:
        # Filter to only valid sources in case of invalid input
        valid_sources = [src for src in sources if src in availableSources]
        if valid_sources:
            results = searchBySource(query, valid_sources)
        else:
            # Fallback to all sources if none of the selected ones are valid
            results = searchAll(query)
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
