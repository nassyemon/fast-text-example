import re
import MeCab
from typing import Callable, Iterable, List, Set, Dict, Tuple, Optional

class MeCabTagger:
    DEBUG = True
    yomi: MeCab.Tagger = None
    RE_ALL_KATAKANAS = re.compile(r'^[\u30A1-\u30F4]+$')

    def __init__(self):
        self.yomi = MeCab.Tagger("-Oyomi")

    def reload(self):
        self.yomi = MeCab.Tagger("-Oyomi")

    def get_kana_yomi(self, text: str) -> str:
        # TODO return None if yumi parse failed
        reading = self.yomi.parse(text).replace("\n", '')
        matched = self.RE_ALL_KATAKANAS.match(reading)
        if matched:
            return matched[0]
        return None
