# Mandarin with Pinyin

My course for learning Mandarin Chinese through **Pinyin**, without characters for now. It's built around useful phrases for talking to people.

- **[Flashcards](https://florianpein.github.io/chinese/)**: review, tone quiz and audio for every lesson (works on your phone)
- **[PLAN.md](PLAN.md)**: the full plan (tracks, units, tools, milestones)
- **[PROGRESS.md](PROGRESS.md)**: what's done and what needs more practice

## Daily routine

| Day type | What to do |
|----------|------------|
| Normal (10–15 min) | Review, then 1 new lesson |
| Busy (2–5 min) | Review only |
| Free (30 min+) | Review, 2–3 lessons, or a chat role-play with Claude |
| Back after a break | Review only until little is due |

Don't start a new lesson while more than ~40 flashcards are due.

## How Pinyin is written here

- **Tone marks** are the main form: `nǐ hǎo`.
- In early lessons, **tone numbers** are shown small underneath: <sub>ni3 hao3</sub>. The neutral tone is `5`.
- When **answering**, either form is fine: `nǐ hǎo`, `ni3 hao3` and `ni3hao3` are all accepted.

| Tone | Mark | Number | Shape |
|------|------|--------|-------|
| 1st | ā | a1 | high, flat ¯ |
| 2nd | á | a2 | rising ˊ |
| 3rd | ǎ | a3 | low, dipping ˇ |
| 4th | à | a4 | falling ˋ |
| neutral | a | a5 | short, light |

## Lessons

Recommended order: Track A and Track B interleaved, as listed.

| Done | Lesson | Topic |
|:----:|--------|-------|
| ☐ | [A01](lessons/A01-tones.md) | The four tones + neutral tone |
| ☐ | [U01-L01](lessons/U01-L01-hello.md) | Hello, thank you, goodbye |

More lessons are added as you go.

## Flashcards

The [flashcard page](https://florianpein.github.io/chinese/) has four tabs:

- **Review**: spaced repetition. Each phrase or word becomes three cards: *read* (Pinyin → meaning), *listen* (audio → meaning) and *say it in Pinyin* (meaning → type the Pinyin, with tone marks or numbers). Grade yourself *Again / Hard / Good / Easy*; cards you know come back less often.
- **Tones**: hear a word and pick the right tones from four options.
- **Listen**: every phrase and word of a lesson with audio; 🐢 plays it slowly.
- **Lessons**: tick the lessons you've done so their cards join your reviews. Also has settings and export/import of your progress (it's stored per browser).

On a computer: keys 1–4 grade, Space shows the answer, P plays the audio.

## Building audio and flashcards

Lessons are written by hand in `lessons/`; every phrase and word is also in `data/<lesson>.json`. After changing data:

```sh
pip install -r tools/requirements.txt   # once; also needs ffmpeg
python tools/build.py                   # check data + lessons, make audio, write docs/cards.json
```

The check makes sure the tone numbers shown in lessons match the tone marks, and that every Pinyin in a lesson is in the data.

Audio comes from an offline Mandarin voice ([Matcha-TTS](https://github.com/k2-fsa/sherpa-onnx), trained on the Baker corpus), downloaded on first run to `tools/.cache/`. It's driven directly by the Pinyin, so it applies the spoken tone changes (*nǐ hǎo* is said *ní hǎo*). Where the voice can't say a syllable, an item gets a `"say"` override plus an `"audio_note"` (e.g. *shéi* is spoken as *shuí*).

## Practising with Claude

Open a session in this repo and ask, for example:

- *"Quiz me on Unit 1."*
- *"Role-play: we meet for the first time at a party."*
- *"Drill my tones on A01."*
- *"I finished U01-L01. Update my progress."*
