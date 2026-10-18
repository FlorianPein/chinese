# Mandarin with Pinyin

My course for learning Mandarin Chinese through **Pinyin**, without characters for now. It works through the **Pinyin chart**: first one group of initials per lesson (*bo po mo fo*, *de te ne le*, …), then mixed lessons that go faster. The focus for now is listening: hearing the four tones and the sounds apart, plus a few useful words per lesson.

- **[Open the app](https://florianpein.github.io/chinese/)**: lessons, flashcard review, your words, tone quiz and all audio (works on your phone)
- **[CHART.md](CHART.md)**: the Pinyin chart with the lesson for every syllable, and the order of all 24 lessons
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

Each lesson teaches part of the chart and 2–5 words made only of sounds you already know, in about 35 short steps (10–12 min), mostly listening exercises. From the 2nd lesson on, each one starts with a warm-up and mixes in older sounds and words. Do them in the app; the notes are a summary to read.

| Lesson | Block | Tone focus | New words | Notes |
|--------|-------|------------|-----------|-------|
| [P01](https://florianpein.github.io/chinese/#lesson/P01) | bo po mo fo · wo | all four | wǒ, pò, mō, fó | [notes](lessons/P01.md) |
| [P02](https://florianpein.github.io/chinese/#lesson/P02) | de te ne le · me · e | 2nd vs 3rd; neutral | è, wǒ de, *Wǒ è le.*, *Wǒ ne?* | [notes](lessons/P02.md) |
| [P03](https://florianpein.github.io/chinese/#lesson/P03) | ge ke he | 4th vs 3rd and 1st | hē, hé, kě, gēge, *Wǒ kě le.*, *Wǒ hé gēge* | [notes](lessons/P03.md) |
| [P04](https://florianpein.github.io/chinese/#lesson/P04) | ze ce se | all four | sè, gè, kè | [notes](lessons/P04.md) |
| [P05](https://florianpein.github.io/chinese/#lesson/P05) | zhe che she re | all four | zhè, chē, rè, zhège, *Wǒ de chē*, *Zhège ne?* | [notes](lessons/P05.md) |
| [P06](https://florianpein.github.io/chinese/#lesson/P06) | ji qi xi | all four | qī, jǐ, xǐ, qìchē, *Wǒ xǐ chē.* | [notes](lessons/P06.md) |
| [P07](https://florianpein.github.io/chinese/#lesson/P07) | recap: the puff of air | all four, mixed | kělè, kèqi, *Wǒ hē kělè.*, *Gēge kèqi.* | [notes](lessons/P07.md) |
| [P08](https://florianpein.github.io/chinese/#lesson/P08) | recap: z, zh or j? | all four, faster | jìde, jǐ ge, *Wǒ jìde.*, *Qī ge.* | [notes](lessons/P08.md) |

More lessons are added as you go (next: P09, *ba da ga za zha*). Every lesson uses all four tones. The whole order is in [CHART.md](CHART.md#lesson-order).

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

Audio comes from an offline Mandarin voice ([Matcha-TTS](https://github.com/k2-fsa/sherpa-onnx), trained on the Baker corpus), downloaded on first run to `tools/.cache/`. It's driven directly by the Pinyin, so it applies the spoken tone changes (*nǐ hǎo* is said *ní hǎo*). Each take's pitch is measured and checked against the tones it should have. The best of several takes is kept, and a syllable no take gets right is pitch-edited into the correct tone shape. A 3rd tone said on its own is always pitch-edited into the full dip and rise, and made a bit longer and louder at the end: the voice learned the 3rd tone from sentences, where it's short and only falls, so said alone it sounded like a low 4th. `docs/audio/manifest.json` records which method each file used. Some syllables never occur in some tones in the voice's training data (*fō*, *fǒ*, *fò*, *dě*, *cē*, …). Said directly, they come out as a different sound (*fō* sounded close to *jiē*), so a single syllable like that is always made by pitch-editing the same syllable in a tone the voice knows well (*fó* → *fō*); the manifest's `from` says which. Words and phrases may not use such syllables at all: the build stops and names them. Where the voice can't say a syllable at all, an item gets a `"say"` override plus an `"audio_note"` (e.g. *shéi* is spoken as *shuí*).

## Sync between devices

The app saves your progress in the browser. With sync on, it also keeps it in `progress.json` on a branch of this repo called `progress`. Each device merges that file with its own progress when the app opens, a few seconds after each change, and when you leave the app. So your phone and computer stay in step, and Claude can read your progress without a paste. Nothing done on either device is lost: lessons are combined, each flashcard keeps its latest review, and the mistake logs are joined. Settings stay per device.

The repo is public, so anyone could see `progress.json` (scores, mistakes and flashcard grades), but nothing else about you.

**1. Make a token on GitHub** (once per device, so you can cancel one without the other):

1. Open [github.com/settings/personal-access-tokens/new](https://github.com/settings/personal-access-tokens/new). It's also under your profile picture → **Settings** → **Developer settings** → **Personal access tokens** → **Fine-grained tokens** → **Generate new token**.
2. **Token name:** e.g. `Pinyin app (phone)`.
3. **Expiration:** pick a date, e.g. a year from now. When it expires, the app says so; make a new one and connect again.
4. **Repository access:** **Only select repositories** → `FlorianPein/chinese`.
5. **Permissions** → **Repository permissions** → **Contents** → **Read and write**. Leave everything else as it is (Metadata: read-only is added by itself).
6. **Generate token** and copy it (it starts with `github_pat_`). GitHub shows it only once.

**2. Connect the app:** open the app → **⚙︎** → **Sync between devices**, paste the token, check the device name, and tap **Connect**. Do the same on the other device with its own token. The first sync creates the `progress` branch.

The token is kept only in that browser and can do nothing but read and change this one repo. If you lose a device, delete its token on the same GitHub page. **Disconnect** stops syncing on a device and keeps its progress.

## Practising with Claude

Open a session in this repo and ask, for example:

- *"Check my progress."* With sync on (see above), Claude reads it from the `progress` branch with `python tools/progress.py --github`, updates PROGRESS.md, and plans the next lessons around your mistakes.
- *"Here's my progress:"* and paste from **⚙︎ → Copy progress for Claude**. It holds your finished lessons and scores, the answers you got wrong and your flashcard grades. Claude merges it with `python tools/progress.py`, updates PROGRESS.md, and plans the next lessons around your mistakes. Without sync, each device keeps its own progress, so paste from both: the pastes add up here.
- *"I finished P01."* (marks its words as seen, if you don't want to paste)
- *"Quiz me on everything so far. I'll answer like ma1."*
- *"Drill b vs p and d vs t."*
- *"Build the next lesson."*
