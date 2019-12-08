from flask import Flask, render_template, jsonify, request
import os
from .models.WordnetSearch import WordnetSearch

# initialize our Flask application and pre-trained model
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
wordnet = None
wndb_filepath = os.path.join(os.path.dirname(__file__), '../data/wnjpn.db')

def load_model():
    global wordnet
    wordnet = WordnetSearch(wndb_filepath)

@app.route("/__debug/load", methods=["GET"])
def debug_load():
    load_model()
    return jsonify({
        "success": True,
        "Content-Type": "application/json"
    })


@app.route("/wordnet/synonyms", methods=["GET"])
def predict():
    response = {
        "success": False,
        "Content-Type": "application/json"
    }
    query_search = request.args.get("search")
    if not query_search or len(query_search) < 1:
        return jsonify(response)
    searches = [*filter(lambda x: len(x) > 0, query_search.split(" "))]
    search = searches[0] if len(searches) < 2 else searches
    ret = wordnet.get_words_in_shared_synsets(search)
    response = {
        **response,
        "success": True,
        "results": ret
    }
    return jsonify(response)


if __name__ == "__main__":
    load_model()
    print(" * Flask starting server...")
    app.run()
