import re
import math
from .Word2Vec import Word2Vec
from .MeCabTagger import MeCabTagger
from typing import Callable, Iterable, List, Set, Dict, Tuple, Optional

class RelatedWord:
    w2v: Word2Vec = None
    tagger: MeCabTagger = None

    def __init__(
        self,
        w2v: Word2Vec,
        tagger: MeCabTagger
    ):
        self.w2v = w2v
        self.tagger = tagger

    def get_related_words(
        self, searches: Iterable[str],
        limit: int = 50,
    ):
        combi = [
        (word, score, [self.w2v.similarity(word, search) for search in searches])
        for (word, score) in self.w2v.most_similar(
            positive=searches,
            topn=100
            )
        ]
        coocs = [*filter(None, [
            None if len([*filter(lambda x: x > score, search_scores)]) > 0 else
            (
                word,
                score,
                min([*map(lambda x:score/x, search_scores)]),
                search_scores,
            )
            for (word, score, search_scores) in combi]
        )]
        sorted_result =  [*sorted(coocs, key=lambda x:-x[2])]
        if limit > 0:
            return sorted_result[0:limit]
        return sorted_result