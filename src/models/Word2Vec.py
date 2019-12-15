import re
import math
from gensim.models import KeyedVectors
from typing import Callable, Iterable, List, Set, Dict, Tuple, Optional

model = None

class Word2Vec:
    DEBUG = True
    EXPECTED_ENTITY_CONTENT_RATE = 0.7
    model_filepath = None
    model = None

    def __init__(self, model_filepath, binary = True):
        global model
        self.model_filepath = model_filepath
        if self.DEBUG and model is not None:
            print("reusing loaded model.")
            self.model = model
            return
        self.model = KeyedVectors.load_word2vec_format(model_filepath, binary=binary)
        model = self.model

    def reload(self, model_filepath=None, binary = True):
        global model
        if model_filepath is not None:
            self.model_filepath = model_filepath
        self.model = KeyedVectors.load_word2vec_format(model_filepath, binary=binary)
        model = self.model

    def most_similar(
        self,
        positive: str or List[str],
        topn: int=30,
    ) -> List[Tuple[str, float]]:
        try:
            similars = self.model.wv.most_similar(
                positive=positive,
                topn=math.ceil(topn/(1-self.EXPECTED_ENTITY_CONTENT_RATE))
            )
        except KeyError:
            return [(positive, 1.0)] if type(positive) == str else [(s, 1.0) for s in positive]
        # remove entities.
        return [*filter(lambda x: not x[0].startswith("["), similars)][0:topn]

    def similarity(
        self,
        w1,
        w2,
    ):
        score = 0.0
        try:
            score = self.model.wv.similarity(w1, w2)
        except  KeyError:
            score = 0.0
        return score