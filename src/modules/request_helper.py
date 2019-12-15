def get_search_param(request, search_key="q"):
    query_search = request.args.get(search_key)
    if not query_search or len(query_search) < 1:
        return None
    searches = [*filter(lambda x: len(x) > 0, query_search.split(" "))]
    return searches[0] if len(searches) < 2 else searches
    