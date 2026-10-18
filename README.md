# Mandarin with Pinyin

My course for learning Mandarin Chinese through **Pinyin**, without characters for now. It starts by working through the **Pinyin chart** block by block (*ba pa ma fa*, *da ta na la*, …), in small Duolingo-style lessons with a few useful words each.

- **[Open the app](https://florianpein.github.io/chinese/)**: lessons, flashcard review, your words, tone quiz and all audio (works on your phone)
- **[CHART.md](CHART.md)**: the Pinyin chart with the lesson for every syllable, and the order of all 48 lessons
- **[WORDS.md](WORDS.md)**: every word taught so far, and which ones you've seen
- **[PLAN.md](PLAN.md)**: how the course works, the slide types, the first lessons in detail, future plans
- **[PROGRESS.md](PROGRESS.md)**: what's done and what needs more practice

## Daily routine

| Day type | What to do |
|----------|------------|
| Normal (10–15 min) | Review if anything is due, then 1 lesson |
| Busy (2–5 min) | Review only |
| Free (30 min+) | Review, then 2–3 lessons |
| Back after a break | Review only until little is due |

Don't start a new lesson while more than ~40 flashcards are due.

## Lessons

Each lesson teaches one block of the chart and 2–5 words made only of sounds you already know, in about 30 short steps (8–10 min). From the 2nd lesson on, each one starts with a warm-up and mixes in older sounds and words. Do them in the app; the notes are a summary to read.

| Lesson | Block | Tone focus | New words | Notes |
|--------|-------|------------|-----------|-------|
| [P01](https://florianpein.github.io/chinese/#lesson/P01) | ba pa ma fa · a | all four (+ neutral) | bā, pà, māma, bàba | [notes](lessons/P01.md) |
| [P02](https://florianpein.github.io/chinese/#lesson/P02) | da ta na la | 2nd vs 3rd | tā, dà, nà, nǎ | [notes](lessons/P02.md) |

More lessons are added as you go (next: P03, *ga ka ha*). Every lesson uses all four tones. The whole order is in [CHART.md](CHART.md#lesson-order).

## The app

| Tab | What it does |
|-----|--------------|
| **Learn** | The lessons in chart order. Tap the next one to start. Planned lessons are shown greyed out. |
| **Review** | Spaced-repetition flashcards for every word and phrase from lessons you've finished: *read* (Pinyin → meaning), *listen* (audio → meaning) and *say it in Pinyin* (meaning → type it). Grade yourself *Again / Hard / Good / Easy*. |
| **Words** | Every word and phrase you've seen, by lesson, with audio. |
| **Tones** | Hear a word or syllable and pick the right tones. |
| **Listen** | All audio of a lesson: words, phrases, and every sound in each tone. 🐢 plays slowly. |
| **⚙︎** | **Copy progress for Claude**, mark lessons as done, settings, export/import your progress (it's stored per browser). |

In speaking exercises you can record yourself and play it back next to the original. The recording stays in your browser.

On a computer: number keys pick an answer, Enter continues, P replays the audio.

## How Pinyin is written here

- **Tone marks** are the main form: `mā`. **Tone numbers** are shown small underneath (<sub>ma1</sub>); you can switch them off in ⚙︎. The neutral tone is `5`.
- When **answering**, either form is fine: `bàba`, `ba4ba5` and `ba4ba` are all accepted.

| Tone | Mark | Number | Shape |
|------|------|--------|-------|
| 1st | ā | a1 | high, flat ¯ |
| 2nd | á | a2 | rising ˊ |
| 3rd | ǎ | a3 | low, dipping ˇ |
| 4th | à | a4 | falling ˋ |
| neutral | a | a5 | short, light |

## Building lessons and audio

`data/course.json` holds the chart and the order of all lessons: each lesson's chart blocks (`a:bpmf` = *ba pa ma fa*), its new tones, and candidate words. A lesson is built once it has its own file, `data/<lesson>.json`, with its words, phrases and the exact list of slides. After changing data:

```sh
pip install -r tools/requirements.txt   # once; also needs ffmpeg
python tools/build.py                   # check, make audio, write docs/cards.json, lessons/*.md, CHART.md, WORDS.md
```

The check catches mistakes such as a chart block missing or taught twice, a word using a syllable or tone that hasn't been taught yet, a word being tested before it's taught, or an answer missing from its options. Everything the build writes is committed, so the app needs nothing generated at run time.

Audio comes from an offline Mandarin voice ([Matcha-TTS](https://github.com/k2-fsa/sherpa-onnx), trained on the Baker corpus), downloaded on first run to `tools/.cache/`. It's driven directly by the Pinyin, so it applies the spoken tone changes (*nǐ hǎo* is said *ní hǎo*). Each take's pitch is measured and checked against the tones it should have. The best of several takes is kept, and a syllable no take gets right is pitch-edited into the correct tone shape. `docs/audio/manifest.json` records which method each file used. Where the voice can't say a syllable at all, an item gets a `"say"` override plus an `"audio_note"` (e.g. *shéi* is spoken as *shuí*).

## Practising with Claude

Open a session in this repo and ask, for example:

- *"Here's my progress:"* and paste from **⚙︎ → Copy progress for Claude**. It holds your finished lessons and scores, the answers you got wrong and your flashcard grades. Claude merges it with `python tools/progress.py`, updates PROGRESS.md, and plans the next lessons around your mistakes.
- *"I finished P01."* (marks its words as seen, if you don't want to paste)
- *"Quiz me on everything so far. I'll answer like ma1."*
- *"Drill b vs p and d vs t."*
- *"Build the next lesson."*
