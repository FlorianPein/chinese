# Mandarin with Pinyin

My course for learning Mandarin Chinese through **Pinyin**, without characters for now. It's built around useful phrases for talking to people, in small Duolingo-style lessons.

- **[Open the app](https://florianpein.github.io/chinese/)**: lessons, flashcard review, tone quiz and all audio (works on your phone)
- **[PLAN.md](PLAN.md)**: the full plan (topics, lessons, tools, milestones)
- **[PROGRESS.md](PROGRESS.md)**: what's done and what needs more practice

## Daily routine

| Day type | What to do |
|----------|------------|
| Normal (10–15 min) | Review if anything is due, then 1 lesson |
| Busy (2–5 min) | Review only |
| Free (30 min+) | Review, 2–3 lessons, or a chat role-play with Claude |
| Back after a break | Review only until little is due |

Don't start a new lesson while more than ~40 flashcards are due.

## Lessons

Each lesson brings only a little new (one sound, 3–5 words) and practises it in about 30 short exercises, mixed with earlier words: about 10–15 minutes. Do them in the app; the notes are a summary to read.

| Lesson | Topic | New words | Notes |
|--------|-------|-----------|-------|
| [A01-L01](https://florianpein.github.io/chinese/#lesson/A01-L01) | Tones 1 and 4: high and falling | tā, hē, shì, bù, duì | [notes](lessons/A01-L01.md) |
| [A01-L02](https://florianpein.github.io/chinese/#lesson/A01-L02) | Tone 3: low | wǒ, nǐ, hǎo | [notes](lessons/A01-L02.md) |

More lessons are added as you go (next: A01-L03, the 2nd tone).

## The app

| Tab | What it does |
|-----|--------------|
| **Learn** | The lessons, in order. Tap the next one to start. |
| **Review** | Spaced-repetition flashcards for every word and phrase from lessons you've finished: *read* (Pinyin → meaning), *listen* (audio → meaning) and *say it in Pinyin* (meaning → type it). Grade yourself *Again / Hard / Good / Easy*. |
| **Tones** | Hear a word or syllable and pick the right tones. |
| **Listen** | All audio of a lesson: words, phrases, and every sound in each tone. 🐢 plays slowly. |
| **⚙︎** | Mark lessons as done, settings, export/import your progress (it's stored per browser). |

In speaking exercises you can record yourself and play it back next to the original. The recording stays in your browser.

On a computer: number keys pick an answer, Enter continues, P replays the audio.

## How Pinyin is written here

- **Tone marks** are the main form: `nǐ hǎo`. **Tone numbers** are shown small underneath (<sub>ni3 hao3</sub>); you can switch them off in ⚙︎. The neutral tone is `5`.
- When **answering**, either form is fine: `nǐ hǎo`, `ni3 hao3` and `ni3hao3` are all accepted.

| Tone | Mark | Number | Shape |
|------|------|--------|-------|
| 1st | ā | a1 | high, flat ¯ |
| 2nd | á | a2 | rising ˊ |
| 3rd | ǎ | a3 | low, dipping ˇ |
| 4th | à | a4 | falling ˋ |
| neutral | a | a5 | short, light |

## Building lessons and audio

Every lesson is one file, `data/<lesson>.json`: its words and phrases, and the exact list of steps (explanations and exercises). `data/course.json` sets the order. After changing data:

```sh
pip install -r tools/requirements.txt   # once; also needs ffmpeg
python tools/build.py                   # check lessons, make audio, write docs/cards.json and lessons/*.md
```

The check catches mistakes such as a word being tested before it's taught, an answer missing from its options, or a phrase using a word that hasn't been learned yet. Everything the build writes is committed, so the app needs nothing generated at run time.

Audio comes from an offline Mandarin voice ([Matcha-TTS](https://github.com/k2-fsa/sherpa-onnx), trained on the Baker corpus), downloaded on first run to `tools/.cache/`. It's driven directly by the Pinyin, so it applies the spoken tone changes (*nǐ hǎo* is said *ní hǎo*). Each take's pitch is measured and checked against the tones it should have. The best of several takes is kept, and a syllable no take gets right is pitch-edited into the correct tone shape. `docs/audio/manifest.json` records which method each file used. Where the voice can't say a syllable at all, an item gets a `"say"` override plus an `"audio_note"` (e.g. *shéi* is spoken as *shuí*).

## Practising with Claude

Open a session in this repo and ask, for example:

- *"Quiz me on A01."*
- *"Drill my tones."*
- *"I finished A01-L02. Update my progress."*
- *"Role-play: we meet for the first time at a party."* (once Unit 1 is done)
