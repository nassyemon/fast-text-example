from flask import Blueprint, jsonify, request
from ..models.WordnetSearch import WordnetSearch
from ..models.Word2Vec import Word2Vec
from ..models.MeCabTagger import MeCabTagger
from ..models.Synonyms import Synonyms
from ..modules.request_helper import get_search_param
from ..modules.response_helper import get_default_repsonse

synonyms = Blueprint('synonyms', __name__)

@synonyms.route("/mixed", methods=["GET"])
def get_mixed_synonyms(w2v: Word2Vec, wordnet_search: WordnetSearch, tagger: MeCabTagger):
    synonyms = Synonyms(w2v, wordnet_search, tagger)
    response = get_default_repsonse(False)
    search = get_search_param(request)
    use_neigbhor_synonym=True
    append_neigbhors = True
    neigbhor_topn=20
    neigbhor_boost=1.0
    synonym_boost=1.0
    neigbhor_synonym_boost=0.1
    if not search or len(search) < 1:
        return jsonify(response)
    mixed = synonyms.get_mixed_synonyms(
        search,
        use_neigbhor_synonym=use_neigbhor_synonym,
        append_neigbhors=append_neigbhors,
        neigbhor_topn=neigbhor_topn,
        neigbhor_boost=neigbhor_boost,
        synonym_boost=synonym_boost,
        neigbhor_synonym_boost=neigbhor_synonym_boost,
    )
    sorted_result = sorted(mixed, key=lambda x:x['s'], reverse=True)
    response = {
        **response,
        "success": True,
        "results": list(sorted_result),
    }
    return jsonify(response)

@synonyms.route("/search", methods=["GET"])
def search_agregated_synonyms(w2v: Word2Vec, wordnet_search: WordnetSearch, tagger: MeCabTagger):
    synonyms = Synonyms(w2v, wordnet_search, tagger)
    response = get_default_repsonse(False)
    search = get_search_param(request)
    use_neigbhor_synonym=True
    append_neigbhors = True
    neigbhor_topn=20
    neigbhor_boost=1.0
    synonym_boost=1.0
    neigbhor_synonym_boost=0.1
    top_percentile = 0.95
    if not search or len(search) < 1:
        return jsonify(response)
    mixed = synonyms.get_mixed_synonyms(
        search,
        use_neigbhor_synonym=use_neigbhor_synonym,
        append_neigbhors=append_neigbhors,
        neigbhor_topn=neigbhor_topn,
        neigbhor_boost=neigbhor_boost,
        synonym_boost=synonym_boost,
        neigbhor_synonym_boost=neigbhor_synonym_boost,
    )
    tops = synonyms.get_top_n_percentile(mixed, top_percentile)
    result = synonyms.aggregate_by_yomi(search,tops)
    response = {
        **response,
        "success": True,
        "results": result
    }
    return jsonify(response)