"""Sentences to translate, for the app's Sentences tab.

data/sentences.json holds the sentences, one per line:

    {"about": "...", "sentences": [
      ["你是谁？", "Nǐ shì shéi?", "Who are you?"],
      ...
    ]}

Every sentence is made only of words from the word list (data/words.json),
each with the same Pinyin as there (tone marks without the 3rd-tone change,
with the changes of 一 and 不, light syllables unmarked), like the grammar
sentences. The app shows a sentence once you've seen all its words in the
Words tab, so a sentence's *level* is the place in the word list of its
furthest word. Every word must be in at least MIN_USES sentences, so you meet
it in different sentences.

Writing sentences: a row may leave out the Pinyin ([characters, English]);
`python tools/sentences.py fill` cuts it into words and writes the Pinyin from
the word list (with 一 and 不 changed before the next syllable). Read what it
wrote: a character with two readings (还 hái / huán, 得 de / děi) gets the
word list's one.

    python tools/sentences.py fill [file]      # add missing Pinyin, then check
    python tools/sentences.py refill [file]    # write all the Pinyin again (after changing the rules)
    python tools/sentences.py report [file] [--from N] [--to M]
                                               # each sentence's words and level,
                                               # and how often each word is used
"""

import json
import re
import sys
import unicodedata
from pathlib import Path

import grammar
import pinyin

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
MIN_USES = 3      # every word is in at least this many sentences
SOON = 10         # ...and should be in MIN_USES sentences you can do within 10 words of it
MAX_CHARS = 16    # characters in a sentence (without punctuation), so it stays short
# words after which 过 is the verb "to pass, to spend" (我过生日), not 去过 "have been"
NOT_BEFORE_GUO = {"我", "你", "他", "她", "它", "我们", "你们", "他们", "大家", "谁", "不", "没", "别", "要", "想",
                  "能", "会", "可以", "还", "也", "都", "就", "再", "又", "才", "先", "怎么", "一起", "得", "该",
                  "应该", "必须", "需要", "可能", "快", "已经", "一直", "不要", "不想", "不能", "不会", "想要"}
PUNCT_PY = {"，": ", ", "。": ". ", "？": "? ", "！": "! ", "：": ": ", "；": ", "}


def load_words():
    """The word list by characters (with "order", its place, and "id", its audio)."""
    import build
    return {w["hanzi"]: w for w in build.load_words().values()}


def dictionary(words):
    return grammar.Dictionary({w["id"]: w for w in words.values()})


def cut(hz, dic):
    """The words of a sentence, run by run: [[word, ...], punctuation, [word, ...], ...]."""
    out = []
    for m in re.finditer(rf"[一-鿿]+|[{grammar.PUNCT_ZH}]", hz):
        t = m.group()
        if grammar.HANZI.match(t[0]):
            out.append(["".join(t[a:b]) for a, b in dic.segment(list(t), lambda w: True)])
        else:
            out.append(t)
    return out


def make_pinyin(hz, dic):
    """Pinyin for a sentence from the word list's Pinyin of each word."""
    text = ""
    for part in cut(hz, dic):
        if isinstance(part, str):
            text = text.rstrip() + PUNCT_PY[part]
            continue
        pys = [dic.entries[w]["pinyin"] for w in part]
        for i, w in enumerate(part):
            # light: 个 as a measure word (哪个 nǎ ge), 过 after a verb (去过 qù guo)
            if w == "个" and i > 0:
                pys[i] = "ge"
            if w == "过" and i > 0 and part[i - 1] not in NOT_BEFORE_GUO:
                pys[i] = "guo"
            if w in ("不", "一") and i + 1 < len(part):
                tone = pinyin.syllables(pinyin.parse(pys[i + 1]))[0][1]
                pys[i] = {"不": "bú" if tone == 4 else "bù", "一": "yí" if tone == 4 else "yì"}[w]
        text += " ".join(pys) + " "
    text = text.strip()
    # capitals at the start and after . ? !
    return re.sub(r"(^|[.?!] )(\w)", lambda m: m.group(1) + m.group(2).upper(), unicodedata.normalize("NFC", text))


def load(path):
    return json.loads(Path(path).read_text())


def save(path, data):
    rows = ",\n".join("  " + json.dumps(r, ensure_ascii=False) for r in data["sentences"])
    head = json.dumps({k: v for k, v in data.items() if k != "sentences"}, ensure_ascii=False)[1:-1]
    Path(path).write_text("{" + head + (",\n" if head else "\n") + "\"sentences\": [\n" + rows + "\n]}\n")


def process(rows, words):
    """Check every sentence. Returns (errors, sentences for the app, audio items, uses by word)."""
    dic = dictionary(words)
    errors, out, items, seen = [], [], {}, {}
    uses = {h: 0 for h in words}
    for n, row in enumerate(rows, 1):
        where = f"sentence {n}"
        if len(row) != 3 or not all(isinstance(x, str) and x.strip() for x in row):
            errors.append(f"{where}: {row!r}: give [characters, Pinyin, English] (fill adds the Pinyin)")
            continue
        hz, py, english = row
        if hz in seen:
            errors.append(f"{where}: {hz} is also sentence {seen[hz]}")
            continue
        seen[hz] = n
        try:
            x = grammar.sentence(hz, py, english, dic, set(), lambda w: True)
        except ValueError as e:
            errors.append(f"{where}: {e}")
            continue
        chars = len(grammar.HANZI.findall(hz))
        if chars > MAX_CHARS:
            errors.append(f"{where}: {hz} has {chars} characters; at most {MAX_CHARS}")
        ws = [t[0] for t in x["tiles"]]
        for w in set(ws):
            uses[w] += 1
        x["level"] = max(dic.entries[w]["pos"] for w in ws)
        items[x["audio"]] = {"id": x["audio"], "kind": "sentence", "hanzi": x["hanzi"], "pinyin": x["pinyin"]}
        out.append(x)
    return errors, out, items, uses


def coverage_errors(uses, words):
    few = [h for h, n in uses.items() if n < MIN_USES]
    if not few:
        return []
    few.sort(key=lambda h: words[h]["order"])
    return [f"{len(few)} words in fewer than {MIN_USES} sentences: "
            + ", ".join(f"{h} #{words[h]['order']} ({uses[h]})" for h in few)]


def main():
    args = sys.argv[1:]
    cmd = args.pop(0) if args else "report"
    lo = hi = None
    if "--from" in args:
        i = args.index("--from"); lo = int(args[i + 1]); del args[i:i + 2]
    if "--to" in args:
        i = args.index("--to"); hi = int(args[i + 1]); del args[i:i + 2]
    path = Path(args[0]) if args else DATA / "sentences.json"
    words = load_words()
    data = load(path)
    if cmd in ("fill", "refill"):   # refill: write the Pinyin of every sentence again
        dic = dictionary(words)
        filled = 0
        for i, row in enumerate(data["sentences"]):
            if cmd == "refill" and len(row) == 3:
                new = make_pinyin(row[0], dic)
                if new != row[1]:
                    print(f"{row[1]}  ->  {new}")
                row = data["sentences"][i] = [row[0], row[2]]
            if len(row) == 2:
                try:
                    data["sentences"][i] = [row[0], make_pinyin(row[0], dic), row[1]]
                    filled += 1
                except ValueError as e:
                    print(f"ERROR sentence {i + 1}: {e}")
        save(path, data)
        print(f"Filled in the Pinyin of {filled} sentences.")
    errors, out, _, uses = process(data["sentences"], words)
    examples = {w["example"]["hanzi"] for w in words.values() if "example" in w}
    soon = {h: 0 for h in words}   # sentences with the word, open within SOON words of it
    for x in out:
        for w in {t[0] for t in x["tiles"]}:
            if x["level"] <= words[w]["order"] + SOON:
                soon[w] += 1
        if (lo is None or x["level"] >= lo) and (hi is None or x["level"] <= hi):
            print(f"#{x['level']:>3}  {x['hanzi']}  {x['pinyin']}  | {' '.join(t[0] for t in x['tiles'])} | {x['english']}")
        if x["hanzi"] in examples:
            print(f"WARNING {x['hanzi']} is the example sentence of a word card: write another one")
    for e in errors:
        print("ERROR", e)
    order = sorted(words, key=lambda h: words[h]["order"])
    rng = [h for h in order if (lo is None or words[h]["order"] >= lo) and (hi is None or words[h]["order"] <= hi)]
    few = [h for h in rng if uses[h] < MIN_USES]
    late = [h for h in rng if soon[h] < MIN_USES and h not in few]
    print(f"\n{len(out)} sentences. Words #{lo or 1}–#{hi or len(order)}: "
          f"{len(rng) - len(few)} of {len(rng)} in at least {MIN_USES} sentences, "
          f"{len(rng) - len(few) - len(late)} of them in {MIN_USES} that open within {SOON} words.")
    if few:
        print("Need more sentences (uses): " + ", ".join(f"{h} #{words[h]['order']} ({uses[h]})" for h in few))
    if late:
        print(f"Too few sentences that open within {SOON} words (uses that soon): "
              + ", ".join(f"{h} #{words[h]['order']} ({soon[h]})" for h in late))


if __name__ == "__main__":
    main()
