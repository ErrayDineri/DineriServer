from .search import availableSources

def search_sources(request):
    """
    Add available search sources to all templates
    """
    return {
        'sources': availableSources
    }
