from flask import Blueprint, jsonify, request
from ..models.Word2Vec import Word2Vec
from ..models.MeCabTagger import MeCabTagger
from ..models.RelatedWord import RelatedWord
from ..modules.request_helper import get_search_param
from ..modules.response_helper import get_default_repsonse

related = Blueprint('related', __name__)

defaultOptions = {
    "related_word_topn": 10000,
    "negative_boost": 1.0,
    "limit": 50,
}

@related.route("/search", methods=["GET"])
def get_related_word(w2v: Word2Vec, tagger: MeCabTagger):
    related = RelatedWord(w2v, tagger)
    response = get_default_repsonse(False)
    search = get_search_param(request)
    if not search or len(search) < 1:
        return jsonify(response)
    if type(search) == str:
        return jsonify({
            **response,
            "results": [],
        })
    result = related.get_related_words(
        search,
        **defaultOptions,
    )
    response = {
        **response,
        "success": True,
        "results": list(result),
    }
    return jsonify(response)
