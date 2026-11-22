"""Spoonfed: the sentences of the Anki deck "Spoonfed Chinese", in the deck's
order, for the app's Sentences tab (flashcards like the Words tab), and the word
list of the Words tab: the deck's words in the order they first appear.

The deck (https://ankiweb.net/shared/info/1271086873, 7335 sentences, each a
little harder than the one before) isn't in the repo: download the .apkg from
that page and import it once. Everything made from it is committed.

    python tools/spoonfed.py import Spoonfed_Chinese.apkg
        # data/spoonfed.json (the sentences, cleaned up) and the deck's own
        # recordings in docs/audio/sf/<id>.mp3 (mono, same loudness)
    python tools/spoonfed.py audio [--limit N]
        # the sentences the deck has no recording for: made with the offline
        # voice of tools/build.py (can be stopped and started again)
    python tools/spoonfed.py build
        # docs/spoonfed.json for the app: each sentence cut into words, with
        # the Pinyin and meaning of each word (CC-CEDICT) and the words that
        # are new in it (first time in the deck); and docs/words.json for the
        # Words tab: each word of the deck where it is new, with that sentence
    python tools/spoonfed.py words-audio [--limit N] [--part K/N]
        # recordings of the deck's words that data/words.json doesn't have, made
        # with the voice, in docs/audio/sw/ (can be stopped and started again;
        # --part 0/2 and --part 1/2 run two halves at once)

data/spoonfed.json, one sentence per line, in the deck's order:

    {"about": "...", "sentences": [
      [1419644212689, "你好！", "Nǐ hǎo!", "Hello!"],
      ...
    ]}

[id (the deck's note id, also the audio file name), characters, Pinyin,
English]. A dialogue has one line per speaker ("A: …\\nB: …"). To fix a
sentence, edit it here and run `build` (and delete its audio file and run
`audio` if it was made by the voice).

Words: the deck's Pinyin is written word by word (Wǒmen páshàng le yī gè
dǒupō.), so each Pinyin word gives the characters of one word. A word that
isn't in CC-CEDICT is cut further into the longest words that are. Where the
Pinyin doesn't line up with the characters (digits, names), the characters are
cut by CC-CEDICT alone and its Pinyin is used.
"""

import html
import json
import re
import sqlite3
import subprocess
import sys
import tempfile
import unicodedata
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build  # noqa: E402
import pinyin  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "spoonfed.json"
APP_FILE = ROOT / "docs" / "spoonfed.json"
SF = build.AUDIO / "sf"
MANIFEST = SF / "manifest.json"
SW = build.AUDIO / "sw"
SW_MANIFEST = SW / "manifest.json"
WORDS_FILE = ROOT / "docs" / "words.json"
CEDICT = build.CACHE / "cedict_ts.u8"
CEDICT_URL = "https://www.mdbg.net/chinese/export/cedict/cedict_1_0_ts_utf-8_mdbg.zip"
DECK_URL = "https://ankiweb.net/shared/info/1271086873"
ABOUT = (f"The sentences of the Anki deck Spoonfed Chinese ({DECK_URL}), in the deck's order, "
         "for the Spoonfed tab. Made by tools/spoonfed.py import; [id, characters, Pinyin, English].")

HANZI = re.compile(r"[\u3400-\u9fff]")
UNIT = re.compile(r"[\u3400-\u9fff]|[A-Za-z0-9]+")      # what a Pinyin word lines up with
PY_WORD = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*|\d+")  # a Pinyin word, or a number
BITRATE = "32k"


# --- import ------------------------------------------------------------------

def clean(text):
    """A deck field as plain text: line breaks kept, tags and entities gone."""
    text = re.sub(r"<br\s*/?>|</div>", "\n", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(html.unescape(text)).replace("\xa0", " ")
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n")]
    return unicodedata.normalize("NFC", "\n".join(line for line in lines if line and line not in "-–"))


def tidy(hanzi, py):
    """Dialogues: 'A我也想。\\nB那…' -> 'A: 我也想。\\nB: 那…', and the Pinyin
    lines labelled the same way when there are as many."""
    hz_lines, py_lines = hanzi.split("\n"), py.split("\n")
    labels = [m.group(1) if (m := re.match(r"^([AB])\s*[:：]?\s*(?=[^\sA-Za-z])", line)) else None
              for line in hz_lines]
    if len(hz_lines) > 1 and all(labels):
        hz_lines = [f"{lab}: {line[1:].lstrip(':： ')}" for lab, line in zip(labels, hz_lines)]
        if len(py_lines) == len(hz_lines):
            py_lines = [f"{lab}: {line}" for lab, line in zip(labels, py_lines)]
    hanzi = "\n".join(hz_lines)
    # a stray quote mark left at the end (…讨论。")
    if hanzi.count('"') % 2:
        hanzi = hanzi.rstrip('"').rstrip()
    return hanzi, "\n".join(py_lines)


def read_deck(apkg):
    """[(note id, characters, Pinyin, English, recording's file in the zip or None)] in the deck's order."""
    with zipfile.ZipFile(apkg) as z, tempfile.TemporaryDirectory() as tmp:
        name = next(n for n in ("collection.anki21", "collection.anki2") if n in z.namelist())
        db_path = Path(tmp) / "c.db"
        db_path.write_bytes(z.read(name))
        media = {v: k for k, v in json.loads(z.read("media")).items()}
        db = sqlite3.connect(db_path)
        models = json.loads(db.execute("select models from col").fetchone()[0])
        fields = {int(mid): [f["name"] for f in m["flds"]] for mid, m in models.items()}
        out = []
        for nid, mid, flds in db.execute(
                "select n.id, n.mid, n.flds from cards c join notes n on n.id = c.nid order by c.due, c.id"):
            f = dict(zip(fields[mid], flds.split("\x1f")))
            sound = re.search(r"\[sound:([^\]]+)\]", f.get("Audio", ""))
            hanzi, py = tidy(clean(f["Hanzi"]), clean(f["Pinyin"]))
            out.append((nid, hanzi, py, clean(f["English"]), media.get(sound.group(1)) if sound else None))
        db.close()
        return out


def encode(src_bytes, out):
    """A recording as a mono MP3 at the same loudness as the others."""
    with tempfile.NamedTemporaryFile(suffix=".mp3") as f:
        f.write(src_bytes)
        f.flush()
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f.name, "-ac", "1", "-ar", "22050",
                        "-af", "loudnorm=I=-18:TP=-1.5:LRA=11", "-b:a", BITRATE, str(out)], check=True)


def save_data(rows):
    lines = ",\n".join("  " + json.dumps(list(r), ensure_ascii=False) for r in rows)
    DATA_FILE.write_text("{" + json.dumps({"about": ABOUT}, ensure_ascii=False)[1:-1]
                         + ",\n\"sentences\": [\n" + lines + "\n]}\n")


def load_data():
    return [tuple(r) for r in json.loads(DATA_FILE.read_text())["sentences"]]


def load_manifest():
    return json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}


def save_manifest(m):
    MANIFEST.write_text(json.dumps(dict(sorted(m.items())), ensure_ascii=False, indent=0) + "\n")


def cmd_import(apkg, force=False):
    deck = read_deck(apkg)
    save_data([(nid, hz, py, en) for nid, hz, py, en, _ in deck])
    print(f"{len(deck)} sentences -> {DATA_FILE.relative_to(ROOT)}")
    SF.mkdir(parents=True, exist_ok=True)
    manifest = load_manifest()
    todo = [(nid, src) for nid, *_, src in deck
            if src and (force or not (SF / f"{nid}.mp3").exists() or manifest.get(str(nid), {}).get("from") != "deck")]
    with zipfile.ZipFile(apkg) as z:
        data = {src: z.read(src) for _, src in todo}

    def one(job):
        nid, src = job
        encode(data[src], SF / f"{nid}.mp3")
        return nid

    with ThreadPoolExecutor(4) as pool:
        for n, nid in enumerate(pool.map(one, todo), 1):
            manifest[str(nid)] = {"from": "deck"}
            if n % 500 == 0:
                print(f"  {n}/{len(todo)} recordings")
                save_manifest(manifest)
    save_manifest(manifest)
    print(f"{len(todo)} recordings from the deck; {sum(1 for *_, s in deck if not s)} sentences have none "
          "(make them with: python tools/spoonfed.py audio)")


# --- audio for the sentences without a recording --------------------------------

DIGITS = "líng yī èr sān sì wǔ liù qī bā jiǔ".split()


def number_pinyin(n):
    """12 -> 'shí èr', 305 -> 'sān bǎi líng wǔ' (up to 9999; longer: digit by digit)."""
    if n >= 10000:
        return " ".join(DIGITS[int(d)] for d in str(n))
    if n < 10:
        return DIGITS[n]
    parts, zero = [], False
    for value, name in ((1000, "qiān"), (100, "bǎi"), (10, "shí")):
        d = n // value % 10
        if d:
            if zero:
                parts.append("líng")
            parts.append(name if (value == 10 and d == 1 and n < 20) else f"{DIGITS[d]} {name}")
            zero = False
        elif parts:
            zero = True
    if n % 10:
        if zero:
            parts.append("líng")
        parts.append(DIGITS[n % 10])
    return " ".join(parts)


def without_erhua(word):
    """wánr -> wán, yīhuì'r -> yīhuì: the voice can't say the -r ending (erhua)."""
    word = re.sub(r"['’]r$", "", word)
    if word.endswith("r") and syllables_of(word) is None and syllables_of(word[:-1]):
        return word[:-1]
    return word


def spoken_pinyin(py):
    """The Pinyin as the voice should say it: without the A:/B: labels, numbers in words,
    no -r endings."""
    py = re.sub(r"(^|\n)[AB]:\s*", r"\1", py)
    py = re.sub(r"\d+", lambda m: number_pinyin(int(m.group())), py)
    py = re.sub(r"[^\W\d_]+(?:['’][^\W\d_]+)*", lambda m: without_erhua(m.group()), py)
    return py.replace("\n", " ")


def to_mp3(samples, sr, out):
    import numpy as np
    import soundfile as sf
    samples = np.asarray(samples, dtype=np.float32)
    samples *= 0.9 / max(1e-6, np.abs(samples).max())
    samples = np.concatenate([np.zeros(int(sr * 0.15)), samples, np.zeros(int(sr * 0.25))])
    with tempfile.NamedTemporaryFile(suffix=".wav") as wav:
        sf.write(wav.name, samples, sr)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav.name, "-ac", "1",
                        "-af", "loudnorm=I=-18:TP=-1.5:LRA=11", "-ar", "22050", "-b:a", BITRATE, str(out)], check=True)


def cmd_audio(limit=None):
    build.TAKES = 3     # a whole sentence: 3 takes, the one whose tones measure best
    rows = load_data()
    manifest = load_manifest()
    todo = [r for r in rows if not (SF / f"{r[0]}.mp3").exists()]
    if limit:
        todo = todo[:limit]
    print(f"{len(todo)} sentences to make with the voice")
    if not todo:
        return
    SF.mkdir(parents=True, exist_ok=True)
    lexicon = build.CorpusLexicon()
    speaker = build.Speaker()
    for n, (nid, hz, py, _) in enumerate(todo, 1):
        item = {"kind": "sentence", "hanzi": re.sub(r"(^|\n)[AB]:\s*", r"\1", hz), "pinyin": spoken_pinyin(py)}
        try:
            toks = build.audio_tokens(item, lexicon)
        except ValueError as e:
            print(f"[{n}/{len(todo)}] {nid} {hz}: SKIPPED ({e})")
            continue
        heard = [s[2] for s in build.say_segments(item) if s[0] == "syl"]
        y, sr, method, score, _ = build.make_take(speaker, toks, lexicon, heard)
        to_mp3(y, sr, SF / f"{nid}.mp3")
        manifest[str(nid)] = {"from": "voice", "method": method, "score": None if score is None else round(score, 1)}
        print(f"[{n}/{len(todo)}] {nid} {hz.replace(chr(10), ' ')}  ({method})", flush=True)
        if n % 25 == 0:
            save_manifest(manifest)
    save_manifest(manifest)


# --- words, meanings and the app data ----------------------------------------------

def load_cedict():
    """characters (simplified) -> [(numbered Pinyin, [meanings])], from CC-CEDICT (CC BY-SA 4.0)."""
    if not CEDICT.exists():
        build.CACHE.mkdir(exist_ok=True)
        print("Downloading CC-CEDICT…")
        z = build.CACHE / "cedict.zip"
        urllib.request.urlretrieve(CEDICT_URL, z)
        with zipfile.ZipFile(z) as f:
            CEDICT.write_bytes(f.read("cedict_ts.u8"))
        z.unlink()
    out = {}
    for line in CEDICT.open(encoding="utf-8"):
        m = re.match(r"(\S+) (\S+) \[([^\]]*)\] /(.*)/\s*$", line)
        if m:
            out.setdefault(m.group(2), []).append((m.group(3), m.group(4).split("/")))
    return out


SKIP_SENSE = re.compile(r"^(surname |(old |archaic |Japanese |unofficial |)variant of|see |CL:|used in |abbr\. for |"
                        r"also (written|pr\.) |erhua variant)")


REGISTER = re.compile(r"^\((slang|Internet slang|dialect|Cantonese|archaic|old|literary|Tw|Taiwan|loanword|onom|euphemism|vulgar|derog)")


def senses_of(senses, keep_all=False):
    """The senses worth showing: no surnames, variants or cross-references, no slang or
    dialect after the first; remarks in brackets dropped where the rest says enough
    ((bound form) individual -> individual)."""
    out = []
    for s in senses:
        if not keep_all and (SKIP_SENSE.match(s) or (out and REGISTER.match(s))):
            continue
        s = re.sub(r"\s*\[[^\]]*\]", "", re.sub(r"\S+\|(\S+)", r"\1", s))   # 長|长[chang2] -> 长
        bare = re.sub(r"\s*\([^()]*\)\s*", " ", s).strip(" ;,")
        bare = re.sub(r"\s+([,;:])", r"\1", bare)
        if not bare and s.startswith("(") and s.endswith(")"):
            bare = s[1:-1]          # (completed action marker) -> completed action marker
        for part in (bare or s).split("; "):
            if part and part not in out:
                out.append(part)
    return out


def gloss(senses):
    keep = senses_of(senses) or senses_of(senses, keep_all=True)
    text = ""
    for s in keep:
        if text and len(text) + len(s) > 40:
            break
        text = f"{text}; {s}" if text else s
    if len(text) > 50:
        cut = text[:50]
        text = cut[:max(cut.rfind("; "), cut.rfind(" "))].rstrip(";,( ") + "…"
    return text


def syllables_of(word):
    """'dǒupō' -> ['dǒu', 'pō'] (marks), or None if it isn't Pinyin."""
    try:
        segs = pinyin.parse(word)
    except ValueError:
        return None
    syl = [(b, t) for kind, *rest in segs if kind == "syl" for b, t in [rest]]
    return [pinyin.mark(b, t) for b, t in syl] or None


def numbered(syls):
    """['dǒu', 'pō'] -> 'dou3 po1' (CC-CEDICT style)."""
    out = []
    for s in syls:
        (b, t), = pinyin.syllables(pinyin.parse(s))
        out.append(b.replace("v", "u:") + str(t))
    return " ".join(out)


def marks(cedict_py):
    """'dou3 po1' -> 'dǒupō'"""
    out = []
    for s in cedict_py.split():
        m = re.match(r"([a-zA-Z:üÜ]+)([1-5])$", s)
        out.append(pinyin.mark(m.group(1).lower().replace("u:", "v").replace("ü", "v"), int(m.group(2))) if m else s.lower())
    return "".join(out)


class Words:
    def __init__(self):
        self.dic = load_cedict()
        self.longest = max(len(k) for k in self.dic)
        self.glosses = {}
        self.joined = set()     # words the deck writes as one Pinyin word somewhere

    def join(self, ws):
        """Two words the deck wrote apart here (yī qǐ) but as one word elsewhere (yìqǐ): one word."""
        out = []
        for w in ws:
            if out and out[-1][0] + w[0] in self.joined and out[-1][0] + w[0] in self.dic and len(out[-1][0]) == len(w[0]) == 1:
                h = out[-1][0] + w[0]
                out[-1] = self.word(h, [out[-1][1].lower(), w[1].lower()])
            else:
                out.append(w)
        return out

    def entry(self, hz, syls=None):
        """The CC-CEDICT entry for these characters, the one with this reading if there is one."""
        options = self.dic.get(hz)
        if not options:
            return None
        want = numbered(syls).lower() if syls else ""

        def score(option):
            py, senses = option
            return (py.lower() == want, py[:1].islower(), bool(senses_of(senses)),
                    re.sub(r"\d", "", py.lower()) == re.sub(r"\d", "", want), len(senses_of(senses)))
        return max(options, key=score)

    def cut(self, chars):
        """Longest CC-CEDICT words first: '我们爬上' -> ['我们', '爬上']"""
        out, i = [], 0
        while i < len(chars):
            for n in range(min(self.longest, len(chars) - i), 0, -1):
                if n == 1 or chars[i:i + n] in self.dic:
                    out.append(chars[i:i + n])
                    i += n
                    break
        return out

    def word(self, hz, syls):
        """(characters, Pinyin) of one word, and its meaning remembered under 'characters Pinyin'."""
        e = self.entry(hz, syls)
        py = "".join(syls) if syls else (marks(e[0]) if e else "")
        if e and e[0][:1].isupper():        # a name: 中国 Zhōngguó
            py = py[:1].upper() + py[1:]
        if e:
            self.glosses.setdefault(f"{hz} {py}", gloss(e[1]))
        return [hz, py]

    def split(self, hz, syls):
        """A Pinyin word's characters: one word if CC-CEDICT has it, else cut into words it has."""
        if len(hz) == 1 or hz in self.dic:
            return [self.word(hz, syls)]
        out, i = [], 0
        for part in self.cut(hz):
            out.append(self.word(part, syls[i:i + len(part)]))
            i += len(part)
        return out

    def sentence(self, hanzi, py):
        """The words of a sentence: [[characters, Pinyin], …] (no punctuation, names or numbers)."""
        hz_text = re.sub(r"(^|\n)[AB]:\s*", r"\1", hanzi)
        py_text = re.sub(r"(^|\n)[AB]:\s*", r"\1", py)
        units = UNIT.findall(hz_text)
        out, i = [], 0
        for w in PY_WORD.findall(py_text):
            if i < len(units) and not HANZI.match(units[i]):     # a name or number in both
                if units[i].lower() == w.lower():
                    i += 1
                    continue
                break
            syls = syllables_of(w)
            if not syls or i + len(syls) > len(units) or not all(HANZI.match(u) for u in units[i:i + len(syls)]):
                break
            hz = "".join(units[i:i + len(syls)])
            if len(hz) > 1:
                self.joined.add(hz)
            out += self.split(hz, syls)
            i += len(syls)
        else:
            if i == len(units):
                return self.join(out), True
        # the Pinyin doesn't line up: CC-CEDICT alone
        out = []
        for run in re.findall(r"[\u3400-\u9fff]+", hz_text):
            out += [self.word(part, None) for part in self.cut(run)]
        return out, False


def cmd_build():
    rows = load_data()
    manifest = load_manifest()
    words = Words()
    for _, hz, py, _ in rows:      # first: which words the deck writes as one
        words.sentence(hz, py)
    words.glosses = {}
    seen, out, loose = set(), [], 0
    for nid, hz, py, en in rows:
        ws, lined_up = words.sentence(hz, py)
        loose += not lined_up
        new = [k for k, (h, _) in enumerate(ws) if h not in seen and not seen.add(h)]
        x = {"id": nid, "hanzi": hz, "pinyin": py, "english": en, "words": ws, "new": new}
        try:
            x["numbers"] = pinyin.to_numbers(py)
        except ValueError:
            pass
        f = SF / f"{nid}.mp3"
        if f.exists():
            x["audio"] = f"sf/{nid}"
            x["v"] = build.audio_version(f"sf/{nid}")
            if manifest.get(str(nid), {}).get("from") == "voice":
                x["voice"] = 1
        out.append(x)
    data = {"about": f"Spoonfed Chinese ({DECK_URL}); meanings from CC-CEDICT (CC BY-SA 4.0, mdbg.net)",
            "glosses": dict(sorted(words.glosses.items()))}
    head = json.dumps(data, ensure_ascii=False, separators=(",", ":"))[:-1]
    APP_FILE.write_text(head + ",\n\"sentences\":[\n"
                        + ",\n".join(json.dumps(x, ensure_ascii=False, separators=(",", ":")) for x in out) + "\n]}\n")
    recs = sum(1 for x in out if "audio" in x)
    print(f"{len(out)} sentences -> {APP_FILE.relative_to(ROOT)} ({recs} with audio, "
          f"{sum(1 for x in out if x.get('voice'))} of them made by the voice; "
          f"{loose} cut into words without the Pinyin; {len(words.glosses)} words)")
    write_words(build.word_cards(build.load_words()))


# --- the Words tab: the deck's words in the order they are new in it -----------------

def sw_id(hanzi):
    """Audio id of a deck word: sw/ plus its characters as hex code points."""
    return "sw/" + "-".join(f"{ord(c):x}" for c in hanzi)


def deck_words():
    """[(characters, Pinyin, sentence, place of the word in it)] for each word of the
    deck, at the sentence where it is new, in the deck's order."""
    d = json.loads(APP_FILE.read_text())
    return d, [(x["words"][k][0], x["words"][k][1], x, k) for x in d["sentences"] for k in x["new"]]


LETTER = r"[^\W\d_]"


def syllable_spans(py):
    """Where each syllable of a Pinyin text is ([start, end] each), or None if it isn't all Pinyin."""
    spans = []
    for m in re.finditer(r"[^\W\d_]+", py):
        if m.group() in ("A", "B") and py[m.end():m.end() + 1] == ":":     # a dialogue's speaker
            continue
        letters, _ = pinyin._letters_and_tones(m.group())
        parts = pinyin._split_word(letters)
        if parts is None or len(letters) != len(m.group()):
            return None
        pos = m.start()
        for part in parts:
            spans.append((pos, pos + len(part)))
            pos += len(part)
    return spans


def sentence_mark(x, k):
    """Where the k-th word of a sentence is: [start, end] in the characters and
    [start, end] in the Pinyin (None, None where the Pinyin can't be lined up)."""
    hz, py = x["hanzi"], x["pinyin"]
    a = -1
    for h, _ in x["words"][:k + 1]:
        a = hz.find(h, a + 1)
        if a < 0:
            return None
    h, p = x["words"][k]
    spans = syllable_spans(py)
    if spans and len(spans) == len(HANZI.findall(hz)):
        first = len(HANZI.findall(hz[:a]))
        return [a, a + len(h), spans[first][0], spans[first + len(h) - 1][1]]
    # numbers or names in it: the word's Pinyin as it's written
    m = re.compile(rf"(?<!{LETTER}){re.escape(p)}(?!{LETTER})", re.I).search(py)
    return [a, a + len(h), m.start() if m else None, m.end() if m else None]


def word_audio_item(h, p):
    """What the voice says for a deck word (the item for build.audio_tokens)."""
    return {"kind": "sentence", "hanzi": h, "pinyin": without_erhua(p.lower())}


def cmd_words_audio(limit=None, part=None):
    """Recordings of the deck's words that aren't in data/words.json (those have
    their own), made by the voice, in docs/audio/sw/. part = (k, n): only every
    n-th word from the k-th, so n of these can run at once."""
    build.TAKES = 5
    curated = {w["hanzi"] for w in build.load_words().values()}
    _, words = deck_words()
    manifest = json.loads(SW_MANIFEST.read_text()) if SW_MANIFEST.exists() else {}
    todo = [(h, p) for h, p, _, _ in words if h not in curated and not (build.AUDIO / f"{sw_id(h)}.mp3").exists()
            and sw_id(h)[3:] not in manifest]
    if part:
        todo = todo[part[0]::part[1]]
    if limit:
        todo = todo[:limit]
    print(f"{len(todo)} words to make with the voice", flush=True)
    if not todo:
        return
    SW.mkdir(parents=True, exist_ok=True)
    lexicon = build.CorpusLexicon()
    speaker = build.Speaker()
    made = {}

    def save():
        # several of these may run at once: merge with what's on disk
        m = json.loads(SW_MANIFEST.read_text()) if SW_MANIFEST.exists() else {}
        m.update(made)
        SW_MANIFEST.write_text(json.dumps(dict(sorted(m.items())), ensure_ascii=False, indent=0) + "\n")

    for n, (h, p) in enumerate(todo, 1):
        key = sw_id(h)[3:]
        item = word_audio_item(h, p)
        try:
            toks = build.audio_tokens(item, lexicon)
            syl = [t for t in toks if t[0].isalpha()]
            bad = [t for t in syl if t[-1].isdigit() and not lexicon.trained(t)]
            if len(syl) > 1 and bad:
                raise ValueError(f"the voice never learned {', '.join(bad)}")
            heard = [s[2] for s in build.say_segments(item) if s[0] == "syl"]
            y, sr, method, score, _ = build.make_take(speaker, toks, lexicon, heard)
        except (ValueError, KeyError, SystemExit) as e:
            made[key] = {"hanzi": h, "skipped": str(e)}
            print(f"[{n}/{len(todo)}] {h} {p}: SKIPPED ({e})", flush=True)
            continue
        to_mp3(y, sr, build.AUDIO / f"{sw_id(h)}.mp3")
        made[key] = {"hanzi": h, "tokens": " ".join(toks), "method": method,
                     "score": None if score is None else round(score, 1)}
        print(f"[{n}/{len(todo)}] {h} {p}  ({method})", flush=True)
        if n % 25 == 0:
            save()
    save()


def write_words(curated):
    """docs/words.json for the Words tab: every word of the deck, in the order it is new
    in the deck, with the sentence it is new in (its id: the app takes the sentence from
    docs/spoonfed.json) and where it is in it; then the words of data/words.json that
    aren't in the deck. A word that is also in data/words.json keeps its meaning, notes
    and recording from there."""
    if not APP_FILE.exists():
        return
    d, words = deck_words()
    by = {c["hanzi"]: c for c in curated}
    made = json.loads(SW_MANIFEST.read_text()) if SW_MANIFEST.exists() else {}
    out, missing, no_audio = [], 0, 0
    for h, p, x, k in words:
        if h in by:
            card = {key: v for key, v in by[h].items() if key not in ("example", "parts")}
        else:
            card = {"hanzi": h, "pinyin": p, "english": d["glosses"].get(f"{h} {p}", "")}
            try:
                card["numbers"] = pinyin.to_numbers(p)
            except ValueError:
                pass
            f = build.AUDIO / f"{sw_id(h)}.mp3"
            if f.exists():
                card["audio"], card["v"] = sw_id(h), build.audio_version(sw_id(h))
                if made.get(sw_id(h)[3:], {}).get("method") == "best-effort":
                    card["audio_note"] = "The recording may not have every tone right: go by the Pinyin."
            else:
                no_audio += 1
            missing += not card["english"]
        card["sf"] = x["id"]
        mark = sentence_mark(x, k)
        if mark:
            card["mark"] = mark
        out.append(card)
    in_deck = {c["hanzi"] for c in out}
    out += [c for c in curated if c["hanzi"] not in in_deck]
    # what each character means, where it's a word of its own with a recording
    single = {c["hanzi"]: c for c in out if len(c["hanzi"]) == 1 and c.get("audio")}
    for c in out:
        if len(c["hanzi"]) > 1 and "parts" not in c:
            parts = [{"hanzi": ch, "pinyin": single[ch]["pinyin"], "english": build.short_gloss(single[ch]["english"]),
                      "audio": single[ch]["audio"], "v": single[ch]["v"]} for ch in c["hanzi"] if ch in single]
            if parts:
                c["parts"] = parts
    WORDS_FILE.write_text("{\"words\":[\n" + ",\n".join(json.dumps(c, ensure_ascii=False, separators=(",", ":"))
                                                     for c in out) + "\n]}\n")
    print(f"Words: {len(out)} ({len(words)} from the deck, {len(out) - len(words)} only in data/words.json; "
          f"{no_audio} without a recording yet, {missing} without a meaning)")


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    if args[0] == "import" and len(args) >= 2:
        cmd_import(args[1], force="--force" in args)
    elif args[0] == "audio":
        cmd_audio(int(args[args.index("--limit") + 1]) if "--limit" in args else None)
    elif args[0] == "words-audio":
        part = tuple(map(int, args[args.index("--part") + 1].split("/"))) if "--part" in args else None
        cmd_words_audio(int(args[args.index("--limit") + 1]) if "--limit" in args else None, part)
    elif args[0] == "build":
        cmd_build()
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
