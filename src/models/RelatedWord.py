import re
import math
import statistics
from .Word2Vec import Word2Vec
from .MeCabTagger import MeCabTagger
from typing import Callable, Iterable, List, Set, Dict, Tuple, Optional

INV_SQRT2 = 1/math.sqrt(2)
EPSILON = math.pow(10, -10)

# erf function with negative boost    
def erf(x, negative_boost:float=1.0):
    if x < 0:
        return negative_boost*math.erf(INV_SQRT2*x)
    return math.erf(INV_SQRT2*x)

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
        related_word_topn: int = 100,
        limit: int = 50,
        negative_boost:float = 1.0,
    ) -> List[Tuple[str, float, float, Dict[str, float]]]:
        combi = [
        (word, score, [score - self.w2v.similarity(word, search) for search in searches])
        for (word, score) in self.w2v.most_similar(
            positive=searches,
            topn=related_word_topn,
            )
        ]
        dists = [
            [*map(lambda x:x[2][i], combi)]
            for i, search in enumerate(searches)
        ]
        avg_dists = [statistics.mean(dist) + EPSILON for dist in dists]
        sigma_dists = [statistics.stdev(dist) + EPSILON for dist in dists]
        normalized = [
            (
                word,
                score, 
                [(search_scores[i]-avg_dists[i])/sigma_dists[i] for i, s in enumerate(search_scores)],
                search_scores
            )
            for (word, score, search_scores) in combi
        ]
        coocs = [*filter(None, [
            # None if len([*filter(lambda x: x > score, search_scores)]) > 0 else
            (
                word,
                float(score),
                float(sum(map(lambda x: erf(x, negative_boost), normalized))),
                dict([(search, (score+search_scores[i], normalized[i])) for i, search in enumerate(searches)])
            )
            for (word, score, normalized, search_scores) in normalized]
        )]
        sorted_result =  [*sorted(coocs, key=lambda x:-x[2])]
        if limit > 0:
            return sorted_result[0:limit]
        return sorted_result
