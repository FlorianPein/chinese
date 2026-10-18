"""The Pinyin chart: which syllable sits in which cell.

A cell is a final plus a group of initials, written "a:bpmf" (ba pa ma fa) or
"uo:none" (wo). Syllables use v for ü, like pinyin.py.
"""

import pinyin

I_FINALS = {"i", "ia", "ie", "iao", "iu", "ian", "in", "iang", "ing", "iong"}
U_FINALS = {"u", "ua", "uo", "uai", "ui", "uan", "un", "uang", "ueng"}
V_FINALS = {"ü", "üe", "üan", "ün"}
BUZZ = {"z", "c", "s", "zh", "ch", "sh", "r"}   # initials that take the buzzing -i
# how a final is written with no initial (None: it doesn't occur alone)
ALONE = {"a": "a", "o": "o", "e": "e", "er": "er", "ai": "ai", "ei": "ei", "ao": "ao", "ou": "ou",
         "an": "an", "en": "en", "ang": "ang", "eng": "eng", "ong": None, "-i": None,
         "i": "yi", "ia": "ya", "ie": "ye", "iao": "yao", "iu": "you", "ian": "yan", "in": "yin",
         "iang": "yang", "ing": "ying", "iong": "yong",
         "u": "wu", "ua": "wa", "uo": "wo", "uai": "wai", "ui": "wei", "uan": "wan", "un": "wen",
         "uang": "wang", "ueng": "weng",
         "ü": "yu", "üe": "yue", "üan": "yuan", "ün": "yun"}


def spell(initial, final):
    """How initial + final is written (v for ü), or None if the spelling rules rule it out."""
    if initial == "":
        s = ALONE[final]
        return s and s.replace("ü", "v")
    if final == "-i":
        return initial + "i" if initial in BUZZ else None
    if final == "er":
        return None
    if initial in ("j", "q", "x"):
        if final in I_FINALS:
            return initial + final
        if final in V_FINALS:
            return initial + final.replace("ü", "u")   # ju, jue, juan, jun
        return None
    if final in V_FINALS:
        return initial + final.replace("ü", "v")       # nü (nv), lüe (lve)
    if final in I_FINALS and (initial in BUZZ or initial in ("g", "k", "h")):
        return None
    return initial + final


class Chart:
    def __init__(self, course):
        self.groups = {g["id"]: g for g in course["groups"]}
        self.families = course["finals"]
        self.finals = [f for _, fs in self.families for f in fs]
        self.rare = set(course.get("rare", []))

    def cell(self, final, initial):
        """The syllable in one square of the chart, or None."""
        s = spell(initial, final)
        return s if s in pinyin.ALL_SYLLABLES and s not in self.rare else None

    def syllables(self, cell):
        """'a:bpmf' -> ['ba', 'pa', 'ma', 'fa']"""
        final, group = cell.split(":")
        if final not in self.finals or group not in self.groups:
            raise ValueError(f"unknown chart cell {cell!r}")
        out = [self.cell(final, i) for i in self.groups[group]["initials"]]
        return [s for s in out if s]

    def all_cells(self):
        """Every cell with at least one syllable."""
        return [f"{f}:{g}" for f in self.finals for g in self.groups if self.syllables(f"{f}:{g}")]
