from flask import Flask, render_template, jsonify, request
from injector import Module, Injector, inject, singleton
import os
from flask_injector import FlaskInjector
from .models.WordnetSearch import WordnetSearch
from .models.MeCabTagger import MeCabTagger
from .models.Word2Vec import Word2Vec
from .modules.request_helper import get_search_param
from .modules.response_helper import get_default_repsonse
from .routes.wordnet import wordnet
from .routes.w2v import w2v
from .routes.synonyms import synonyms
from .routes.related import related

# initialize our Flask application and pre-trained model
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
wndb_filepath = os.path.join(os.path.dirname(__file__), '../data/wnjpn.db')
w2v_model_filepath = os.path.join(os.path.dirname(__file__), '../data/entity_vector.model.bin')

wordnet_search = None
word2vec = None
tagger = None

def bind_wordnet(binder):
    global wordnet_search
    if wordnet_search is None:
        print("loading word2vec model.")
        wordnet_search = WordnetSearch(wndb_filepath)
    binder.bind(
        WordnetSearch,
        to=wordnet_search,
        scope=singleton,
    )
    print("loaded wordnet model.")


def bind_word2vec(binder):
    global word2vec
    if word2vec is None:
        print("loading word2vec model.")
        word2vec = Word2Vec(w2v_model_filepath, binary=True)
    binder.bind(
        Word2Vec,
        to=word2vec,
        scope=singleton,
    )
    print("loaded word2vec model.")



def bind_mecab(binder):
    global tagger
    if tagger is None:
        print("loading mecab model.")
        tagger = MeCabTagger()
    binder.bind(
        MeCabTagger,
        to=tagger,
        scope=singleton,
    )
    print("loaded mecab model.")


@app.route("/__reload", methods=["GET"])
def debug_load(
    wordnet_search: WordnetSearch,
    w2v: Word2Vec,
):
    wordnet_search.reload()
    w2v.reload()
    return jsonify(get_default_repsonse(True))


print(" * Flask starting server...")

app.register_blueprint(wordnet, url_prefix='/wordnet')
app.register_blueprint(w2v, url_prefix='/w2v')
app.register_blueprint(synonyms, url_prefix='/synonyms')
app.register_blueprint(related, url_prefix='/related')
FlaskInjector(app=app, modules=[
    bind_mecab,
    bind_wordnet,
    bind_word2vec,
])

if __name__ == '__main__':
    app.run(debug=True)
