"""Build the course: check the data, generate audio, write the flashcard data.

    python tools/build.py            # check + audio + cards
    python tools/build.py check      # only check data and lessons
    python tools/build.py audio      # (re)generate changed audio
    python tools/build.py cards      # write docs/cards.json

Audio comes from an offline Mandarin TTS model (Matcha-TTS trained on the Baker
corpus, run with sherpa-onnx). The model is fed Pinyin syllables directly, so
the audio follows the Pinyin in the data exactly, including neutral tones and
the spoken tone changes from pinyin.spoken().
"""

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

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
LESSONS = ROOT / "lessons"
DOCS = ROOT / "docs"
AUDIO = DOCS / "audio"
CACHE = Path(__file__).parent / ".cache"

RELEASES = "https://github.com/k2-fsa/sherpa-onnx/releases/download"
MODEL_DIR = CACHE / "matcha-icefall-zh-baker"
VOCODER = CACHE / "vocos-22khz-univ.onnx"


def load_course():
    course = json.loads((DATA / "course.json").read_text())
    lessons = []
    for entry in course["lessons"]:
        data = json.loads((DATA / f"{entry['id']}.json").read_text())
        lessons.append({**entry, "items": data["items"]})
    return lessons


def say_segments(item):
    """What the audio says: the "say" override, or the Pinyin with tone changes."""
    if "say" in item:
        return pinyin.parse_numbers(item["say"])
    return pinyin.spoken(pinyin.parse(item["pinyin"]))


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
        neutral_counts = {}
        for line in (MODEL_DIR / "lexicon.txt").open(encoding="utf-8"):
            word, *toks = line.split()
            if len(toks) == len(word):
                self.words[word] = toks
            for t in toks:
                if t.isalpha():
                    neutral_counts[t] = neutral_counts.get(t, 0) + 1
        self.rare = lambda base: neutral_counts.get(base, 0) < self.RARE

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
    segments = say_segments(item)
    syl = [i for i, s in enumerate(segments) if s[0] == "syl"]
    chars = [c for c in item["hanzi"] if "\u4e00" <= c <= "\u9fff"]
    if "say" not in item and len(chars) == len(syl):
        segments = list(segments)
        for i, label in zip(syl, lexicon.labels(chars)):
            _, base, tone = segments[i]
            if tone == 5 and lexicon.rare(base) and label and label[:-1] == base:
                segments[i] = ("syl", base, int(label[-1]))
    return pinyin.tts_tokens(segments)


# --- check -------------------------------------------------------------------

def check(lessons):
    errors = []
    ids = set()
    known_pinyin = set()
    for lesson in lessons:
        lid = lesson["id"]
        md = LESSONS / lesson["file"]
        if not md.exists():
            errors.append(f"{lid}: lesson file {md.name} missing")
            continue
        text = md.read_text()
        for item in lesson["items"]:
            where = f"{lid}/{item.get('id')}"
            for field in ("id", "kind", "pinyin", "english", "hanzi"):
                if field not in item:
                    errors.append(f"{where}: missing {field!r}")
            if item["id"] in ids:
                errors.append(f"{where}: duplicate id")
            ids.add(item["id"])
            if not item["id"].startswith(lid + "-"):
                errors.append(f"{where}: id should start with {lid}-")
            try:
                pinyin.tts_tokens(say_segments(item))
            except ValueError as e:
                errors.append(f"{where}: {e}")
            if item["pinyin"] not in text:
                errors.append(f"{where}: {item['pinyin']!r} doesn't appear in {md.name}")
            known_pinyin.add(item["pinyin"])

    # Tone numbers shown in lessons must match the tone marks.
    for md in sorted(LESSONS.glob("[!_]*.md")):
        for m in re.finditer(r"\*\*([^*]+)\*\*<br><sub>([^<]+)</sub>", md.read_text()):
            marks, numbers = m.groups()
            if pinyin.to_numbers(marks) != numbers:
                errors.append(f"{md.name}: {marks!r} shown as {numbers!r}, "
                              f"expected {pinyin.to_numbers(marks)!r}")
            if marks not in known_pinyin:
                errors.append(f"{md.name}: {marks!r} isn't in any data file")
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

    def to_mp3(self, tokens, out):
        import numpy as np
        import soundfile as sf
        audio = self.tts.generate("".join(self.char[t] for t in tokens), sid=0, speed=1.0)
        samples = np.array(audio.samples, dtype=np.float32)
        samples *= 0.9 / max(1e-6, np.abs(samples).max())
        sr = audio.sample_rate
        samples = np.concatenate([np.zeros(int(sr * 0.15)), samples, np.zeros(int(sr * 0.25))])
        with tempfile.NamedTemporaryFile(suffix=".wav") as wav:
            sf.write(wav.name, samples, sr)
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav.name,
                            "-ac", "1", "-b:a", "48k", str(out)], check=True)


def build_audio(lessons, force=False):
    AUDIO.mkdir(parents=True, exist_ok=True)
    manifest_path = AUDIO / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    lexicon = CorpusLexicon()
    wanted = {}
    for lesson in lessons:
        for item in lesson["items"]:
            wanted[item["id"]] = " ".join(audio_tokens(item, lexicon))

    todo = [i for i, toks in wanted.items()
            if force or manifest.get(i) != toks or not (AUDIO / f"{i}.mp3").exists()]
    speaker = Speaker() if todo else None
    for n, item_id in enumerate(todo, 1):
        tokens = wanted[item_id].split()
        print(f"[{n}/{len(todo)}] {item_id}: {wanted[item_id]}")
        speaker.to_mp3(tokens, AUDIO / f"{item_id}.mp3")
        manifest[item_id] = wanted[item_id]

    for f in AUDIO.glob("*.mp3"):  # remove audio for deleted items
        if f.stem not in wanted:
            f.unlink()
    manifest = {k: v for k, v in sorted(manifest.items()) if k in wanted}
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=1) + "\n")
    print(f"Audio: {len(todo)} generated, {len(wanted)} total.")


# --- cards -------------------------------------------------------------------

def build_cards(lessons):
    out = {"lessons": [], "items": []}
    for lesson in lessons:
        out["lessons"].append({k: lesson[k] for k in ("id", "title", "file")})
        for item in lesson["items"]:
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
                "id": item["id"],
                "lesson": lesson["id"],
                "kind": item["kind"],
                "pinyin": item["pinyin"],
                "numbers": pinyin.to_numbers(item["pinyin"]),
                "english": item["english"],
                # [base, tone, word break before] per syllable; the tone quiz
                # only uses items whose audio has the same tones as the writing
                "syllables": [[b.replace("v", "ü"), t, br] for (b, t), br in zip(written, breaks)],
                "heardAsWritten": written == heard,
            }
            for key in ("literal", "note", "audio_note"):
                if key in item:
                    card[key] = item[key]
            out["items"].append(card)
    DOCS.mkdir(exist_ok=True)
    (DOCS / "cards.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    print(f"Cards: {len(out['items'])} items from {len(lessons)} lessons.")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    lessons = load_course()
    errors = check(lessons)
    for e in errors:
        print("ERROR", e)
    if errors:
        sys.exit(1)
    print("Check: OK")
    if cmd in ("all", "audio"):
        build_audio(lessons, force="--force" in sys.argv)
    if cmd in ("all", "cards"):
        build_cards(lessons)


if __name__ == "__main__":
    main()
