from flask import Blueprint, jsonify, request
from ..models.Word2Vec import Word2Vec
from ..modules.request_helper import get_search_param
from ..modules.response_helper import get_default_repsonse

w2v = Blueprint('w2v', __name__)

@w2v.route("/most_similar", methods=["GET"])
def most_similar(w2v: Word2Vec):
    response = get_default_repsonse(False)
    search = get_search_param(request)
    if not search:
        return jsonify(response)
    ret = w2v.most_similar(search, topn=20)
    response = {
        **response,
        "success": True,
        "results": ret
    }
    return jsonify(response)