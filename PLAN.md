# Learning Plan: Mandarin through Pinyin

**Learner:** total beginner, native English speaker
**Goal:** talking to people: introducing yourself, small talk, friends, hobbies, plans, feelings
**Script:** Pinyin only for now (no characters)
**Time:** around 10–15 min on a typical day, but flexible: skip days, or do several lessons at once

---

## 1. Principles

1. **Phrases first, words inside them.** Every lesson is built around whole phrases you can say straight away. Vocabulary and grammar are pulled *out of* those phrases rather than taught in isolation.
2. **Tones from day one.** Pinyin is always written with tone marks (`nǐ hǎo`) and you always hear it. A wrong tone can change the word (`mǎi` buy vs `mài` sell), so tones are never optional.
3. **Small units.** One lesson is one sitting of about 10–15 minutes. On a busy day do one, on a free day do three, on a bad day do nothing. The review system catches up whatever you missed.
4. **Review beats new material.** Flashcards use spaced repetition: cards you know come back rarely, cards you miss come back soon. If you've been away, start with review rather than a new lesson.
5. **Speak out loud.** Every lesson ends with something to say aloud, and chat sessions with me give you conversation practice.

---

## 2. The two tracks

The course runs on two interleaved tracks so that pronunciation never feels like dry theory.

### Track A: Pinyin & pronunciation (front-loaded)

Mostly in the first ~2 weeks, with refreshers later.

| # | Topic | Key content |
|---|-------|-------------|
| A1 | The four tones + neutral tone | Pitch contours, `mā má mǎ mà ma` |
| A2 | Tone pairs | Drilling 2-syllable combinations (most words have 2 syllables) |
| A3 | Easy initials | b p m f d t n l g k h, aspirated vs unaspirated (`b`/`p`) |
| A4 | Simple finals | a o e i u ü, and how `e` differs from English |
| A5 | The "tricky" initials 1 | j q x (tongue down, smile) |
| A6 | The "tricky" initials 2 | zh ch sh r vs z c s |
| A7 | Compound & nasal finals | ai ei ao ou an en ang eng ong, -n vs -ng |
| A8 | Spelling rules | y/w, ü written as u after j/q/x, `iu` = iou, `ui` = uei, `un` = uen |
| A9 | Tone changes (sandhi) | 3rd + 3rd → 2nd + 3rd (`nǐ hǎo` → `ní hǎo`), `bù` → `bú`, `yī` changes |

Each pronunciation lesson comes with an "English sound-alike" guide (e.g. `x` is roughly between English *s* and *sh*), common mistakes English speakers make, and minimal pairs to train your ear.

### Track B: Conversation units (the main course)

Each unit has about 4–6 short lessons, then a **dialogue** lesson that brings the whole unit together, then a **review** lesson.

| Unit | Theme | You'll be able to… | Grammar met along the way |
|------|-------|--------------------|---------------------------|
| 1 | Hello & politeness | greet, thank, apologise, say goodbye | — |
| 2 | Who are you? | give your name, nationality, where you live (Lancaster/UK) | `shì` (to be), `jiào` (to be called), questions with `ma` |
| 3 | Questions | ask *what / who / where / how*, and ask back with *"and you?"* | `shénme`, `shéi`, `nǎr`, `ne` |
| 4 | Numbers & age | count, give your age and phone number | numbers, `duō dà` (how old) |
| 5 | Family & friends | talk about family members and friends | `yǒu` / `méiyǒu`, measure word `gè` |
| 6 | Work & study | say what you do and where you work or study | `zài` (at), `zuò` (do) |
| 7 | Likes & hobbies | say what you like doing, ask others | `xǐhuan` + verb, `huì` (can), `hěn` |
| 8 | Time & days | days, times, *today / tomorrow / weekend* | time words before the verb |
| 9 | Making plans | invite someone, accept or decline, arrange to meet | `yào`, `xiǎng`, `ba` (suggestion) |
| 10 | Eating & drinking together | order, say what you'd like, toast, compliment food | `hē`, `chī`, `yìdiǎnr` |
| 11 | Feelings & opinions | how are you *really*, tired, happy, *I think…* | `juéde`, `tài … le` |
| 12 | What happened? | talk about the weekend, things you did | `le`, `guo`, `méi` |
| 13 | Keeping a conversation going | fillers, *sorry, again please*, *speak slowly* | `qǐng`, `màn yìdiǎnr` |

Track A runs alongside Units 1–3. After that, Track A only comes back as short refreshers whenever a sound keeps going wrong in practice.

**Rough timeline at ~1 lesson/day:** Units 1–4 + all of Track A in ~4 weeks, all 13 units in ~3–4 months. This is a guide, not a deadline.

---

## 3. What a lesson looks like

Every lesson file follows the same template so it's quick to work through:

1. **Goal**: one line, e.g. *"Say your name and ask someone else's."*
2. **Phrases** (about 5): Pinyin, English, a literal word-by-word breakdown, and audio.
   ```
   Nǐ jiào shénme míngzi?        What's your name?
   (you / be-called / what / name)
   ```
3. **New words**: pulled from the phrases, with tone marks, meaning and audio.
4. **Pattern box**: the one grammar idea of the lesson, shown with 2–3 examples.
5. **Pronunciation tip**: the one sound or tone in this lesson most likely to trip you up.
6. **Practice**: 3–5 small exercises (translate, fill the gap, pick the right tone, reorder words).
7. **Say it aloud**: a short line to record or say out loud.
8. **Answer key**: at the bottom, folded away.

---

## 4. Tools in this repository

| Tool | What it is | How you use it |
|------|------------|----------------|
| **Lesson files** (`lessons/`) | Markdown, one file per lesson | Read on GitHub or locally, then do the exercises |
| **Phrase data** (`data/*.json`) | A single source for every phrase and word: Pinyin, English, literal gloss, unit, and *characters, hidden for now* | Lessons, audio and flashcards are all generated from this, so nothing gets out of sync |
| **Audio** (`audio/`) | One MP3 per phrase/word, generated by text-to-speech with a native Mandarin voice | Click from the lesson or flashcards; slowed-down versions for new material |
| **Flashcard page** (`app/`) | A single web page: flashcards (Pinyin → English, English → Pinyin, audio → meaning), tone quizzes, spaced repetition; progress saved in your browser | Open it daily; it tells you how many cards are due |
| **Progress log** (`PROGRESS.md`) | What you've done, and which sounds and phrases you struggle with | I update it after our chat sessions and use it to plan the next lesson |
| **Chat sessions** | You open a session and say e.g. *"quiz me on Unit 2"* or *"role-play meeting someone at a party"* | I quiz, correct your Pinyin and tones, and adapt the next lessons |

Characters are stored in the data from the start, so if you decide to learn them later we can switch them on without redoing anything.

### Planned layout

```
PLAN.md          ← this file
README.md        ← how to use the repo day to day
PROGRESS.md      ← your progress + weak spots
lessons/
  A01-tones.md
  U01-L01-hello.md
  ...
data/
  phrases.json
audio/
  U01-L01-01.mp3 ...
app/
  index.html     ← flashcards & quizzes
tools/
  build.py       ← data → audio + flashcards
```

---

## 5. Your routine (flexible)

| Day type | What to do |
|----------|------------|
| **Normal day (10–15 min)** | Flashcard review (~5 min), then 1 new lesson |
| **Busy day (2–5 min)** | Flashcard review only, which still counts |
| **Free day (30 min+)** | Review, 2–3 lessons, or a chat role-play with me |
| **Back after a break** | Review only until the due count is low, then continue |

Rule of thumb: **don't start a new lesson if more than ~40 flashcards are due.** Clear the review first.

---

## 6. Milestones

- **After Track A + Unit 1:** read any Pinyin aloud with roughly the right sounds and tones.
- **After Unit 4:** hold a 1-minute self-introduction (name, where from, where you live, age, job).
- **After Unit 9:** have a short back-and-forth: ask about someone, talk hobbies, make a plan.
- **After Unit 13:** have a 5-minute simple conversation with me in Pinyin, with mistakes allowed.

Each milestone has a short "checkpoint" chat session where I test you on it.

---

## 7. Build order

1. Set up the repo: `README.md`, `PROGRESS.md`, data format, lesson template.
2. Write **A1 (tones)** and **Unit 1, Lesson 1 (hello)** so you can start straight away.
3. Build the audio generator and add audio to those first lessons.
4. Build the flashcard page.
5. Continue lessons, roughly a week of content ahead of where you are, adjusted by what `PROGRESS.md` shows.
