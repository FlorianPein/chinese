"""Build the course: check the lessons, generate audio, write the app data.

    python tools/build.py            # check + audio + cards + lesson notes
    python tools/build.py check      # only check the data
    python tools/build.py audio      # (re)generate missing or changed audio
    python tools/build.py cards      # write docs/cards.json and lessons/*.md
    python tools/build.py audio --force   # regenerate all audio

Everything this writes (audio, docs/cards.json, lessons/*.md) is committed, so
nothing has to be generated when a lesson is started.

Audio comes from an offline Mandarin TTS model (Matcha-TTS trained on the Baker
corpus, run with sherpa-onnx). The model is fed Pinyin syllables directly, so
the audio follows the Pinyin in the data exactly, including neutral tones and
the spoken tone changes from pinyin.spoken().

The model sometimes gets a tone wrong, mostly for syllables that are rare in
that tone (hě, bū). So every take is checked: its pitch is measured and
compared with the tone shapes it should have. Up to TAKES takes are made and
the best is kept. If no take of a single syllable is right, a good take of the
same syllable in another tone is pitch-edited into the right tone shape.

Some syllables never occur in a tone in the training corpus (fō, fǒ, fò, dě,
tē, cē, …). The model has never heard those tokens, so it says something else
entirely (fō comes out close to jiē). A syllable alone in such a tone is always
made by pitch-editing the same syllable in its best-trained tone (fó -> fō);
words and phrases must not use such tokens at all (the build stops).
"""

import hashlib
import json
import re
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pinyin  # noqa: E402
from chart import Chart  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
LESSONS = ROOT / "lessons"
DOCS = ROOT / "docs"
AUDIO = DOCS / "audio"
CACHE = Path(__file__).parent / ".cache"
APP_URL = "https://florianpein.github.io/chinese/"

RELEASES = "https://github.com/k2-fsa/sherpa-onnx/releases/download"
MODEL_DIR = CACHE / "matcha-icefall-zh-baker"
VOCODER = CACHE / "vocos-22khz-univ.onnx"

# Tones are never taught or tested apart: every chart and tone question has all
# four, so they can always be compared.
ALL_TONES = [1, 2, 3, 4]
TONE_NAMES = {1: "1st tone", 2: "2nd tone", 3: "3rd tone", 4: "4th tone", 5: "neutral tone"}
SOUND_ID = re.compile(r"^s-([a-zv]+)([1-5])$")
EXERCISES = {"hear", "tone", "same", "audio", "meaning", "pinyin", "match", "build", "type"}
# rough seconds per step, for the time estimate
SECONDS = {"intro": 35, "chart": 40, "new": 20, "hear": 10, "tone": 8, "same": 10, "audio": 15,
           "meaning": 10, "pinyin": 10, "match": 30, "build": 20, "type": 15, "speak": 25}


# --- loading -----------------------------------------------------------------

def sound_item(sid, lesson_id, label=""):
    base, tone = SOUND_ID.match(sid).groups()
    return {"id": sid, "kind": "sound", "pinyin": pinyin.mark(base, int(tone)),
            "english": label, "lesson": lesson_id}


def chart_ids(step):
    """Sound ids of a chart step: every syllable in every tone shown."""
    return [f"s-{b.replace('ü', 'v')}{t}" for b in step["syllables"] for t in step["tones"]]


def step_refs(step):
    """Item and sound ids a step refers to (not counting answer options that are plain Pinyin)."""
    refs = []
    for key in ("item", "play"):
        if key in step:
            refs.append(step[key])
    if step["type"] in ("meaning", "audio"):
        refs += step.get("options", [])
    refs += step.get("items", [])
    refs += step.get("pair", [])
    for row in step.get("rows", []):
        refs += row
    if step["type"] == "chart":
        refs += chart_ids(step)
    return refs


def load_course():
    """Topics, the built lessons (those with a data file), all items, and the
    plan: every lesson of the course, built or not, in order."""
    course = json.loads((DATA / "course.json").read_text())
    chart = Chart(course)
    topics, lessons, items, plan = [], [], {}, []
    for topic in course["topics"]:
        topics.append({"id": topic["id"], "title": topic["title"],
                       "lessons": [l["id"] for l in topic["lessons"]]})
        for entry in topic["lessons"]:
            lid = entry["id"]
            path = DATA / f"{lid}.json"
            planned = {**entry, "topic": topic["id"], "built": path.exists(),
                       "tones": entry.get("tones", []), "words": entry.get("words", [])}
            plan.append(planned)
            if not path.exists():
                continue
            data = json.loads(path.read_text())
            lesson = {"id": lid, "topic": topic["id"], "title": entry["title"], "focus": entry["focus"],
                      "goal": data["goal"], "file": f"{lid}.md", "steps": data["steps"], "own": []}
            for item in data["items"]:
                item = {**item, "lesson": lid}
                if item["id"] in items:
                    raise SystemExit(f"ERROR {lid}: item id {item['id']!r} is already used "
                                     f"in {items[item['id']]['lesson']}")
                items[item["id"]] = item
                lesson["own"].append(item["id"])
            # sounds: every s-… id the steps use, plus every new one-syllable
            # word in all four tones
            labels = data.get("sounds", {})
            wanted = [r for s in data["steps"] for r in step_refs(s) if r.startswith("s-")]
            for s in data["steps"]:
                if s["type"] == "new" and s["item"] in items:
                    syl = pinyin.syllables(pinyin.parse(items[s["item"]]["pinyin"]))
                    if len(syl) == 1:
                        wanted += [f"s-{syl[0][0]}{t}" for t in (1, 2, 3, 4)]
            for sid in wanted:
                if not SOUND_ID.match(sid):
                    raise SystemExit(f"ERROR {lid}: {sid!r} isn't a sound id like s-ma1")
                if sid not in items:
                    items[sid] = sound_item(sid, lid, labels.get(sid, ""))
                    lesson["own"].append(sid)
            lessons.append(lesson)
    return chart, topics, lessons, items, plan


def tiles(text):
    """'Hǎo, wǒ hē.' -> ['hǎo', 'wǒ', 'hē'] (the word tiles of a build exercise)."""
    words = re.findall(r"[^\s,.!?:;，。！？：；]+", text)
    return [w[:1].lower() + w[1:] for w in words]


def say_segments(item):
    """What the audio says: the "say" override, or the Pinyin with tone changes."""
    if "say" in item:
        return pinyin.parse_numbers(item["say"])
    return pinyin.spoken(pinyin.parse(item["pinyin"]))


# --- check -------------------------------------------------------------------

def check(lessons, items):
    errors, warnings = [], []
    known = set()           # vocabulary introduced so far (by "new" steps)
    known_pinyin = set()

    def pin(x):
        return pinyin.to_numbers(x).lower()

    for lesson in lessons:
        lid = lesson["id"]
        for iid in lesson["own"]:
            item = items[iid]
            if item["kind"] == "sound":
                continue
            for field in ("id", "kind", "pinyin", "english", "hanzi"):
                if field not in item:
                    errors.append(f"{lid}/{iid}: missing {field!r}")
            if item["kind"] not in ("word", "phrase"):
                errors.append(f"{lid}/{iid}: kind should be word or phrase")
            try:
                pinyin.tts_tokens(say_segments(item))
            except ValueError as e:
                errors.append(f"{lid}/{iid}: {e}")
        introduced = [s["item"] for s in lesson["steps"] if s["type"] == "new"]
        for iid in lesson["own"]:
            if items[iid]["kind"] != "sound" and introduced.count(iid) != 1:
                errors.append(f"{lid}/{iid}: needs exactly one 'new' step (has {introduced.count(iid)})")

        for n, step in enumerate(lesson["steps"], 1):
            where = f"{lid} step {n} ({step.get('type')})"
            t = step.get("type")
            for ref in step_refs(step):
                if ref not in items:
                    errors.append(f"{where}: unknown item {ref!r}")
                elif items[ref]["kind"] != "sound" and ref not in known and not (t == "new" and ref == step["item"]):
                    errors.append(f"{where}: {ref!r} is used before its 'new' step")
            if any(r not in items for r in step_refs(step)):
                continue
            opts = step.get("options", [])
            if len(opts) != len(set(map(str, opts))):
                errors.append(f"{where}: duplicate options")
            if t == "intro":
                if "title" not in step or "text" not in step:
                    errors.append(f"{where}: needs title and text")
            elif t == "chart":
                if "title" not in step or not step.get("syllables") or not step.get("tones"):
                    errors.append(f"{where}: needs title, syllables and tones")
                elif step["tones"] != ALL_TONES:
                    errors.append(f"{where}: a chart shows all four tones, so they can be compared")
            elif t == "same":
                if len(step.get("pair", [])) != 2 or any(items[r]["kind"] != "sound" for r in step["pair"]):
                    errors.append(f"{where}: 'pair' must be two sounds")
            elif t == "audio":
                if step["item"] not in opts:
                    errors.append(f"{where}: options don't include {step['item']!r}")
                if len({items[o]["pinyin"] for o in opts}) != len(opts):
                    errors.append(f"{where}: two options sound the same")
            elif t == "new":
                item = items[step["item"]]
                if item["lesson"] != lid:
                    errors.append(f"{where}: {item['id']!r} belongs to {item['lesson']}")
                known.add(item["id"])
                if item["kind"] == "word":
                    known_pinyin.add(pin(item["pinyin"]))
                else:
                    for w in tiles(item["pinyin"]):
                        if pin(w) not in known_pinyin:
                            warnings.append(f"{where}: phrase word {w!r} hasn't been taught as a word")
            elif t == "hear":
                right = items[step["play"]]["pinyin"]
                if right not in opts:
                    errors.append(f"{where}: options don't include {right!r}")
                for o in opts:
                    try:
                        pinyin.parse(o)
                    except ValueError as e:
                        errors.append(f"{where}: {e}")
            elif t == "tone":
                item = items[step["play"]]
                syl = pinyin.syllables(pinyin.parse(item["pinyin"]))
                if len(syl) != 1 or syl != pinyin.syllables(say_segments(item)):
                    errors.append(f"{where}: tone steps need a one-syllable item heard as written")
                elif syl[0][1] not in opts:
                    errors.append(f"{where}: options don't include tone {syl[0][1]}")
                elif syl[0][1] != 5 and sorted(opts) != ALL_TONES:
                    errors.append(f"{where}: tone questions offer all four tones")
            elif t == "meaning":
                if step["item"] not in opts:
                    errors.append(f"{where}: options don't include {step['item']!r}")
                if step.get("from") not in ("audio", "pinyin"):
                    errors.append(f"{where}: 'from' must be audio or pinyin")
                english = [items[o]["english"] for o in opts]
                if len(set(english)) != len(english):
                    errors.append(f"{where}: two options have the same meaning")
            elif t == "pinyin":
                if items[step["item"]]["pinyin"] not in opts:
                    errors.append(f"{where}: options don't include {items[step['item']]['pinyin']!r}")
            elif t == "match":
                its = [items[i] for i in step["items"]]
                if not 2 <= len(its) <= 5:
                    errors.append(f"{where}: match needs 2–5 items")
                for key in ("pinyin",) if step.get("mode") == "sound" else ("pinyin", "english"):
                    if len({i[key] for i in its}) != len(its):
                        errors.append(f"{where}: two items have the same {key}")
            elif t == "build":
                words = tiles(items[step["item"]]["pinyin"])
                if set(step.get("extra", [])) & set(words):
                    errors.append(f"{where}: an extra tile is part of the answer")
                if len(words) < 2:
                    errors.append(f"{where}: build needs at least 2 words")
            elif t == "type":
                if step.get("from") not in ("audio", "english"):
                    errors.append(f"{where}: 'from' must be audio or english")
            elif t == "speak":
                pass
            else:
                errors.append(f"{where}: unknown step type")
    return errors, warnings


def check_plan(chart, plan, items):
    """The chart side of the course: every chart cell is taught exactly once,
    and words only use syllables and tones taught by then."""
    errors = []
    taught = {}
    known, tones = set(), set()
    for entry in plan:
        lid = entry["id"]
        for cell in entry["cells"]:
            try:
                syls = chart.syllables(cell)
            except ValueError as e:
                errors.append(f"{lid}: {e}")
                continue
            if not syls:
                errors.append(f"{lid}: chart cell {cell!r} has no syllables")
            if cell in taught:
                errors.append(f"{lid}: chart cell {cell!r} is already taught in {taught[cell]}")
            taught[cell] = lid
            known |= set(syls)
        tones |= set(entry["tones"])
        entry["known"], entry["known_tones"] = set(known), set(tones)
        if entry["built"]:
            words = [(i["id"], i["pinyin"]) for i in items.values() if i.get("lesson") == lid and i["kind"] != "sound"]
        else:
            words = [(w, w) for w in entry["words"]]
            if not 2 <= len(words) <= 5:
                errors.append(f"{lid}: plan 2–5 new words (has {len(words)})")
        for wid, text in words:
            for base, tone in pinyin.syllables(pinyin.parse(text)):
                if base not in known:
                    errors.append(f"{lid}/{wid}: {pinyin.mark(base, tone)!r} uses a syllable not taught yet")
                elif tone not in tones:
                    errors.append(f"{lid}/{wid}: {pinyin.mark(base, tone)!r} uses tone {tone} before it's taught")
    if plan and not set(ALL_TONES) <= set(plan[0]["tones"]):
        errors.append(f"{plan[0]['id']}: the first lesson teaches all four tones together")
    for cell in chart.all_cells():
        if cell not in taught:
            errors.append(f"chart cell {cell!r} ({' '.join(chart.syllables(cell))}) isn't in any lesson")
    covered = {s for c in chart.all_cells() for s in chart.syllables(c)}
    for s in sorted(pinyin.ALL_SYLLABLES - covered - chart.rare):
        errors.append(f"syllable {s!r} isn't in any chart cell (spelling rules in chart.py?)")
    return errors


# --- audio -------------------------------------------------------------------

def download_models():
    CACHE.mkdir(exist_ok=True)
    if not MODEL_DIR.exists():
        print("Downloading TTS model (~75 MB)…")
        tar = CACHE / "model.tar.bz2"
        urllib.request.urlretrieve(f"{RELEASES}/tts-models/matcha-icefall-zh-baker.tar.bz2", tar)
        with tarfile.open(tar) as t:
            t.extractall(CACHE, filter="data")
        tar.unlink()
    if not VOCODER.exists():
        print("Downloading vocoder (~55 MB)…")
        urllib.request.urlretrieve(f"{RELEASES}/vocoder-models/vocos-22khz-univ.onnx", VOCODER)


class CorpusLexicon:
    """The model's own lexicon (characters -> tokens), as used in its training.

    The training corpus mostly labels neutral tones with the full tone
    (谢谢 = xie4 xie4) although the speaker said them lightly, so neutral
    tokens like "xie" were hardly trained and sound garbled. For a neutral
    syllable whose neutral token is rare, the audio uses the corpus label for
    that character instead, which the model says with a natural, light tone.
    """
    RARE = 5

    def __init__(self):
        download_models()
        self.words = {}
        self.counts = {}    # token -> how many lexicon words use it
        for line in (MODEL_DIR / "lexicon.txt").open(encoding="utf-8"):
            word, *toks = line.split()
            if len(toks) == len(word):
                self.words[word] = toks
            for t in toks:
                self.counts[t] = self.counts.get(t, 0) + 1
        self.rare = lambda base: self.counts.get(base, 0) < self.RARE

    def trained(self, token):
        """Whether the model learned this token well enough to say it."""
        return self.counts.get(token, 0) >= self.RARE

    def best_tones(self, base):
        """The base's well-trained tones, most common first."""
        return sorted((t for t in (1, 2, 3, 4) if self.trained(f"{base}{t}")),
                      key=lambda t: -self.counts[f"{base}{t}"])

    def labels(self, chars):
        """Corpus token for each character (longest word match first)."""
        out, i = [], 0
        while i < len(chars):
            for n in range(min(10, len(chars) - i), 0, -1):
                word = "".join(chars[i:i + n])
                if word in self.words:
                    out += self.words[word]
                    i += n
                    break
            else:
                out.append(None)
                i += 1
        return out


def audio_tokens(item, lexicon):
    if item["kind"] == "sound":
        base, tone = SOUND_ID.match(item["id"]).groups()
        return [base + ("" if tone == "5" else tone), "."]
    segments = say_segments(item)
    syl = [i for i, s in enumerate(segments) if s[0] == "syl"]
    chars = [c for c in item["hanzi"] if "一" <= c <= "鿿"]
    if "say" not in item and len(chars) == len(syl):
        segments = list(segments)
        for i, label in zip(syl, lexicon.labels(chars)):
            _, base, tone = segments[i]
            if tone == 5 and lexicon.rare(base) and label and label[:-1] == base:
                segments[i] = ("syl", base, int(label[-1]))
    return pinyin.tts_tokens(segments)


# Tone checking. Pitch is measured in semitones above 200 Hz; this voice's
# high level (1st tone) is around 9, its low (3rd tone) around 0.

def pitch_track(samples, sr):
    import numpy as np
    import parselmouth
    snd = parselmouth.Sound(np.asarray(samples, dtype=np.float64), sampling_frequency=sr)
    p = snd.to_pitch(time_step=0.01, pitch_floor=75, pitch_ceiling=600)
    return p.xs(), p.selected_array["frequency"]


def voiced_runs(f0, gap=2, shortest=4):
    """Index ranges of voiced stretches (gaps of up to `gap` frames are bridged)."""
    runs, start, last = [], None, None
    for i, f in enumerate(f0):
        if f > 0:
            if start is None:
                start = i
            elif i - last > gap + 1:
                runs.append((start, last + 1))
                start = i
            last = i
    if start is not None:
        runs.append((start, last + 1))
    return [r for r in runs if r[1] - r[0] >= shortest]


def contour(f0):
    """Five median pitch values (semitones) across a voiced stretch."""
    import numpy as np
    st = 12 * np.log2(f0[f0 > 0] / 200)
    return [float(np.median(x)) for x in np.array_split(st, 5)]


def tone_margin(c, tone, alone):
    """How clearly a 5-point contour has the given tone (> 0: it does)."""
    s, e, lo, hi = c[0], c[-1], min(c), max(c)
    mean = sum(c) / 5
    if tone == 1:
        return min(3.0 - (hi - lo), mean - (7 if alone else 5))
    if tone == 2:
        return min(e - min(c[:3]) - 2.5, e - (7 if alone else 5))
    if tone == 3:
        if alone:
            return min(3.0 - min(c[:4]), 6.5 - max(c[:3]), 8 - e)
        return min(4.0 - min(c), 6.5 - max(c[:3]))
    if tone == 4:
        return min(max(c[:2]) - e - (4 if alone else 3), max(c[:2]) - (7.5 if alone else 6))
    return 0.0  # neutral: not checked


def tone_score(samples, sr, tones):
    """Smallest tone margin over the syllables, or None if the syllables
    can't be told apart in the pitch track."""
    _, f0 = pitch_track(samples, sr)
    if len(tones) == 1:
        return tone_margin(contour(f0), tones[0], True) if (f0 > 0).sum() >= 5 else None
    runs = voiced_runs(f0)
    if len(runs) != len(tones):
        return None
    margins = [tone_margin(contour(f0[a:b]), t, False) for (a, b), t in zip(runs, tones) if t != 5]
    return min(margins) if margins else 0.0


class Speaker:
    """Matcha TTS driven by model tokens. Each token gets a private-use
    character in a generated lexicon, so text in = exact tokens out."""

    def __init__(self):
        import sherpa_onnx
        download_models()
        tokens = [line.split()[0] for line in (MODEL_DIR / "tokens.txt").open()
                  if len(line.split()) == 2]
        self.char = {}
        lexicon = CACHE / "token-lexicon.txt"
        with lexicon.open("w") as f:
            for i, tok in enumerate(t for t in tokens if t[0].isalpha()):
                self.char[tok] = chr(0xE000 + i)
                f.write(f"{chr(0xE000 + i)} {tok}\n")
        self.char.update({p: p for p in ",.!?:"})
        config = sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(
            matcha=sherpa_onnx.OfflineTtsMatchaModelConfig(
                acoustic_model=str(MODEL_DIR / "model-steps-3.onnx"),
                vocoder=str(VOCODER),
                lexicon=str(lexicon),
                tokens=str(MODEL_DIR / "tokens.txt"),
            ),
            num_threads=4,
        ))
        self.tts = sherpa_onnx.OfflineTts(config)

    def say(self, tokens, speed=1.0):
        import numpy as np
        audio = self.tts.generate("".join(self.char[t] for t in tokens), sid=0, speed=speed)
        return np.array(audio.samples, dtype=np.float32), audio.sample_rate


TAKES = 9
GOOD = 0.6           # tone margin (semitones) a take needs to count as right
SPEED = {1: 0.9}     # single syllables a little slower: easier to hear the tone

# Target tone shapes for pitch editing, as (time 0–1, level 1–5) on the
# usual 5-level scale; level L is -1 + 2.6 * (L - 1) semitones above 200 Hz.
# A syllable said alone gets the full shape; inside a phrase the 3rd tone
# just stays low.
SHAPES = {1: [(0, 5), (1, 4.9)], 2: [(0, 3), (0.3, 2.8), (1, 5)],
          3: [(0, 2.3), (0.55, 1), (0.8, 1.2), (1, 3.3)], 4: [(0, 5.2), (1, 1.3)]}
SHAPES_IN_PHRASE = {**SHAPES, 2: [(0, 3), (0.3, 2.8), (1, 4.8)],
                    3: [(0, 2.2), (0.6, 1), (1, 1.3)], 4: [(0, 5), (1, 1.8)]}


def hz(level):
    return 200 * 2 ** ((-1 + 2.6 * (level - 1)) / 12)


def retone(samples, sr, tone):
    """Pitch-edit a one-syllable take into the given tone shape (PSOLA)."""
    import numpy as np
    import parselmouth
    from parselmouth.praat import call
    snd = parselmouth.Sound(np.asarray(samples, dtype=np.float64), sampling_frequency=sr)
    t, f0 = pitch_track(samples, sr)
    voiced = t[f0 > 0]
    t0, t1 = voiced[0], voiced[-1]
    manip = call(snd, "To Manipulation", 0.01, 75, 600)
    tier = call("Create PitchTier", "target", snd.xmin, snd.xmax)
    for x, level in SHAPES[tone]:
        call(tier, "Add point", t0 + x * (t1 - t0), hz(level))
    call([tier, manip], "Replace pitch tier")
    out = call(manip, "Get resynthesis (overlap-add)")
    return np.array(out.values[0], dtype=np.float32), sr


def fix_phrase(samples, sr, tones):
    """Pitch-edit only the syllables of a phrase whose tone came out wrong,
    keeping the rest of the take as it is. None if the syllables can't be
    found in the pitch track."""
    import numpy as np
    import parselmouth
    from parselmouth.praat import call
    t, f0 = pitch_track(samples, sr)
    runs = voiced_runs(f0)
    if len(runs) != len(tones):
        return None
    snd = parselmouth.Sound(np.asarray(samples, dtype=np.float64), sampling_frequency=sr)
    manip = call(snd, "To Manipulation", 0.01, 75, 600)
    tier = call(manip, "Extract pitch tier")
    for (a, b), tone in zip(runs, tones):
        if tone == 5 or tone_margin(contour(f0[a:b]), tone, False) > GOOD + 0.3:
            continue
        t0, t1 = t[a], t[b - 1]
        call(tier, "Remove points between", t0 - 0.006, t1 + 0.006)
        for x, level in SHAPES_IN_PHRASE[tone]:
            call(tier, "Add point", t0 + x * (t1 - t0), hz(level))
    call([tier, manip], "Replace pitch tier")
    out = call(manip, "Get resynthesis (overlap-add)")
    return np.array(out.values[0], dtype=np.float32), sr


def pitch_edit(speaker, base, tone, sources, speed):
    """Pitch-edit the clearest take of `base` in one of the source tones into
    `tone`. Returns (samples, sr, method, score, source token) or None."""
    takes = []
    for t in sources:
        for _ in range(TAKES):
            ys, srs = speaker.say([f"{base}{t}", "."], speed)
            m = tone_score(ys, srs, [t])
            if m is not None:
                takes.append((m, ys, srs, f"{base}{t}"))
    if not takes:
        return None
    _, ys, srs, src = max(takes, key=lambda s: s[0])
    y2, sr2 = retone(ys, srs, tone)
    return y2, sr2, "pitch-edited", tone_score(y2, sr2, [tone]), src


def make_take(speaker, tokens, lexicon):
    """Best of up to TAKES takes, pitch-edited if none has the right tones.
    Returns (samples, sr, method, score, source token if pitch-edited)."""
    tones = [int(t[-1]) if t[-1].isdigit() else 5 for t in tokens if t[0].isalpha()]
    base_speed = SPEED.get(len(tones), 1.0)
    if all(t == 5 for t in tones):
        y, sr = speaker.say(tokens, base_speed)
        return y, sr, "natural", None, None
    if len(tones) == 1:
        base = tokens[0].rstrip("12345")
        trained = lexicon.best_tones(base)
        if tones[0] not in trained:
            # never heard in training: only a pitch-edited take sounds right
            made = pitch_edit(speaker, base, tones[0], trained[:2], base_speed)
            if made is None:
                raise SystemExit(f"ERROR: no usable take of {base} in any tone")
            return made
    best = None
    for k in range(TAKES):
        y, sr = speaker.say(tokens, base_speed * (1.0, 0.92, 1.08)[k % 3])
        score = tone_score(y, sr, tones)
        key = -99 if score is None else score
        if best is None or key > best[0]:
            best = (key, y, sr, score)
        if score is not None and score > GOOD + 0.3:
            break
    key, y, sr, score = best
    if score is not None and score > GOOD:
        return y, sr, "natural", score, None
    if len(tones) == 1:
        # pitch-edit the clearest take of this syllable in a level or
        # falling tone (the easiest to pitch-edit), if trained, else any
        base = tokens[0].rstrip("12345")
        trained = lexicon.best_tones(base)
        sources = [t for t in (1, 4) if t in trained] or trained[:2]
        made = pitch_edit(speaker, base, tones[0], sources, base_speed)
        if made:
            return made
    elif score is not None:
        fixed = fix_phrase(y, sr, tones)
        if fixed:
            s2 = tone_score(*fixed, tones)
            if s2 is not None and s2 > score:
                return *fixed, "pitch-edited", s2, None
    return y, sr, "unchecked" if score is None else "best-effort", score, None


def to_mp3(samples, sr, out):
    import numpy as np
    import soundfile as sf
    samples = np.asarray(samples, dtype=np.float32)
    samples *= 0.9 / max(1e-6, np.abs(samples).max())
    samples = np.concatenate([np.zeros(int(sr * 0.15)), samples, np.zeros(int(sr * 0.25))])
    with tempfile.NamedTemporaryFile(suffix=".wav") as wav:
        sf.write(wav.name, samples, sr)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav.name,
                        "-ac", "1", "-b:a", "48k", str(out)], check=True)


def build_audio(items, force=False):
    AUDIO.mkdir(parents=True, exist_ok=True)
    manifest_path = AUDIO / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    manifest = {k: v for k, v in manifest.items() if isinstance(v, dict)}
    lexicon = CorpusLexicon()
    wanted = {iid: " ".join(audio_tokens(item, lexicon)) for iid, item in items.items()}
    untrained = []
    for iid, toks in wanted.items():
        syl = [t for t in toks.split() if t[0].isalpha()]
        bad = [t for t in syl if t[-1].isdigit() and not lexicon.trained(t)]
        if len(syl) > 1 and bad:
            untrained.append(f"ERROR {iid}: the voice never learned {', '.join(bad)}; "
                             "pick another word or add a \"say\" override")
    if untrained:
        raise SystemExit("\n".join(untrained))

    def stale(iid):
        made = manifest.get(iid, {})
        toks = wanted[iid].split()
        if made.get("tokens") != wanted[iid] or not (AUDIO / f"{iid}.mp3").exists():
            return True
        # single syllables made before untrained tokens were avoided: said
        # with an untrained token, or pitch-edited from one
        return (len(toks) == 2 and toks[0][-1].isdigit() and "from" not in made
                and (made["method"] == "pitch-edited" or not lexicon.trained(toks[0])))

    todo = [i for i in wanted if force or stale(i)]
    speaker = Speaker() if todo else None
    done = {}   # tokens -> id already made in this run (same sound, same file)
    for n, iid in enumerate(todo, 1):
        toks = wanted[iid]
        if toks in done:
            (AUDIO / f"{iid}.mp3").write_bytes((AUDIO / f"{done[toks]}.mp3").read_bytes())
            manifest[iid] = {**manifest[done[toks]]}
        else:
            y, sr, method, score, source = make_take(speaker, toks.split(), lexicon)
            to_mp3(y, sr, AUDIO / f"{iid}.mp3")
            manifest[iid] = {"tokens": toks, "method": method,
                             "score": None if score is None else round(score, 1)}
            if source:
                manifest[iid]["from"] = source
            done[toks] = iid
        m = manifest[iid]
        src = f" from {m['from']}" if "from" in m else ""
        print(f"[{n}/{len(todo)}] {iid}: {toks}  ({m['method']}{src}, {m['score']})")

    for f in AUDIO.glob("*.mp3"):  # remove audio for deleted items
        if f.stem not in wanted:
            f.unlink()
    manifest = {k: v for k, v in sorted(manifest.items()) if k in wanted}
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=1) + "\n")
    methods = {}
    for v in manifest.values():
        methods[v["method"]] = methods.get(v["method"], 0) + 1
    print(f"Audio: {len(todo)} generated, {len(wanted)} total {methods}.")
    for k, v in manifest.items():
        if v["method"] == "best-effort" or (v["score"] is not None and v["score"] <= GOOD):
            print(f"  WARNING {k}: no take had clearly the right tones (score {v['score']})")


# --- cards + lesson notes ----------------------------------------------------

def minutes(steps):
    return round(sum(SECONDS.get(s["type"], 15) for s in steps) / 60)


def cell_text(chart, cells):
    """['a:bpmf', 'a:none'] -> 'ba pa ma fa · a'; a recap lesson has no cells"""
    if not cells:
        return "recap, no new sounds"
    return " · ".join(" ".join(x.replace("v", "ü") for x in chart.syllables(c)) for c in cells)


def build_cards(chart, topics, lessons, items, plan):
    out = {"topics": topics, "plan": [], "lessons": [], "items": []}
    for entry in plan:
        out["plan"].append({k: entry[k] for k in ("id", "topic", "title", "focus", "built")}
                           | {"chart": cell_text(chart, entry["cells"])})
    for lesson in lessons:
        out["lessons"].append({k: lesson[k] for k in ("id", "topic", "title", "focus", "goal", "file", "steps")}
                              | {"minutes": minutes(lesson["steps"])})
    for lesson in lessons:
        for iid in lesson["own"]:
            item = items[iid]
            segments = pinyin.parse(item["pinyin"])
            written = pinyin.syllables(segments)
            heard = pinyin.syllables(say_segments(item))
            # 1 where a word break comes before the syllable
            breaks, gap = [], 0
            for s in segments:
                if s[0] == "syl":
                    breaks.append(gap)
                    gap = 0
                elif s[1] == " ":
                    gap = 1
            card = {
                "id": iid,
                "lesson": item["lesson"],
                "kind": item["kind"],
                "pinyin": item["pinyin"],
                "numbers": pinyin.to_numbers(item["pinyin"]),
                "english": item["english"],
                # [base, tone, word break before] per syllable; the tone quiz
                # only uses items whose audio has the same tones as the writing
                "syllables": [[b.replace("v", "ü"), t, br] for (b, t), br in zip(written, breaks)],
                "heardAsWritten": written == heard,
                # changes with the audio file, so browsers don't keep an old copy
                "v": hashlib.md5((AUDIO / f"{iid}.mp3").read_bytes()).hexdigest()[:8],
            }
            for key in ("literal", "note", "audio_note"):
                if key in item:
                    card[key] = item[key]
            out["items"].append(card)
    DOCS.mkdir(exist_ok=True)
    (DOCS / "cards.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    print(f"Cards: {len(out['items'])} items, {len(lessons)} lessons.")


def py(text):
    """Pinyin for the notes: tone marks, with tone numbers underneath."""
    return f"**{text}**<br><sub>{pinyin.to_numbers(text)}</sub>"


def chart_table(step):
    """A chart step as a Markdown table: syllables down, tones across."""
    head = "| | " + " | ".join(TONE_NAMES[t] for t in step["tones"]) + " |"
    rows = [head, "|---" * (len(step["tones"]) + 1) + "|"]
    for b in step["syllables"]:
        rows.append(f"| **{b}** | " + " | ".join(pinyin.mark(b.replace("ü", "v"), t) for t in step["tones"]) + " |")
    return rows


def build_notes(chart, topics, lessons, items, plan):
    """lessons/<id>.md: a readable summary of each lesson, generated from its data."""
    LESSONS.mkdir(exist_ok=True)
    order = [l["id"] for l in lessons]
    by_id = {e["id"]: e for e in plan}
    for lesson in lessons:
        lid = lesson["id"]
        entry = by_id[lid]
        i = order.index(lid)
        nav = []
        if i > 0:
            nav.append(f"**Previous:** [{order[i - 1]}]({order[i - 1]}.md)")
        if i + 1 < len(order):
            nav.append(f"**Next:** [{order[i + 1]}]({order[i + 1]}.md)")
        own = [items[x] for x in lesson["own"]]
        words = [x for x in own if x["kind"] == "word"]
        phrases = [x for x in own if x["kind"] == "phrase"]
        sounds = [x for x in own if x["kind"] == "sound"]
        counts = {}
        for s in lesson["steps"]:
            counts[s["type"]] = counts.get(s["type"], 0) + 1
        n_ex = sum(v for k, v in counts.items() if k in EXERCISES)
        new_tones = ", ".join(TONE_NAMES[t] for t in entry["tones"])

        md = [f"# {lid}: {lesson['title']}", "",
              f"> **Goal:** {lesson['goal']}", ">",
              f"> **Chart:** {cell_text(chart, entry['cells'])}" + (f" · **New tones:** {new_tones}" if new_tones else ""),
              ">",
              f"> **Do the lesson:** [in the app]({APP_URL}#lesson/{lid}) · "
              f"**Listen:** [all audio]({APP_URL}#listen/{lid}) · ~{minutes(lesson['steps'])} min · "
              f"{len(lesson['steps'])} steps, {n_ex} exercises",
              ">", f"> " + " · ".join(nav + [f"**Data:** [`data/{lid}.json`](../data/{lid}.json)",
                                            "**Chart:** [all lessons](../CHART.md)"]), "",
              f"<!-- Generated by tools/build.py from data/{lid}.json. Edit the data, not this file. -->", ""]
        md += ["## Explanations", ""]
        for s in lesson["steps"]:
            if s["type"] not in ("intro", "chart"):
                continue
            md += [f"### {s['title']}", ""]
            if s.get("text"):
                md += [s["text"], ""]
            if s["type"] == "chart":
                md += chart_table(s) + [""]
            for row in s.get("rows", []):
                md.append(" · ".join(f"**{items[r]['pinyin']}**" + (f" ({items[r]['english']})" if items[r]["english"] else "")
                                     for r in row) + "  ")
            if s.get("rows"):
                md.append("")
        if words:
            md += ["## New words", "", "| Pinyin | Meaning | Note |", "|--------|---------|------|"]
            md += [f"| {py(w['pinyin'])} | {w['english']} | {w.get('note', '')} |" for w in words]
            md.append("")
        if phrases:
            md += ["## New phrases", "", "| Pinyin | English | Literally |", "|--------|---------|-----------|"]
            md += [f"| {py(p['pinyin'])} | {p['english']} | {p.get('literal', '')} |" for p in phrases]
            md.append("")
        if sounds:
            groups = {}
            for s in sounds:
                groups.setdefault(SOUND_ID.match(s["id"]).group(1), []).append(s)
            md += ["## Sounds with audio", "",
                   "Every syllable this lesson plays, in each tone it uses. Play them on the "
                   f"[listening page]({APP_URL}#listen/{lid}).", ""]
            for base, group in groups.items():
                group.sort(key=lambda s: s["id"])
                md.append(f"- **{base.replace('v', 'ü')}**: " + " · ".join(s["pinyin"] for s in group))
            md.append("")
        reviewed = sorted({r for s in lesson["steps"] for r in step_refs(s)
                           if r in items and items[r]["kind"] != "sound" and items[r]["lesson"] != lid},
                          key=lambda r: list(items).index(r))
        if reviewed:
            md += ["## Repeated from earlier lessons", "",
                   ", ".join(f"**{items[r]['pinyin']}** ({items[r]['english']})" for r in reviewed), ""]
        kinds = {"hear": "pick what you hear", "tone": "name the tone", "same": "same or different?",
                 "audio": "pick the sound that matches the Pinyin", "meaning": "pick the meaning",
                 "pinyin": "pick the Pinyin", "match": "match pairs", "build": "build the sentence",
                 "type": "type the Pinyin", "speak": "say it aloud (record and compare)"}
        md += ["## Exercises", "", " · ".join(f"{counts[k]}× {v}" for k, v in kinds.items() if k in counts), ""]
        (LESSONS / f"{lid}.md").write_text("\n".join(md))
    for f in LESSONS.glob("[!_]*.md"):
        if f.stem not in order:
            f.unlink()
    print(f"Notes: {len(lessons)} lesson files.")


def load_progress():
    """data/progress.json: the lessons done so far, {"done": {"P01": "2026-10-19"}}."""
    path = DATA / "progress.json"
    return json.loads(path.read_text()).get("done", {}) if path.exists() else {}


def build_chart_page(chart, topics, plan, items):
    """CHART.md: the Pinyin chart with the lesson for every syllable, and the lesson order."""
    done = load_progress()
    lesson_of = {c: e["id"] for e in plan for c in e["cells"]}
    md = ["# The Pinyin chart", "",
          "<!-- Generated by tools/build.py from data/course.json. Edit the data, not this file. -->", "",
          "Every syllable of Mandarin, with the lesson that teaches it (the small number). "
          "**Bold** means you've done that lesson. Initials go down, finals go across, "
          "like the [Yabla chart](https://chinese.yabla.com/chinese-pinyin-chart.php).", "",
          f"{len(plan)} lessons · {sum(len(chart.syllables(c)) for c in chart.all_cells())} syllables · "
          f"{len(done)} lessons done · [lesson order](#lesson-order) · [words you've seen](WORDS.md)", ""]
    for family, finals in chart.families:
        md += [f"### {family}", "", "| | " + " | ".join(f"**{f}**" for f in finals) + " |",
               "|---" * (len(finals) + 1) + "|"]
        for gid, group in chart.groups.items():
            for ini in group["initials"]:
                cells = []
                for f in finals:
                    s = chart.cell(f, ini)
                    lid = lesson_of.get(f"{f}:{gid}")
                    if not s:
                        cells.append("")
                        continue
                    s = s.replace("v", "ü")
                    if lid in done:
                        s = f"**{s}**"
                    cells.append(f"{s}<sub>{int(lid[1:])}</sub>" if lid else s)
                if any(cells):
                    md.append(f"| **{ini or '–'}** | " + " | ".join(cells) + " |")
        md.append("")

    md += ["## Lesson order", "",
           "Each lesson teaches one or more blocks of the chart and 2–5 words that use only sounds you know by then. "
           "Early lessons take one block each, because everything is new. Later ones combine blocks once "
           "the initials and the type of final are familiar. Words of lessons that aren't built yet are "
           "*candidates* and may still change.", ""]
    tone_short = {1: "1st", 2: "2nd", 3: "3rd", 4: "4th", 5: "neutral"}
    for topic in topics:
        md += [f"### {topic['title']}", "",
               "| # | Syllables | New tones | Focus | Words | Status |", "|---|---|---|---|---|---|"]
        for e in (e for e in plan if e["topic"] == topic["id"]):
            lid = e["id"]
            if e["built"]:
                ws = ", ".join(f"{i['pinyin']} ({i['english']})" for i in items.values()
                               if i.get("lesson") == lid and i["kind"] == "word")
                status = f"✅ done {done[lid]}" if lid in done else f"[ready]({APP_URL}#lesson/{lid})"
                name = f"[{lid}](lessons/{lid}.md)"
            else:
                ws = "*" + ", ".join(e["words"]) + "*"
                status = "planned"
                name = lid
            tones = ", ".join(tone_short[t] for t in e["tones"])
            md.append(f"| {name} | {cell_text(chart, e['cells'])} | {tones} | {e['focus']} | {ws} | {status} |")
        md.append("")
    (ROOT / "CHART.md").write_text("\n".join(md))
    print("Chart: CHART.md")


def build_words_page(lessons, items):
    """WORDS.md: every word and phrase taught so far, and which ones you've seen."""
    done = load_progress()
    seen = [i for i in items.values() if i["kind"] != "sound" and i["lesson"] in done]
    waiting = [i for i in items.values() if i["kind"] != "sound" and i["lesson"] not in done]
    md = ["# Words", "",
          "<!-- Generated by tools/build.py from data/ and data/progress.json. Edit those, not this file. -->", "",
          "Every word and phrase from the lessons. A lesson's words count as **seen** once the lesson is "
          "marked done in `data/progress.json` (tell Claude *I finished P01*). "
          "The app keeps its own list under **Words**.", "",
          f"**Seen:** {sum(i['kind'] == 'word' for i in seen)} words, {sum(i['kind'] == 'phrase' for i in seen)} phrases · "
          f"**In ready lessons, not seen yet:** {sum(i['kind'] == 'word' for i in waiting)} words, "
          f"{sum(i['kind'] == 'phrase' for i in waiting)} phrases", ""]
    for lesson in lessons:
        lid = lesson["id"]
        own = [items[x] for x in lesson["own"] if items[x]["kind"] != "sound"]
        status = f"seen {done[lid]}" if lid in done else "not seen yet"
        md += [f"## [{lid}](lessons/{lid}.md): {lesson['title']} ({status})", "",
               "| Pinyin | Numbers | Meaning | Kind |", "|---|---|---|---|"]
        md += [f"| **{i['pinyin']}** | {pinyin.to_numbers(i['pinyin'])} | {i['english']} | {i['kind']} |" for i in own]
        md.append("")
    (ROOT / "WORDS.md").write_text("\n".join(md))
    print(f"Words: WORDS.md ({len(seen)} seen)")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    chart, topics, lessons, items, plan = load_course()
    errors, warnings = check(lessons, items)
    errors += check_plan(chart, plan, items)
    for w in warnings:
        print("WARNING", w)
    for e in errors:
        print("ERROR", e)
    if errors:
        sys.exit(1)
    print(f"Check: OK ({len(lessons)} lessons, {len(items)} items with audio)")
    for lesson in lessons:
        n_ex = sum(1 for s in lesson["steps"] if s["type"] in EXERCISES)
        print(f"  {lesson['id']}: {len(lesson['steps'])} steps, {n_ex} exercises, ~{minutes(lesson['steps'])} min")
    if cmd in ("all", "audio"):
        build_audio(items, force="--force" in sys.argv)
    if cmd in ("all", "cards"):
        build_cards(chart, topics, lessons, items, plan)
        build_notes(chart, topics, lessons, items, plan)
        build_chart_page(chart, topics, plan, items)
        build_words_page(lessons, items)


if __name__ == "__main__":
    main()
