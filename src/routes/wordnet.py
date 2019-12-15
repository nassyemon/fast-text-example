from flask import Blueprint, jsonify, request
from ..models.WordnetSearch import WordnetSearch
from ..modules.request_helper import get_search_param
from ..modules.response_helper import get_default_repsonse

wordnet = Blueprint('wordnet', __name__)

@wordnet.route("/synonyms", methods=["GET"])
def synonyms(wordnet_search: WordnetSearch):
    response = get_default_repsonse(False)
    search = get_search_param(request)
    if not search:
        return jsonify(response)
    ret = wordnet_search.get_words_in_shared_synsets(search)
    response = {
        **response,
        "success": True,
        "results": ret
    }
    return jsonify(response)