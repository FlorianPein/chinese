"""Merge a "Copy progress for Claude" paste from the app into the repo.

    python tools/progress.py pasted.txt     # or: ... | python tools/progress.py
    python tools/progress.py --github       # what the app synced to the progress branch

- data/progress.json gets the lessons done (date, best score, times), which
  build.py uses for CHART.md. Pastes from different devices add
  up: a lesson recorded before is kept, even if this paste doesn't have it
- data/progress-log.jsonl gets every new log entry (finished lessons, wrong
  answers, practice rounds, batches of word flashcard answers), without duplicates
- data/progress.json also gets the latest word flashcard summary: how many
  words were seen, and how often each word was forgotten (Don't know), and
  the grammar sessions checked (date, best score, times)
- prints a summary of weak spots over the whole log, for PROGRESS.md

Run tools/build.py afterwards to update CHART.md.
"""

import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
PROGRESS = DATA / "progress.json"
LOG = DATA / "progress-log.jsonl"


def extract(text):
    m = re.search(r"```json\s*(\{.*?\})\s*```", text, re.S) or re.search(r'(\{"v":\s*1.*\})', text, re.S)
    if not m:
        sys.exit("No progress data found. Paste the whole text from 'Copy progress for Claude'.")
    return json.loads(m.group(1))


def from_github():
    """The file the app syncs to the progress branch (see README: Sync between devices)."""
    root = DATA.parent
    if subprocess.run(["git", "fetch", "-q", "origin", "progress"], cwd=root).returncode:
        sys.exit("No progress branch on GitHub yet: connect sync in the app first (README: Sync between devices).")
    synced = json.loads(subprocess.run(["git", "show", "FETCH_HEAD:progress.json"], cwd=root, check=True,
                                       capture_output=True, text=True).stdout)
    cards = synced.get("words", {})
    words = {"seen": len(cards),
             "forgotten": {w: c["lapses"] for w, c in cards.items() if c.get("lapses", 0) >= 2}}
    return {"copied": synced.get("updated", "")[:16].replace("T", " "),
            "lessons": synced.get("lessons", {}), "words": words, "grammar": synced.get("grammar", {}),
            "log": synced.get("log", [])}


def main():
    if sys.argv[1:] == ["--github"]:
        data = from_github()
    else:
        text = Path(sys.argv[1]).read_text(encoding="utf-8") if len(sys.argv) > 1 else sys.stdin.read()
        data = extract(text)

    progress = json.loads(PROGRESS.read_text()) if PROGRESS.exists() else {}
    # each device (phone, computer) keeps its own progress, so pastes are
    # merged with what's recorded, never replace it
    lessons = progress.get("lessons", {})
    for lid, st in data["lessons"].items():
        old = lessons.get(lid, {})
        merged = {**old, **st}
        for key, pick in (("done", min), ("last", max), ("best", max), ("times", max)):
            vals = [x[key] for x in (old, st) if x.get(key) is not None]
            if vals:
                merged[key] = pick(vals)
        lessons[lid] = merged
    progress["lessons"] = dict(sorted(lessons.items()))
    progress["done"] = {lid: st["done"] for lid, st in progress["lessons"].items()}
    if data.get("words", {}).get("seen"):
        # the newest summary wins: a word's lapses only grow
        old_words = progress.get("words", {})
        forgotten = {**old_words.get("forgotten", {})}
        for w, n in data["words"].get("forgotten", {}).items():
            forgotten[w] = max(n, forgotten.get(w, 0))
        progress["words"] = {"seen": max(data["words"]["seen"], old_words.get("seen", 0)),
                             "forgotten": dict(sorted(forgotten.items(), key=lambda kv: -kv[1]))}
    grammar = progress.get("grammar", {})
    for gid, st in data.get("grammar", {}).items():
        old = grammar.get(gid, {})
        merged = {k: v for k, v in {**old, **st}.items() if k != "at"}
        for key, pick in (("done", min), ("last", max), ("best", max), ("times", max)):
            vals = [x[key] for x in (old, st) if x.get(key) is not None]
            if vals:
                merged[key] = pick(vals)
        grammar[gid] = merged
    if grammar:
        progress["grammar"] = dict(sorted(grammar.items()))
    progress["copied"] = max(progress.get("copied", ""), data["copied"])
    PROGRESS.write_text(json.dumps(progress, ensure_ascii=False, indent=1) + "\n")

    old = LOG.read_text(encoding="utf-8").splitlines() if LOG.exists() else []
    seen = set(old)
    new = [line for line in (json.dumps(e, ensure_ascii=False, sort_keys=True) for e in data["log"])
           if line not in seen]
    LOG.write_text("".join(line + "\n" for line in old + new), encoding="utf-8")
    log = [json.loads(line) for line in old + new]
    print(f"Merged: {len(progress['done'])} lessons done, {len(new)} new log entries ({len(log)} in total).")

    misses = [e for e in log if e["t"] == "mistake"]
    if misses:
        print("\nMistakes by kind:")
        for (kind, want, got), n in Counter((e["type"], e["want"], e["got"]) for e in misses).most_common(15):
            print(f"  {n}× {kind}: {want} → {got}")
        tones = Counter(e["want"].split()[0] + " → " + e["got"] for e in misses if e["type"] == "tone")
        if tones:
            print("Tone confusions:", ", ".join(f"{k} ({n}×)" for k, n in tones.most_common(8)))
    rounds = [e for e in log if e["t"] == "practice"]
    if rounds:
        right, total = sum(e["right"] for e in rounds), sum(e["total"] for e in rounds)
        print(f"\nPractice: {total} questions, {round(100 * right / total)}% right")
    batches = [e for e in log if e["t"] == "words" and not e.get("practice")]
    practised = sum(e["total"] for e in log if e["t"] == "words" and e.get("practice"))
    words = progress.get("words")
    if batches or words:
        grades = [sum(e["grades"][i] for e in batches) for i in range(5)]
        names = ["Don't know", "Barely know", "Know", "Safely know", "Securely know"]
        print(f"\nWords: {words['seen'] if words else '?'} seen; {sum(grades)} answers logged "
              f"({', '.join(f'{n} {g}' for n, g in zip(names, grades))})"
              + (f"; {practised} practice answers (today's Know words again)" if practised else ""))
        if words and words["forgotten"]:
            hard = [f"{w} {n}×" + (" ⚑" if n >= 6 else "") for w, n in list(words["forgotten"].items())[:20]]
            print("Often forgotten:", ", ".join(hard))
    checks = [e for e in log if e["t"] == "grammar"]
    if progress.get("grammar"):
        print("\nGrammar:", ", ".join(f"{g} best {st['best']}% ({st['times']}×)" for g, st in progress["grammar"].items()))
        for e in checks[-10:]:
            for w in e.get("wrong", []):
                print(f"  {e['id']} {w}")


if __name__ == "__main__":
    main()
