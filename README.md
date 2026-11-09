# Mandarin with Pinyin

My course for learning Mandarin Chinese through **Pinyin**, without characters for now. It works through the **Pinyin chart**: first one group of initials per lesson (*bo po mo fo*, *de te ne le*, …), then mixed lessons that go faster. For now it's **only sounds and tones, no words**: every lesson is listening, hearing the four tones and the sounds apart.

- **[Open the app](https://florianpein.github.io/chinese/)**: lessons, a listening drill and all audio (works on your phone)
- **[CHART.md](CHART.md)**: the Pinyin chart with the lesson for every syllable, and the order of all 24 lessons
- **[PLAN.md](PLAN.md)**: how the course works, the slide types, the first lessons in detail, future plans
- **[PROGRESS.md](PROGRESS.md)**: what's done and what needs more practice
- **[WORDS-PLAN.md](WORDS-PLAN.md)**: how the word flashcards work: when a word comes back, how new words come in through Study, where the words come from
- **[GRAMMAR.md](GRAMMAR.md)**: the grammar topics in HSK order, one per session, and which are built

## Daily routine

| Day type | What to do |
|----------|------------|
| Normal (15–25 min) | Words, a few minutes of Practice, then 1 lesson |
| Busy (2–5 min) | Words or Practice |
| Free (30 min+) | Words, Practice, then 2–3 lessons, or 1 grammar session |
| Back after a break | Practice, then the last lesson again |

If a lesson came out below about 70% right first time, do it again before the next one.

## Lessons

Each lesson teaches part of the chart in about 37 short steps (10–12 min), almost all of them listening exercises: which tone, which sound, same or different, odd one out, two to four sounds in a row, match the sounds, type what you hear. From the 2nd lesson on, each one starts with a warm-up on the sounds before. Do them in the app; the notes are a summary to read.

| Lesson | Block | Sounds | Tones | Notes |
|--------|-------|--------|-------|-------|
| [P01](https://florianpein.github.io/chinese/#lesson/P01) | bo po mo fo · wo | b vs p | all four, then two and three in a row | [notes](lessons/P01.md) |
| [P02](https://florianpein.github.io/chinese/#lesson/P02) | de te ne le · e | the vowel e; d vs t | 2nd vs 3rd, alone and in pairs | [notes](lessons/P02.md) |
| [P03](https://florianpein.github.io/chinese/#lesson/P03) | ge ke he | g vs k; the rough h | 4th vs 3rd and 1st, alone and in a row | [notes](lessons/P03.md) |
| [P04](https://florianpein.github.io/chinese/#lesson/P04) | ze ce se | z vs c vs s; z/c vs d/t | same tone, different initial | [notes](lessons/P04.md) |
| [P05](https://florianpein.github.io/chinese/#lesson/P05) | zhe che she re | z vs zh, s vs sh, r vs l | all four | [notes](lessons/P05.md) |
| [P06](https://florianpein.github.io/chinese/#lesson/P06) | ji qi xi | j vs q; x vs s and sh | all four, up to four in a row | [notes](lessons/P06.md) |
| [P07](https://florianpein.github.io/chinese/#lesson/P07) | recap: the puff of air | b/p d/t g/k z/c zh/ch j/q | all four, mixed | [notes](lessons/P07.md) |
| [P08](https://florianpein.github.io/chinese/#lesson/P08) | recap: z, zh or j? | z/zh/j c/ch/q s/sh/x, r | all four, faster | [notes](lessons/P08.md) |

More lessons are added as you go (next: P09, *ba da ga za zha*). Every lesson uses all four tones. The whole order is in [CHART.md](CHART.md#lesson-order).

## The app

| Tab | What it does |
|-----|--------------|
| **Learn** | The lessons in chart order. Tap the next one to start. Planned lessons are shown greyed out. |
| **Practice** | An endless listening drill with the sounds of the lessons you've finished: which tone, which sound, or same or different. A sound you get wrong comes back a few questions later. |
| **Words** | Flashcards of the most common words, Anki-style. You hear the word and see its Pinyin and characters; tap for the English and an example sentence (Pinyin, characters, English), then pick *Don't know*, *Barely know*, *Know*, *Safely know* or *Securely know*. Each button shows when the word comes back. Sessions never bring new words: **Study** shows a table of the next 10 words to learn (first the ones you said *Don't know* to, then new words), and once you've studied them they come into your sessions. A word you say *Don't know* to twice is set aside until you study it. **Practise today's *Know* words** goes over the words you picked *Know* for today that come back tomorrow, without moving them up. Details in [WORDS-PLAN.md](WORDS-PLAN.md). |
| **Grammar** | Chinese grammar, **one topic per session**, in HSK order (19 HSK 1 topics built, HSK 2 and 3 planned). Each session explains its topic with example sentences you can play (🔊, 🐢 slowly), the grammar point highlighted, and wrong sentences marked ✗ with why. Then **Check yourself**: 6 questions (put the words in order, fill the gap, which sentence is right, what it means); a wrong one comes back once at the end. The sentences only use words from Words, the further on the topic, the further down the word list; *Words in this session* shows which ones you've already seen there. Topics and order in [GRAMMAR.md](GRAMMAR.md). |
| **Listen** | All audio of a lesson: every sound in each tone. 🐢 plays slowly. |
| **⚙︎** | **Copy progress for Claude**, mark lessons as done, settings, export/import your progress (it's stored per browser). |

On a computer: number keys pick an answer, Enter continues, P replays the audio. In Words: Space shows the answer, 1–5 are the five buttons.

## How Pinyin is written here

- **Tone marks** are the main form: `mā`. **Tone numbers** are shown small underneath (<sub>ma1</sub>); you can switch them off in ⚙︎. The neutral tone is `5`.
- When **answering**, either form is fine: `mā` and `ma1` are both accepted.

| Tone | Mark | Number | Shape |
|------|------|--------|-------|
| 1st | ā | a1 | high, flat ¯ |
| 2nd | á | a2 | rising ˊ |
| 3rd | ǎ | a3 | low, dipping ˇ |
| 4th | à | a4 | falling ˋ |
| neutral | a | a5 | short, light |

## Building lessons and audio

`data/course.json` holds the chart and the order of all lessons: each lesson's chart blocks (`a:bpmf` = *ba pa ma fa*) and its focus. A lesson is built once it has its own file, `data/<lesson>.json`, with the exact list of slides. After changing data:

```sh
pip install -r tools/requirements.txt   # once; also needs ffmpeg
python tools/build.py                   # check, make audio, write docs/cards.json, docs/words.json, lessons/*.md, CHART.md
node tools/test_srs.js                  # check the flashcard rules (when a word comes back, sessions, Study)
```

The flashcard words are in `data/words.json`, most common first. The build checks each one (characters, Pinyin, one syllable per character, the voice can say it) and makes its audio like the lesson audio.

The grammar topics are listed in `data/grammar.json` (HSK order); a topic is built once it has `data/grammar/<id>.json` (format at the top of `tools/grammar.py`). The build checks every sentence: one syllable per character, and cut into words that are all in the word list with the same Pinyin there. Each topic may use the word list up to a limit that grows from the 170 most common words (G01) to all of them (the last topic); a session can bring in at most 6 further words as `extra`. It makes audio for every example and question sentence, writes `docs/grammar.json` and [GRAMMAR.md](GRAMMAR.md).

The check catches mistakes such as a chart block missing or taught twice, a lesson playing a syllable that hasn't been taught yet, a tone question without all four tones, or an answer missing from its options. Everything the build writes is committed, so the app needs nothing generated at run time.

Audio comes from an offline Mandarin voice ([Matcha-TTS](https://github.com/k2-fsa/sherpa-onnx), trained on the Baker corpus), downloaded on first run to `tools/.cache/`. It's driven directly by the Pinyin, so it applies the spoken tone changes (*nǐ hǎo* is said *ní hǎo*). Each take's pitch is measured and checked against the tones it should have. The best of several takes is kept, and a syllable no take gets right is pitch-edited into the correct tone shape. A 3rd tone said on its own is always pitch-edited into the full dip and rise, and made a bit longer and louder at the end: the voice learned the 3rd tone from sentences, where it's short and only falls, so said alone it sounded like a low 4th. `docs/audio/manifest.json` records which method each file used. Some syllables never occur in some tones in the voice's training data (*fō*, *fǒ*, *fò*, *dě*, *cē*, …). Said directly, they come out as a different sound (*fō* sounded close to *jiē*), so a single syllable like that is always made by pitch-editing the same syllable in a tone the voice knows well (*fó* → *fō*); the manifest's `from` says which. Words and phrases may not use such syllables at all: the build stops and names them. Where the voice can't say a syllable at all, an item gets a `"say"` override plus an `"audio_note"` (e.g. *shéi* is spoken as *shuí*).

## Sync between devices

The app saves your progress in the browser. With sync on, it also keeps it in `progress.json` on a branch of this repo called `progress`. Each device merges that file with its own progress when the app opens, a few seconds after each change, and when you leave the app. So your phone and computer stay in step (lessons, practice and words), and Claude can read your progress without a paste. Nothing done on either device is lost: lessons are combined, and the logs of mistakes and practice are joined. Settings stay per device.

The repo is public, so anyone could see `progress.json` (scores, mistakes and practice results), but nothing else about you.

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
- *"Here's my progress:"* and paste from **⚙︎ → Copy progress for Claude**. It holds your finished lessons and scores, the answers you got wrong and your practice results. Claude merges it with `python tools/progress.py`, updates PROGRESS.md, and plans the next lessons around your mistakes. Without sync, each device keeps its own progress, so paste from both: the pastes add up here.
- *"I finished P01."* (marks it done in CHART.md, if you don't want to paste)
- *"Quiz me on everything so far. I'll answer like ma1."*
- *"Drill b vs p and d vs t."*
- *"Build the next lesson."*
- *"Build the next grammar topics."* (HSK 2 and 3 are planned in `data/grammar.json`)
