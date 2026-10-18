"""Merge a "Copy progress for Claude" paste from the app into the repo.

    python tools/progress.py pasted.txt     # or: ... | python tools/progress.py
    python tools/progress.py --github       # what the app synced to the progress branch

- data/progress.json gets the lessons done (date, best score, times), which
  build.py uses for WORDS.md and CHART.md. Pastes from different devices add
  up: a lesson recorded before is kept, even if this paste doesn't have it
- data/progress-log.jsonl gets every new log entry (finished lessons, wrong
  answers, flashcard grades), without duplicates
- prints a summary of weak spots over the whole log, for PROGRESS.md

Run tools/build.py afterwards to update WORDS.md and CHART.md.
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
    return {"copied": synced.get("updated", "")[:16].replace("T", " "),
            "lessons": synced.get("lessons", {}), "log": synced.get("log", [])}


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
    again = Counter(e["card"] for e in log if e["t"] == "review" and e["grade"] == "again")
    if again:
        print("\nFlashcards forgotten most:", ", ".join(f"{c} ({n}×)" for c, n in again.most_common(10)))


if __name__ == "__main__":
    main()
