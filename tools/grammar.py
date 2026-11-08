"""Grammar sessions for the app's Grammar tab: one topic per session, in HSK order.

data/grammar.json lists every topic (id, HSK level, title, focus). A topic is
built once it has its own file, data/grammar/<id>.json:

    {
      "goal": "What you can say after this session.",
      "extra": ["老师", ["学生", "xuésheng", "student"]],  # new words this session brings (few!)
      "blocks": [                                        # the explanation, top to bottom
        {"h": "A heading"},
        {"text": "A paragraph. **bold**, *italic*."},
        {"pattern": "A + 是 + B", "english": "A is B"},
        {"ex": [["我[是]老师。", "Wǒ [shì] lǎoshī.", "I'm a teacher.", "optional note"], ...]},
        {"wrong": [["我是很好。", "Wǒ shì hěn hǎo.", "why it's wrong"], ...]},
        {"tip": "A highlighted tip."}
      ],
      "exercises": [                                     # the quiz at the end; first option = right
        {"order": ["我是老师。", "Wǒ shì lǎoshī.", "I'm a teacher."], "also": ["…"]},
        {"gap": ["你是老师＿？", "Nǐ shì lǎoshī ＿?", "Are you a teacher?"],
         "options": [["吗", "ma"], ["呢", "ne"]], "explain": "…"},
        {"pick": "I'm not a teacher.", "options": [["我不是老师。", "Wǒ bú shì lǎoshī."], …], "explain": "…"},
        {"meaning": ["他也是老师。", "Tā yě shì lǎoshī."], "options": ["He's a teacher too.", …], "explain": "…"}
      ]
    }

[Brackets] mark the grammar point in an example, in the characters and in the
Pinyin; the card highlights it. Pinyin follows the word list: tone marks
without the 3rd-tone change, with the changes of 一 and 不 (yí ge, bú shì),
light syllables unmarked.

The check: every sentence has one syllable per character, and is cut into
words that are all in the word list (data/words.json) or declared as extra
words (here or in an earlier session), each with the same Pinyin as there.
The further on the topic, the further down the word list its words may be
(word_limit): the first topic uses only the 170 most common words, the last
one all of them. A session may bring a few more words as "extra": a word
from further down the list (just its characters), or one that isn't in the
list ([characters, Pinyin, English]). Later sessions may use them too.
"""

import hashlib
import json
import re
import unicodedata

import pinyin

HANZI = re.compile(r"[一-鿿]")
PUNCT_ZH = "，。？！：；、"
GAP = "＿"
FIRST_LIMIT = 170   # the first topic only uses the 170 most common words
MAX_EXTRA = 6       # extra words per session


def word_limit(i, n, words):
    """How far down the word list topic i of n may go: the more advanced the
    grammar, the more advanced the words."""
    return round(FIRST_LIMIT + (words - FIRST_LIMIT) * i / max(1, n - 1))


def sentence_id(hanzi, py):
    return "g-" + hashlib.md5(f"{hanzi}|{py}".encode()).hexdigest()[:10]


def syllable_spans(py):
    """[start, end] of each syllable in a Pinyin text."""
    spans = []
    for m in re.finditer(r"[^\W\d_]+", py):
        letters, _ = pinyin._letters_and_tones(m.group())
        parts = pinyin._split_word(letters)
        if parts is None or len(letters) != len(m.group()):
            raise ValueError(f"can't split {m.group()!r} into Pinyin syllables")
        pos = m.start()
        for part in parts:
            spans.append((pos, pos + len(part)))
            pos += len(part)
    return spans


def same_pinyin(want, got):
    """A word's Pinyin in a sentence: as in the word list, except that 一 and
    不 change tone, and any syllable may be light."""
    a = pinyin.syllables(pinyin.parse(want))
    b = pinyin.syllables(pinyin.parse(got))
    return len(a) == len(b) and all(
        b1 == b2 and (t1 == t2 or b1 in ("yi", "bu") or t2 == 5) for (b1, t1), (b2, t2) in zip(a, b))


class Dictionary:
    """The word list plus the extra words declared so far."""

    def __init__(self, words):
        self.entries = {}   # hanzi -> {pinyin, english, pos (place in the word list) or None, audio}
        for n, w in enumerate(sorted(words.values(), key=lambda w: w["order"]), 1):
            self.entries[w["hanzi"]] = {"pinyin": w["pinyin"], "english": w["english"], "pos": n, "audio": w["id"]}
        self.longest = max(len(h) for h in self.entries) if self.entries else 1
        self.introduced = {}   # hanzi -> session that brought it as an extra word

    def add_extra(self, hanzi, py, english, session, word_id):
        if hanzi in self.introduced:
            raise ValueError(f"{hanzi} is already an extra word of {self.introduced[hanzi]}")
        if py is None:
            if hanzi not in self.entries:
                raise ValueError(f"{hanzi} isn't in the word list: give [characters, Pinyin, English]")
        elif hanzi in self.entries:
            raise ValueError(f"{hanzi} is in the word list: give just its characters")
        else:
            self.entries[hanzi] = {"pinyin": py, "english": english, "pos": None, "audio": word_id}
            self.longest = max(self.longest, len(hanzi))
        self.introduced[hanzi] = session

    def segment(self, chars, allowed):
        """Cut a run of characters into as few known words as possible,
        avoiding words the topic may not use yet (很多 can be 很 + 多)."""
        n = len(chars)
        best = [None] * (n + 1)   # best[i] = (cost, cuts) covering chars[:i]
        best[0] = (0, [])
        for i in range(n):
            if best[i] is None:
                continue
            for j in range(i + 1, min(n, i + self.longest) + 1):
                w = "".join(chars[i:j])
                if w in self.entries:
                    cost = best[i][0] + (1 if allowed(w) else 1000)
                    if best[j] is None or cost < best[j][0]:
                        best[j] = (cost, best[i][1] + [(i, j)])
        if best[n] is None:
            reach = max(i for i in range(n + 1) if best[i] is not None)
            raise ValueError(f"{''.join(chars)}: {''.join(chars[reach:reach + 2])}… isn't in the word list; "
                             "use another word or add it to the session's extra words")
        return best[n][1]


def strip_marks(text):
    """'我[是]老师' -> ('我是老师', [(1, 2)])"""
    out, marks, start = "", [], None
    for ch in text:
        if ch == "[":
            if start is not None:
                raise ValueError(f"{text!r}: [ inside [ ]")
            start = len(out)
        elif ch == "]":
            if start is None:
                raise ValueError(f"{text!r}: ] without [")
            marks.append((start, len(out)))
            start = None
        else:
            out += ch
    if start is not None:
        raise ValueError(f"{text!r}: [ without ]")
    return out, marks


def sentence(hz, py, english, dic, used, allowed, audio=True):
    """Check a sentence and work out its words; returns what the app needs."""
    py = unicodedata.normalize("NFC", py)
    hz, hz_marks = strip_marks(hz)
    py, py_marks = strip_marks(py)
    if len(hz_marks) != len(py_marks):
        raise ValueError(f"{hz}: {len(hz_marks)} [marks] in the characters, {len(py_marks)} in the Pinyin")
    if not re.fullmatch(rf"[一-鿿{PUNCT_ZH}]+", hz):
        raise ValueError(f"{hz!r}: Chinese characters and Chinese punctuation only")
    spans = syllable_spans(py)
    pos = [i for i, c in enumerate(hz) if HANZI.match(c)]
    if len(spans) != len(pos):
        raise ValueError(f"{hz}: {len(spans)} syllables in {py!r} for {len(pos)} characters")
    pinyin.tts_tokens([("syl", pinyin.SAY_AS.get(x[1], x[1]), x[2]) if x[0] == "syl" else x
                       for x in pinyin.parse(py)])   # the voice can say every syllable
    # each run of characters between punctuation, cut into words
    words, tiles, k = [], [], 0
    for run in re.finditer(r"[一-鿿]+", hz):
        chars = list(run.group())
        for a, b in dic.segment(chars, allowed):
            w = "".join(chars[a:b])
            said = py[spans[k + a][0]:spans[k + b - 1][1]]
            entry = dic.entries[w]
            if not same_pinyin(entry["pinyin"], said):
                raise ValueError(f"{hz}: {w} is {entry['pinyin']!r} in the word list, here {said!r}")
            words.append(w)
            if said[:1].isupper() and not entry["pinyin"][:1].isupper():   # sentence start
                said = said[:1].lower() + said[1:]
            tiles.append([w, said])
        k += len(chars)
    used.update(words)
    marks = []
    for (a, b), (c, d) in zip(hz_marks, py_marks):
        n_hz = sum(1 for i in range(a, b) if HANZI.match(hz[i]))
        n_py = sum(1 for s, e in spans if s >= c and e <= d)
        if n_hz != n_py:
            raise ValueError(f"{hz}: [{hz[a:b]}] and [{py[c:d]}] don't match")
        marks.append([a, b, c, d])
    out = {"hanzi": hz, "pinyin": py, "numbers": pinyin.to_numbers(py)}
    if english:
        out["english"] = english
    if marks:
        out["mark"] = marks
    out["tiles"] = tiles
    if audio:
        out["audio"] = sentence_id(hz, py)
    return out


def load(data_dir):
    plan = json.loads((data_dir / "grammar.json").read_text())["topics"]
    sessions = {}
    for t in plan:
        f = data_dir / "grammar" / f"{t['id']}.json"
        if f.exists():
            sessions[t["id"]] = {**t, **json.loads(f.read_text())}
    return plan, sessions


def process(plan, sessions, words, word_id):
    """Check every built session. Returns (errors, built sessions for the app,
    audio items {id: item})."""
    errors, out, items = [], [], {}
    dic = Dictionary(words)
    ids = [t["id"] for t in plan]
    if len(set(ids)) != len(ids):
        errors.append("grammar.json: a topic id is listed twice")
    levels = [t["hsk"] for t in plan]
    if levels != sorted(levels):
        errors.append("grammar.json: topics must be in HSK order")
    for t in plan:
        if t["id"] not in sessions:
            continue
        s, sid = sessions[t["id"]], t["id"]
        used = set()
        limit = word_limit(ids.index(sid), len(ids), len(words))
        allowed = lambda w: (dic.entries[w]["pos"] or 0) <= limit or w in dic.introduced
        res = {k: s[k] for k in ("id", "hsk", "title", "focus", "goal")}
        res["blocks"], res["exercises"] = [], []

        def add_sentence(where, hz, py, english, audio=True):
            try:
                x = sentence(hz, py, english, dic, used, allowed, audio)
            except ValueError as e:
                errors.append(f"{sid} {where}: {e}")
                return None
            if audio:
                items[x["audio"]] = {"id": x["audio"], "kind": "sentence", "hanzi": x["hanzi"], "pinyin": x["pinyin"]}
            return x

        extra = s.get("extra", [])
        if len(extra) > MAX_EXTRA:
            errors.append(f"{sid}: {len(extra)} extra words; at most {MAX_EXTRA}, use words from the list")
        for x in extra:
            hz, py, english = (x, None, None) if isinstance(x, str) else x
            if py is None and hz in dic.entries and (dic.entries[hz]["pos"] or 0) <= limit:
                errors.append(f"{sid} extra {hz}: #{dic.entries[hz]['pos']} of the word list is common enough "
                              f"for this topic (up to #{limit}); no need to list it")
                continue
            try:
                if py is not None and len(pinyin.syllables(pinyin.parse(py))) != len(hz):
                    raise ValueError(f"{py!r} doesn't fit {hz}")
                dic.add_extra(hz, py, english, sid, word_id(hz))
                if py is not None:
                    items[word_id(hz)] = {"id": word_id(hz), "kind": "word", "hanzi": hz, "pinyin": py}
            except ValueError as e:
                errors.append(f"{sid} extra {hz}: {e}")
        for n, b in enumerate(s["blocks"], 1):
            where = f"block {n}"
            if "ex" in b:
                exs = []
                for e in b["ex"]:
                    x = add_sentence(where, e[0], e[1], e[2])
                    if x:
                        if len(e) > 3:
                            x["note"] = e[3]
                        exs.append(x)
                res["blocks"].append({"ex": exs})
            elif "wrong" in b:
                exs = []
                for e in b["wrong"]:
                    x = add_sentence(where, e[0], e[1], None, audio=False)
                    if x:
                        x["why"] = e[2]
                        exs.append(x)
                res["blocks"].append({"wrong": exs})
            elif any(k in b for k in ("h", "text", "pattern", "tip")):
                res["blocks"].append(b)
            else:
                errors.append(f"{sid} {where}: unknown block {list(b)}")
        for n, e in enumerate(s["exercises"], 1):
            where = f"exercise {n}"
            if "order" in e:
                x = add_sentence(where, *e["order"])
                if not x:
                    continue
                q = {"type": "order", "sentence": x, "also": e.get("also", [])}
                plain = lambda h: re.sub(rf"[{PUNCT_ZH}]", "", h)
                for alt in q["also"]:
                    if sorted(plain(alt)) != sorted(plain(x["hanzi"])):
                        errors.append(f"{sid} {where}: {alt} doesn't use the same words")
                if len(x["tiles"]) < 3:
                    errors.append(f"{sid} {where}: needs at least 3 words to put in order")
            elif "gap" in e:
                hz, py, english = e["gap"]
                if hz.count(GAP) != 1 or py.count(GAP) != 1:
                    errors.append(f"{sid} {where}: one {GAP} in the characters and one in the Pinyin")
                    continue
                opts = e["options"]
                x = add_sentence(where, hz.replace(GAP, opts[0][0]), py.replace(GAP, opts[0][1]), english)
                for o in opts[1:]:   # the wrong options must still be words
                    add_sentence(where, hz.replace(GAP, o[0]), py.replace(GAP, o[1]), None, audio=False)
                if not x:
                    continue
                q = {"type": "gap", "hanzi": hz, "pinyin": py, "english": english,
                     "options": [{"hanzi": h, "pinyin": p} for h, p in opts], "sentence": x}
            elif "pick" in e:
                opts = [add_sentence(where, h, p, None, audio=(i == 0)) for i, (h, p) in enumerate(e["options"])]
                if not all(opts):
                    continue
                q = {"type": "pick", "english": e["pick"], "options": opts, "sentence": {**opts[0], "english": e["pick"]}}
            elif "meaning" in e:
                hz, py = e["meaning"]
                x = add_sentence(where, hz, py, e["options"][0])
                if not x:
                    continue
                q = {"type": "meaning", "options": e["options"], "sentence": x}
            else:
                errors.append(f"{sid} {where}: unknown exercise {list(e)}")
                continue
            if q["type"] != "order":
                if len(e["options"]) < 2:
                    errors.append(f"{sid} {where}: needs at least 2 options")
                if len(set(map(str, e["options"]))) != len(e["options"]):
                    errors.append(f"{sid} {where}: an option is listed twice")
            if "explain" in e:
                q["explain"] = e["explain"]
            res["exercises"].append(q)
        if len(res["exercises"]) < 4:
            errors.append(f"{sid}: needs at least 4 exercises")
        # the words of the session, in the order they come in the word list
        far = [h for h in used if not allowed(h)]
        if far:
            errors.append(f"{sid}: words too far down the word list for this topic (up to #{limit}): "
                          + ", ".join(f"{h} #{dic.entries[h]['pos']}" for h in sorted(far, key=lambda h: dic.entries[h]['pos']))
                          + "; use more common words or add them to the session's extra words")
        unused = [x if isinstance(x, str) else x[0] for x in extra]
        unused = [h for h in unused if h not in used]
        if unused:
            errors.append(f"{sid}: extra words never used: {', '.join(unused)}")
        res["limit"] = limit
        res["words"] = [{"hanzi": h, **dic.entries[h], **({"new": True} if dic.introduced.get(h) == sid else {})}
                        for h in sorted(used, key=lambda h: (dic.entries[h]["pos"] or 10 ** 6, h))]
        out.append(res)
    return errors, out, items
