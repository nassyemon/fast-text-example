import re
import math
import numpy as np
from gensim.models import KeyedVectors
from typing import Callable, Iterable, List, Set, Dict, Tuple, Optional

model = None

RE_ENTITY_STEM = re.compile(r'^\[?#?([^_\]]+)([^\]]*)?\]?$')

def aggregate(similars: Iterable[Tuple[str, float]]):
    result = {}
    for word, similarity in similars:
        match = RE_ENTITY_STEM.match(word)
        if not match:
            continue
        stem = match[1]
        if stem in result:
            result[stem] += [similarity]
        else:
            result[stem] = [similarity]
    return list(map(lambda x: (x[0], np.mean(x[1])), result.items()))


class Word2Vec:
    DEBUG = True
    EXPECTED_ENTITY_CONTENT_RATE = 0.9
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
        remove_entity: bool=False,
        aggregate_entity: bool=False,
    ) -> List[Tuple[str, float]]:
        try:
            positives_with_entity = self.with_entities_if_exists(positive)
            if len(positives_with_entity) < 1:
                return [(positive, 1.0)] if type(positive) == str else [(s, 1.0) for s in positive]
            similars = self.model.most_similar(
                positive=positives_with_entity,
                topn=math.ceil(topn/(1-self.EXPECTED_ENTITY_CONTENT_RATE))
            )
        except KeyError:
            return [(positive, 1.0)] if type(positive) == str else [(s, 1.0) for s in positive]
        # remove entities.
        if remove_entity:
            return list(filter(lambda x: not x[0].startswith('['), similars))[0:topn]
        if aggregate_entity:
            return aggregate(similars)[0:topn]
        return similars[0:topn]

    def with_entity(self, w: str):
        we = f"[{w}]"
        has_entity =  f"[{w}]" in self.model.vocab
        has_word = w in self.model.vocab
        if has_entity and has_word:
            return [w, we]
        if has_entity:
            return [we, we]
        if has_word:
            return [w, w]
        return []

    def with_entities_if_exists(
        self,
        ws: str or List[str],
    ):
        if type(ws) == str:
            return self.with_entity(ws)
        return sum([self.with_entity(w) for w in ws], [])
    
    def similarity(self, w1, w2):
        if w1 not in self.model.vocab:
            return 0.0
        if w2 not in self.model.vocab:
            return 0.0
        return self.model.similarity(w1, w2)
    # def similarity(
    #     self,
    #     w1,
    #     w2,
    # ):
    #     # w1s =  self.to_entities_if_exists(w1)
    #     # w2s =  self.to_entities_if_exists(w2)
    #     # try:
    #     #     return self.model.similarity(w1s, w2s)
    #     # except KeyError:
    #     #     return 0.0
    #     vocab = self.model.vocab
    #     w1e = f"[{w1}]"
    #     w2e = f"[{w2}]"
    #     patterns = [
    #         self.model.similarity(w1, w2) if w1 in vocab and w2 in vocab else None,
    #         self.model.similarity(w1e, w2) if w1e in vocab and w2 in vocab else None,
    #         self.model.similarity(w1, w2e) if w1 in vocab and w2e in vocab else None,
    #         self.model.similarity(w1e, w2e) if w1e in vocab and w2e in vocab else None,
    #     ]
    #     filtered = [*filter(lambda x: x is not None, patterns)]
    #     if len(filtered) < 1:
    #         return 0.0
    #     return np.mean(filtered)
