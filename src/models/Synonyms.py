import re
import Levenshtein
import math
import numpy as np
from .Word2Vec import Word2Vec
from .WordnetSearch import WordnetSearch
from .MeCabTagger import MeCabTagger
import functools
from typing import Callable, Iterable, List, Set, Dict, Tuple, Optional

class Synonyms:
    w2v: Word2Vec = None
    wordnet_search: WordnetSearch = None
    tagger: MeCabTagger = None

    def __init__(
        self,
        w2v: Word2Vec,
        wordnet_search: WordnetSearch,
        tagger: MeCabTagger
    ):
        self.w2v = w2v
        self.wordnet_search = wordnet_search
        self.tagger = tagger

    def list_synonyms_from_similar_words(
        self,
        search: str or List[str],
        topn: int=20,
        threshold: int = 1,
        includes_self: bool = False,
    ) -> List[Tuple[str, int, float, int]]:
        neigbhor_list= self.w2v.most_similar(
            search,
            topn=topn,
        )
        # similar_words = [*map(lambda x:x[0],neigbhor_list)]
        synonyms = self.wordnet_search.get_synonym_score_for_neigbhor_list(
            neigbhor_list=neigbhor_list,
            threshold=threshold,
            includes_self=includes_self,
        )
        return synonyms

    def get_mixed_synonyms(
        self,
        search: str or Iterable[str],
        search_threshold: int=1,
        use_neigbhor_synonym: bool=True,
        append_neigbhors: bool = True,
        neigbhor_topn: int=20,
        neigbhor_boost: float=1.0,
        synonym_boost: float=1.0,
        neigbhor_synonym_boost=0.1,
        neigbhor_aggregate_entity: bool=True,
        similar_threshold: int=1,
    ) -> List[Dict]:
        synoyms_from_search = self.wordnet_search.get_words_in_shared_synsets(
            search=search,
            threshold=search_threshold,
        )
        neigbhor_list= self.w2v.most_similar(
            search,
            topn=neigbhor_topn,
            aggregate_entity=neigbhor_aggregate_entity,
        )
        if use_neigbhor_synonym:
            # similar_words = [*map(lambda x:x[0],neigbhor_list)]
            synonyms_from_similar_words = self.wordnet_search.get_synonym_score_for_neigbhor_list(
                neigbhor_list=neigbhor_list,
                threshold=similar_threshold,
                includes_self=True,
            )
        else:
            synonyms_from_similar_words = []
        
        if append_neigbhors:
            neighbor_words = [(None, word, score, 0) for (word, score) in neigbhor_list]
        else:
            neighbor_words = []

        aggregated_dict = {}
        for x, is_sim, is_neigbhor, boost in [
            *[(x, False, False, synonym_boost) for x in synoyms_from_search],
            *[(x, True, False, neigbhor_synonym_boost) for x in synonyms_from_similar_words],
            *[(x, False, True, neigbhor_boost) for x in neighbor_words]
        ]:
            key = x[1] # lemma
            score = x[2]*boost
            
            if key in aggregated_dict:
                curr = aggregated_dict[key]
                aggregated_dict[key] = {
                    **curr,
                    "s": curr["s"] + score,
                    "occ":curr["occ"] + (x[3] if not is_sim else 0),
                    "sim_occ":curr["sim_occ"] + (x[3] if is_sim else 0),
                    "is_neigbhor": curr["is_neigbhor"] or is_neigbhor
                }
            else:
                aggregated_dict[key] = {
                    "i": x[0], # wordid
                    "w": x[1], # word (lemma)
                    "s": score, # score
                    "occ": x[3] if not is_sim else 0, # occurrence in search iteself
                    "sim_occ": x[3] if is_sim else 0, # occurrence in similar words
                    "is_neigbhor": is_neigbhor
                }
        return list(aggregated_dict.values())

    def get_yomi_lookup(
        self,
        synonym_list: List[str]
    ):
        with_yomi = []
        for x in synonym_list:
            yomi = self.tagger.get_kana_yomi(x["w"])
            if yomi is None or len(yomi) < 1:
                continue
            with_yomi += [{**x, "y": yomi }]
        return functools.reduce(lambda acc, x: {
            **acc,
            x["y"]: (acc[x["y"]] if x["y"] in acc else []) + [x]
        }, with_yomi, {})

    def get_representative_word(
        self,
        search: str or List[str],
        items: Iterable[Dict],
    ):
        if len(items) < 1:
            return (None, None)
        if len(items) == 1:
            return (items[0], [])
        max_score = max(map(lambda x:x["s"], items))
        ties = [*filter(lambda x:x["s"] >= max_score, items)]
        if len(ties) < 2:
            rep = ties[0]
            return (rep, [*filter(lambda x:x["w"] != rep["w"], items)])
        sim_score = [*map(lambda x: (x, np.mean(self.w2v.similarity(search, x["w"]))), ties)]
        # top_sim_score = max(map(lambda x:x[1], sim_score))
        score_sorted = sorted(sim_score, key=lambda x: x[1], reverse=True)
        rep = score_sorted[0][0]
        return (rep, [*filter(lambda x:x["w"] != rep["w"], items)])

    @staticmethod
    def has_neigbhor(items: Iterable[Dict])-> bool:
        return len([True for x in items if x["is_neigbhor"]]) > 0

    @staticmethod
    def aggregate_score(items: Iterable[Dict]):
        scores = [*map(lambda x:x["s"], items)]
        return sum(scores)

    def aggregate_by_yomi(
        self,
        search: str or List[str],
        synonym_list: List[str],
        top_n: int = 20,
        use_similar_yomi: bool = True,
        remove_self: bool = True,
        jaro_winkler_prefix_weight: float = 0.05,
        jaro_winkler_threshold: float = 0.95,
    ):
        yomi_lookup = self.get_yomi_lookup(synonym_list)
        unique_yomi_list = [yomi for yomi in yomi_lookup.keys() if yomi != '']
        if use_similar_yomi:
            yomi_table,_ = self.get_similar_yomi_table(
                unique_yomi_list,
                prefix_weight = jaro_winkler_prefix_weight,
                threshold = jaro_winkler_threshold,
            )
        else:
            yomi_table = dict([(yomi, yomi) for yomi in unique_yomi_list])
        yomi_aggregated = []
        for yomi, similar_yomis in yomi_table.items():
            items = sum([yomi_lookup[sim_y] for sim_y in similar_yomis], [])
            (rep,_) = self.get_representative_word(search, items)
            has_neigbhor = self.has_neigbhor(items)
            agg_score = self.aggregate_score(items)
            yomi_aggregated.append({
                "i": rep["i"],
                "word": rep["w"],
                "yomi": rep["y"],
                "neigbhor": has_neigbhor,
                "score": agg_score,
                "children": items
            })
        
        if remove_self and type(search) == str:
            self_yomi = self.tagger.get_kana_yomi(search)
            yomi_aggregated = [*filter(lambda x: x["yomi"] != self_yomi, yomi_aggregated)]
        if remove_self and type(search) == list:
            self_yomis = [self.tagger.get_kana_yomi(s) for s in search]
            yomi_aggregated = [*filter(lambda x: x["yomi"] not in self_yomis, yomi_aggregated)]

        agg_sorted = sorted(yomi_aggregated, key=lambda x:x["score"], reverse=True)
        if top_n <= 0:
            return agg_sorted
        return agg_sorted[0: top_n]


    @staticmethod
    def get_similar_yomi_table(
        yomi_list: List[str],
        prefix_weight: float = 0.05,
        threshold: float = 0.90
    ):
        n = len(yomi_list)
        parent = [-1] * n
        root_word = [None] * n
        sim_links = []
        for i, w_i in enumerate(yomi_list):
            sims = []
            for  j, w_j in enumerate(yomi_list[i+1:], i+1):
                if parent[j] >= 0:
                    continue
                dist = Levenshtein.jaro_winkler(w_i, w_j, prefix_weight) # pylint: disable =no-member
                if dist < threshold:
                    continue
                parent[j] = i
                root_word[j] = yomi_list[i] if parent[i] < 0 else root_word[i]
                sims += [(j, w_j, dist)]
            if parent[i] < 0 or len(sims) > 0:
                sim_links += [(i, w_i, parent[i], sims)]
            else:
                sim_links += [None]
        translate_dict = dict([
            (yomi_list[i], root_word[i] if root_word[i] is not None else yomi_list[i])
            for i in range (0, n)
        ])
        yomi_table = functools.reduce(
            lambda acc, x: {
                **acc,
                x[1]: [x[0]] if x[1] not in acc else [*acc[x[1]], x[0]]
            }, translate_dict.items(), {})
        return yomi_table, sim_links

    @staticmethod
    def sort_by_score(
        synonym_list: List[str],
        top_n: int = -1,
        order: str = "asc",
    ) -> List[Dict]:
        result_sorted = sorted(
            synonym_list,
            key=lambda x: x["s"],
            reverse=order=="desc",
        )
        if (top_n > 0 and type(top_n) == int):
            return result_sorted[0:top_n]
        return result_sorted

    @staticmethod
    def get_top_n_percentile(
        synonym_list: List[str],
        percentile: float = 0.95,
    ) -> List[Dict]:
        if len(synonym_list) < 1:
            return []
        sorted_list = Synonyms.sort_by_score(synonym_list, order="desc")
        score_list = [*map(lambda x:x["s"], sorted_list)]
        total_score = sum(score_list)
        until = percentile * total_score
        curr = 0.0
        for i,s in enumerate(score_list):
            curr += s
            if (curr >= until):
                break
        return sorted_list[0:i]
