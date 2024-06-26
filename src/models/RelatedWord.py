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
        remove_entity: bool = True
    ) -> List[Tuple[str, float, float, Dict[str, float]]]:
        combi = [
        (word, similarity, [similarity - self.w2v.similarity(word, search) for search in searches])
        for (word, similarity) in self.w2v.most_similar(
            positive=searches,
            topn=related_word_topn,
            remove_entity=remove_entity
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
                similarity, 
                [(search_scores[i]-avg_dists[i])/sigma_dists[i] for i, s in enumerate(search_scores)],
                search_scores
            )
            for (word, similarity, search_scores) in combi
        ]
        coocs = [*filter(None, [
            # None if len([*filter(lambda x: x > score, search_scores)]) > 0 else
            (
                word,
                float(similarity),
                float(sum(map(lambda x: erf(x, negative_boost), norm_distance))),
                dict([(search, (similarity-search_scores[i], norm_distance[i])) for i, search in enumerate(searches)])
            )
            for (word, similarity, norm_distance, search_scores) in normalized]
        )]
        sorted_result =  [*sorted(coocs, key=lambda x:-x[2])]
        if limit > 0:
            return [*map(self.to_dict_result, sorted_result[0:limit])]
        return [*map(self.to_dict_result, sorted_result)]

    @staticmethod
    def to_dict_result(record):
        (word, similarity, score, dict_scores) = record
        return {
            "word": word,
            "score": score,
            "similarity": similarity,
            "base_scores": dict_scores
        }