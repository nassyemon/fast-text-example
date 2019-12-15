import re
import math
import sqlite3
import functools
from typing import Callable, Iterable, List, Set, Dict, Tuple, Optional

conn = None

class WordnetSearch:
    DEBUG = True
    db_filepath = None
    conn = None

    def __init__(self, db_filepath):
        global conn
        self.db_filepath = db_filepath
        if self.DEBUG and conn is not None:
            self.conn = conn
            return
        self.conn = sqlite3.connect(self.db_filepath, check_same_thread=False)
        conn = self.conn

    def reload(self, db_filepath = None):
        global conn
        if db_filepath is not None:
            self.db_filepath = db_filepath
        self.conn = sqlite3.connect(self.db_filepath, check_same_thread=False)
        conn = self.conn

    def get_words_in_shared_synsets(
        self,
        search: str or List[str],
        threshold: int = 1,
        score_func: str = "log",
    ) -> List[Tuple[int, str, float, int]]:
        num_searches = len(search) if type(search) is list else 1
        params = [*search, threshold] if type (search) is list else (search, threshold)
        query = self.get_words_in_shared_synset_query(num_searches)
        # print(placeholder, params)
        cur = self.conn.execute(query, params)
        return list(map(lambda x:self.modify_score(x, score_func=score_func), cur.fetchall()))

    ## returns a list of
    ## (wordid: int, lemma: str,score: float, occurrence: int)
    def get_synonym_score_for_neigbhor_list(
        self,
        neigbhor_list: Iterable[Tuple[str, float]],
        threshold: int = 1,
        includes_self: bool = False,
        score_func: str = "log",
    ) -> List[Tuple[str, int, float, int]]:
        (values_query, params) = self.create_values_query(neigbhor_list)
        query = self.create_neigbhor_list_score_query(values_query, includes_self)
        cur = self.conn.execute(query, {**params, "threshold": threshold })
        return list(map(lambda x:self.modify_score(x, score_func=score_func), cur.fetchall()))
    
    @staticmethod
    def modify_score(x, score_func="log"):
        if score_func == "log":
            return (x[0], x[1], 1+math.log(x[2], 2), x[3])
        return x[0:4]
    
    @staticmethod
    def get_words_in_shared_synset_query(num_searches: int):
        placeholder = ",".join(["?" for i in range(0, num_searches)])
        return f"""\
select
    sub.wordid,
    sub.lemma,
    sum(1.0) as score,
    count(sub.lemma) as occurrence
from (
    select
        related_word.wordid,
        related_word.lemma
    from word base
    inner join sense attributed_sense
        on attributed_sense.wordid = base.wordid
    inner join sense all_sense
        on all_sense.synset = attributed_sense.synset
    inner join word related_word
        on related_word.wordid = all_sense.wordid
        and related_word.lang = "jpn"
    where base.lemma in ({placeholder})
) sub
group by sub.lemma, sub.wordid
having count(sub.lemma) >= (?)
order by count(sub.lemma) desc\
"""

    @staticmethod
    def create_values_query(
        neigbhor_list: Iterable[Tuple[str, float]],
    ) -> Tuple[str, Dict]:
        params = functools.reduce(
            lambda acc,e: { **acc, f"w{e[0]}": e[1][0], f"s{e[0]}": e[1][1] },
            enumerate(neigbhor_list),
            {}
        )
        query_elems = [f":w{i}, :s{i}" for i in range(0, len(neigbhor_list))]
        return (f"""select {" union select ".join(query_elems)} """, params)

    @staticmethod
    def create_neigbhor_list_score_query(
        values_query: str,
        includes_self: bool,
    ) -> str:
        return f"""\
with neigbhors(word, score) as (
    {values_query}
),
sub(word, score, wordid, lemma) as
(
    select
        n.word,
        n.score,
        rel_w.wordid,
        rel_w.lemma
    from neigbhors n
    inner join word w
        on w.lemma = n.word
    inner join sense s
        on s.wordid = w.wordid
    inner join sense rel_s
        on rel_s.synset = s.synset
        {"" if includes_self else "and rel_s.wordid != s.wordid" }
    inner join word rel_w
        on rel_w.wordid = rel_s.wordid
        and rel_w.lang = "jpn"
)
select
    sub.wordid,
    sub.lemma,
    sum(sub.score) as score,
    count(sub.lemma) as occurrence
from sub
group by sub.lemma, sub.wordid
having count(sub.lemma) >= :threshold
order by count(sub.lemma) desc\
"""

