"""Merge a "Copy progress for Claude" paste from the app into the repo.

    python tools/progress.py pasted.txt     # or: ... | python tools/progress.py

- data/progress.json gets the lessons done (date, best score, times), which
  build.py uses for WORDS.md and CHART.md
- data/progress-log.jsonl gets every new log entry (finished lessons, wrong
  answers, flashcard grades), without duplicates
- prints a summary of weak spots over the whole log, for PROGRESS.md

Run tools/build.py afterwards to update WORDS.md and CHART.md.
"""

import json
import re
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


def main():
    text = Path(sys.argv[1]).read_text(encoding="utf-8") if len(sys.argv) > 1 else sys.stdin.read()
    data = extract(text)

    progress = json.loads(PROGRESS.read_text()) if PROGRESS.exists() else {}
    progress["done"] = {lid: st["done"] for lid, st in sorted(data["lessons"].items())}
    progress["lessons"] = dict(sorted(data["lessons"].items()))
    progress["copied"] = data["copied"]
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
