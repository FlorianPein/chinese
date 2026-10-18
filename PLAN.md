# Learning Plan: Mandarin through the Pinyin chart

**Learner:** total beginner; explanations in English, pronunciation compared to English *and* German
**Goal:** talking to people. The first step is to hear and say every sound of Mandarin
**Script:** Pinyin only (no characters for now)
**Time:** one lesson is about 10–12 min; skip days, or do several lessons at once
**Focus for now:** listening (telling the tones and the sounds apart) and a few words per lesson

### Decisions

| Topic | Decision |
|-------|----------|
| Course structure | For now the lessons work through the **Pinyin chart** (like the [Yabla chart](https://chinese.yabla.com/chinese-pinyin-chart.php)). First **one group of initials per lesson** (P01–P06), then **two recap lessons**, then **mixed lessons** that combine several groups and finals and get faster. Everything else is in [future plans](#6-future-plans) |
| Lesson size | P01–P08: one group of initials with one final (e.g. *bo po mo fo*) and 2–5 words. From P09: 3–15 chart blocks around one contrast (e.g. *an vs ang* everywhere). About 35 short steps |
| Exercises | Mostly **listening**: which tone, which sound, same or different, match the sounds, write what you hear. Speaking and sentence building come back later |
| Words | Chosen by importance, and only from syllables and tones you've already learned (checked automatically) |
| Repetition | From the 2nd lesson on, every lesson starts with a warm-up and mixes in older sounds and words. Finished lessons go into spaced-repetition flashcards |
| Where lessons happen | In the web app ([Learn tab](https://florianpein.github.io/chinese/)). Each lesson also has generated notes in `lessons/` |
| Your answers | Mostly buttons. When you type, `ma1` and `mā` both work; neutral tone is `5` or no number |
| Tones | **All four, always together.** P01 teaches all four at once, and every chart and tone question in every lesson has all four, so you always hear the contrasts. The build enforces this |
| Sound comparisons | English *and* German |
| Characters | Stored in the data, hidden everywhere for now |

---

## 1. How the course works

Every syllable is **initial + final + tone**: `b` + `a` + 1st tone = `bā`. The chart puts initials down the side and finals across the top. One **block** (or *entry*) is one final with one group of initials:

| Group | Initials | Where the tongue is |
|-------|----------|---------------------|
| lips | b p m f | |
| tongue tip | d t n l | behind the top teeth |
| back of the tongue | g k h | |
| tongue at the teeth | z c s | |
| tongue curled back | zh ch sh r | |
| tongue flat | j q x | |
| no initial | (a, o, e, yi, wu, yu, …) | |

So `a` with the lips group is the block **ba pa ma fa**, and `a` with the tongue-tip group is **da ta na la**.

**How blocks become lessons**

- **P01–P06: one group of initials per lesson**, each with the one final that suits it (*o* after the lips, *e* after the others, *i* after j q x). So the first six lessons go through every initial with almost the same vowel, and what you learn to hear is the initials: *bo/po*, *de/te*, *ge/ke*, *ze/ce*, *zhe/che*, *ji/qi*, and *ze/zhe/ji* side by side.
- **P07–P08: recap** of the first six. No new sounds: P07 mixes the pairs with and without a puff of air (b/p, d/t, g/k, z/c, zh/ch, j/q), P08 the three tongue positions (z/zh/j, c/ch/q, s/sh/x). Mixed in random order, all four tones, faster than before.
- **From P09: mixed and faster.** Each lesson takes a new final, or a pair of finals that are easy to confuse (*ai/ei*, *an/ang*, *en/eng*, *in/ing*, *u/ü*), across several groups of initials at once, in no fixed order. Lessons cover more of the chart each time: 3 blocks in P10, up to 15 in P23.
- **All four tones from the start, never separated**: P01 introduces all four side by side. From then on every chart shows all four tones and every tone question offers all four, because the tones are learned by hearing them against each other. Each early lesson also trains one hard contrast: P02 the 2nd against the 3rd (and the light neutral tone in *wǒ de*), P03 the 4th against the 3rd (low, dips and comes back up) and the 1st (stays high).
- **Tone changes** are taught where they first come up: *bù → bú* before a 4th tone (P11), *yī → yí* (as soon as *yí gè* appears), and two 3rd tones in a row (*nǐ hǎo*, P14).

**The order: 24 lessons in 7 topics.** The full list, with the chart showing which lesson teaches each of the 404 syllables, is in **[CHART.md](CHART.md)** (generated from `data/course.json`).

| Topic | Lessons | What's new | Example words |
|-------|---------|-----------|---------------|
| One group of initials per lesson | P01 | bo po mo fo · wo; the four tones | `wǒ`, `pò`, `mō`, `fó` |
| | P02 | de te ne le · me · e; 2nd vs 3rd; neutral tone | `è`, `wǒ de`, *Wǒ è le.* |
| | P03 | ge ke he; 4th vs 3rd and 1st | `hē`, `hé`, `kě`, `gēge`, *Wǒ kě le.* |
| | P04 | ze ce se; s is always sharp (German ß) | `sè`, `gè`, `kè` |
| | P05 | zhe che she re; z vs zh, s vs sh | `zhè`, `chē`, `rè`, `zhège`, *Zhège ne?* |
| | P06 | ji qi xi; x = German *ich* | `qī`, `jǐ`, `xǐ`, `qìchē`, *Wǒ xǐ chē.* |
| Recap | P07 | the puff of air: b/p d/t g/k z/c zh/ch j/q | `kělè`, `kèqi`, *Wǒ hē kělè.* |
| | P08 | z, zh or j? c, ch or q? s, sh or x? | `jìde`, `jǐ ge`, *Qī ge.* |
| Simple finals, mixed | P09–P12 | the a row everywhere · zi zhi, er · i vs u · u vs ü | `bàba`, `tā`, `chá`, `shì`, `chī`, `nǐ`, `bù`, `qù` |
| ai ei ao ou, mixed | P13–P15 | ai vs ei · ao vs ou · z c s vs zh ch sh with all four | `lái`, `méi`, `hǎo`, `dōu`, `zài`, `shéi` |
| -n and -ng, mixed | P16–P18 | an vs ang · an ang ong with z/zh · en vs eng | `kàn`, `máng`, `sān`, `hěn`, `rén`, `néng` |
| Finals starting with i, mixed | P19–P21 | ia ie iao · iu ian · in ing iang iong | `jiā`, `xièxie`, `yǒu`, `qián`, `míngzi` |
| Finals starting with u and ü, mixed | P22–P24 | ua uo uai · ui uan un · uang weng and üe üan ün | `shuō`, `Zhōngguó`, `duì`, `xǐhuan`, `xué` |

Words for lessons that aren't built yet are candidates. They're picked when the lesson is made, adjusted to what you find hard (see `PROGRESS.md`).

---

## 2. Slide types

A lesson is a sequence of slides. Some teach, most are exercises. Every slide that shows a sound can play it.

### Teaching slides

| Slide | What it does | Status |
|-------|--------------|--------|
| **tip** (`intro`) | A short explanation with English and German comparisons, a tone diagram, and rows of sounds to tap | ✅ |
| **chart** (`chart`) | The lesson's block as a grid: syllables down, tones across. Tap a square, a row (one syllable in every tone) or a column (one tone down the block) | 🆕 |
| **new word** (`new`) | The word with audio and slow audio, its meaning, a pronunciation note, and its syllable in all four tones | ✅ |
| **new phrase** (`new`) | A short sentence with a word-by-word breakdown you can tap | ✅ |

### Exercises on sounds

| Slide | What you do | Answer | Status |
|-------|-------------|--------|--------|
| **listen** (`hear`) | Hear a sound, pick the Pinyin (e.g. *bā* or *pā*) | buttons | ✅ |
| **which tone** (`tone`) | Hear a sound, pick its tone | tone buttons | ✅ |
| **same or different** (`same`) | Hear two sounds, say whether they're the same (*bà* / *pà*) | 2 buttons | 🆕 |
| **read and listen** (`audio`) | See the Pinyin, listen to 2–3 sounds, pick the one that says it | buttons | 🆕 |
| **match sounds** (`match`, sound mode) | Match 4 sounds to their Pinyin | tapping pairs | 🆕 |
| **listen and type** (`type`, from audio) | Type what you hear | `ma1` or `mā` | ✅ |
| **say it aloud** (`speak`) | Listen, repeat, record yourself and compare with the original | — | ✅ |

### Exercises on words

| Slide | What you do | Answer | Status |
|-------|-------------|--------|--------|
| **meaning** (`meaning`) | Hear or read a word, pick its meaning | buttons | ✅ |
| **say it in Pinyin** (`pinyin`) | See the meaning, pick the right Pinyin | buttons | ✅ |
| **match the pairs** (`match`) | Match Pinyin and meanings | tapping pairs | ✅ |
| **build the sentence** (`build`) | Put word tiles in order | tiles | ✅ |
| **type it** (`type`, from English) | See the meaning, type the Pinyin | `ma1` or `mā` | ✅ |

Every exercise you get wrong comes back at the end of the lesson (up to twice).

### Ideas for later

| Slide | What you'd do | When it's useful |
|-------|---------------|------------------|
| **spell it** | Hear a syllable, build it from buttons: initial + final + tone (no typing) | Once there are many finals (from P17) |
| **odd one out** | Hear three sounds, pick the one that's different | Hard contrasts: z/zh, in/ing, an/ang |
| **speed round** | 10 quick tone or sound questions in a row | Review lessons |
| **chart review** | The whole chart so far, learned blocks highlighted, tap anything | After each topic |
| **fill the gap** | A sentence with one word missing | Once there are ~30 words |
| **listen and answer** | Hear a question, pick a sensible reply | Once there are questions (*ma*, *nǎ*, *shéi*) |
| **dialogue** | A short conversation with audio, line by line | Later, with the conversation units |

---

## 3. The first lessons

Both are almost all listening: no speaking or sentence-building slides for now.

### P01: bo po mo fo · wo (36 steps, ≈ 11 min)

**Blocks:** `o` with b p m f, and `wo`. **Tones:** all four.

| Part | Slides |
|------|--------|
| 1. The chart | **tip**: initial + final + tone; today's block; the *o* after b p m f has a little *w* in it (*bo* ≈ *b-wo*), open like British *law* / German *Sonne* |
| 2. b vs p | **tip** (the puff of air, hand in front of the mouth) → **listen** *bō/pō* → **same or different** *bò/pò* → **listen** *bó/pó/mó* |
| 3. Tones | **tip**: *mo* in all four tones, just listening → **tip** for each tone, each with *mō mó mǒ mò* to compare → **same or different** *mó/mǒ* → **chart** bo po mo fo × all four tones |
| 4. Practise the block | 4× **which tone** (always 4 choices) · **same or different** *pō/pò* · **read and listen** *pǒ* · **match sounds** (one per tone) · **listen** *mó* (from all four) · **listen and type** *pò* |
| 5. Words, one per tone | **new** `wǒ` (I, me) · **which tone** · **new** `pò` (broken) · **meaning** · **new** `mō` (to touch) · **listen** · **new** `fó` (Buddha) · **tip** the four words side by side: *mō fó wǒ pò* · **meaning** · **same or different** *fó/fǒ* · **match** · **meaning** · **say it in Pinyin** · **listen** *fó* (from all four) · **listen and type** *wǒ* |

### P02: de te ne le · me · e (36 steps, ≈ 10 min)

**Blocks:** `e` with d t n l, `me`, and `e` alone. **Tones:** all four; the contrast to train is the 2nd (rising) against the 3rd (low). New: the neutral tone, in *wǒ de*.

| Part | Slides |
|------|--------|
| 1. Warm-up (P01) | **tip** with P01's block in all four tones → **listen** *bò/pò* → **meaning** *wǒ*, *fó* (audio) → **which tone** *fó* |
| 2. The vowel e | **tip** (say *o*, then smile: a deep *uh*; not the e of *bed* / *Bett*) with *ē é ě è* and *wo* against *e* → **listen** *wò/è* → **same or different** *wō/ē* |
| 3. d vs t | **tip** (same puff as b/p) → **listen** *dè/tè* → **same or different** *dé/té* → **listen** *nè/lè/dè* |
| 4. 2nd or 3rd? | **tip** (where the tone starts: mid and up, or low) with *dé/dě*, *né/ně*, *mó/mǒ* → **same or different** *lé/lě* → **chart** de te ne le × all four tones |
| 5. Practise the block | 4× **which tone** (one old: *pǒ*) · **same or different** · **read and listen** *lě* · **match sounds** · **listen** *né* (from dé té né lé) · **listen and type** *dě* |
| 6. Words | **new** `è` (hungry) · **meaning** · **new** `wǒ de` (my) · **tip** neutral tone (*wǒ* → *wǒ de*) · **new** *Wǒ è le.* (I'm hungry.) · **new** *Wǒ ne?* (And me?) · **meaning** (audio) ×2 · **say it in Pinyin** · **match** · **listen** *pò* · **listen and type** *è* |

Why these words: *wǒ* is the most useful word there is, and the four P01 words have one tone each (*mō fó wǒ pò*), so the words themselves are a tone drill. In P02, *de, le, ne* and *me* are nearly always neutral grammar words, so the lesson uses them for the neutral tone and gives you two everyday phrases: *Wǒ è le.* and *Wǒ ne?*. P03 adds *kě* (thirsty) for *Wǒ kě le.*

**Audio note:** *o* on its own (the interjection *ó / ò*, "oh?") isn't used: the speech model says it unclearly. Neutral syllables are only played inside words, because on their own they come out with a full tone. Syllables the model never heard in a tone (*fō fǒ fò*, *dě dè*, *tē té tě*, …) are pitch-edited from a tone it knows (*fó*), because said directly they sound like another syllable.

### P03–P08 in short

All six follow the same pattern as P02: a warm-up on the previous lesson, the new initials one at a time with English and German comparisons, the chart block, a practice round (always one old sound mixed in), then the words.

| Lesson | Explanations | Contrasts drilled | Words and phrases |
|--------|--------------|-------------------|-------------------|
| P03 | g/k (the puff a third time); h is rough like German *ach*; 4th vs 3rd (high and falling, or low, dipping and rising) and 4th vs 1st (both start high: stay or drop) | gē/kē, kē/hē, lě/lè, kē/kè | `hē` (drink), `hé` (and), `kě` (thirsty), `gēge`, *Wǒ kě le.*, *Wǒ hé gēge* |
| P04 | z = soft ts (German *Zeit*, no puff); c = ts with a puff, never k or s; s always sharp like *ß* | dé/zé, zè/cè, tè/cè, zè/cè/sè | `sè`, `gè`, `kè`: all 4th tone, so only the initial differs |
| P05 | zh ch sh r with the tongue curled back (German *dsch, tsch, sch*; r like English *run*) | zhè/chè, ze/zhe, ce/che, se/she, rè/lè | `zhè`, `chē`, `rè`, `zhège`, *Wǒ de chē*, *Zhège ne?* |
| P06 | the vowel i; j q x with a flat tongue; x = German *ich*; three tongue positions side by side | jì/qì, she/xi, sè/shè/xì | `qī`, `jǐ`, `xǐ`, `qìchē`, *Wǒ xǐ chē.* |
| P07 | recap: the six puff pairs, then puff and tone at once | b/p d/t g/k z/c zh/ch j/q, random order | `kělè`, `kèqi`, *Wǒ hē kělè.*, *Gēge kèqi.* |
| P08 | recap: three tongue positions; s/sh/x and r | z/zh/j, c/ch/q, s/sh/x, faster | `jìde`, `jǐ ge`, *Wǒ jìde.*, *Qī ge.* |

---

## 4. Repetition and tracking words

- **In the lessons:** every lesson after P01 starts with a warm-up on earlier sounds and words, and mixes old words into its exercises and sentences.
- **Flashcards:** a finished lesson's words and phrases go into the **Review** tab (spaced repetition: read, listen, and type it in Pinyin).
- **Words you've seen:**
  - the app's **Words** tab lists every word and phrase from the lessons you've finished in that browser;
  - **[WORDS.md](WORDS.md)** lists every word per lesson and marks it *seen* once the lesson is in `data/progress.json`. Say *"I finished P01"* and Claude updates it. New lessons are planned from this list: no word is taught twice, and recaps use words you've seen.
- **Weak spots** (sounds or words that keep going wrong) go in [PROGRESS.md](PROGRESS.md), and the next lessons repeat them more.
- **How Claude learns your progress:** the app keeps a log of finished lessons (with scores), every wrong answer (what was asked and what you picked) and every flashcard grade. **⚙︎ → Copy progress for Claude** (also on the *Lesson complete* screen) copies a short summary plus the new log entries; paste it into a chat. Claude merges it with `tools/progress.py` into `data/progress.json` and `data/progress-log.jsonl`, updates PROGRESS.md, and plans the next lessons around your mistakes.

---

## 5. Tools in this repository

| Tool | What it is |
|------|------------|
| **Web app** (`docs/`, GitHub Pages) | **Learn**: the lessons in chart order. **Review**: flashcards. **Words**: everything you've seen. **Tones**: a tone-hearing quiz. **Listen**: all audio of a lesson. Progress is saved in your browser (export/import in ⚙︎) |
| **Course** (`data/course.json`) | The chart (initial groups, finals) and all 24 lessons: blocks, new tones, focus, candidate words |
| **Lessons** (`data/P01.json`, …) | A built lesson's words, phrases (with hidden characters) and its exact slides |
| **Progress** (`data/progress.json`) | The lessons you've done, for WORDS.md and CHART.md |
| **Build** (`tools/build.py`) | Checks everything (each chart block taught once, every word only uses sounds taught by then, no word tested before it's taught, …), makes the audio, writes the app data, lesson notes, CHART.md and WORDS.md |
| **Audio** (`docs/audio/`) | One MP3 per word, phrase and sound, made offline and tone-checked |

```
PLAN.md  README.md  PROGRESS.md  CHART.md  WORDS.md
data/      course.json  P01.json … P08.json  progress.json
lessons/   P01.md … P08.md          ← generated notes
docs/      index.html  cards.json  audio/
tools/     build.py  chart.py  pinyin.py
archive/   earlier versions of the course
```

---

## 6. Future plans

Moved out of the course for now. They come back once the chart is done (or earlier, mixed in, if you want a break from sounds).

**Conversation units** (the earlier Track B). By the end of the chart you'll know about 100 words, many of them from these units (*nǐ*, *hǎo*, *xièxie*, *jiào*, *míngzi*, *péngyou*, *xǐhuan* …), so the units can go faster.

| Unit | Theme | You'll be able to… |
|------|-------|--------------------|
| 1 | Hello & politeness | greet, thank, apologise, say goodbye |
| 2 | Who are you? | give a name, nationality, where someone lives |
| 3 | Questions | ask *what / who / where / how*, and *"and you?"* |
| 4 | Numbers & age | count, give your age and phone number |
| 5 | Family & friends | talk about family and friends |
| 6 | Work & study | say what you do and where |
| 7 | Likes & hobbies | say what you like doing, ask others |
| 8 | Time & days | days, times, *today / tomorrow / weekend* |
| 9 | Making plans | invite, accept or decline, arrange to meet |
| 10 | Eating & drinking together | order, toast, compliment food |
| 11 | Feelings & opinions | how are you really, *I think…* |
| 12 | What happened? | talk about the weekend |
| 13 | Keeping a conversation going | fillers, *sorry, again please*, *speak slowly* |

**Other sound topics:**
- **Tone pairs:** the 20 combinations of two tones in a word (*xièxie*, *lǎoshī*, *péngyou*), as drills
- **Tone changes in depth:** 3+3, *bù*, *yī*, as separate practice lessons
- **Chart checkpoints:** a short review lesson after each topic, if the flashcards aren't enough

**To do: automatic progress sync to GitHub.** Instead of copying and pasting, the app would save its log to this repo by itself (on a separate `progress` branch, so the lessons and the app aren't touched), after each lesson and review session. Claude would read it at the start of every session, and your phone and laptop would share progress. It needs a one-time setup per device: a fine-grained GitHub token that can only write to this repo, pasted into ⚙︎. The log format is already the one the copy button uses, so `tools/progress.py` would work unchanged.

**Later still:** characters (they're already stored with every word), chat role-plays with Claude, an in-app chart of every syllable with audio.

The first versions of the tone lessons (A01-L01, A01-L02) and of U01-L01 are in `archive/`. Their explanations and phrases get reused.

---

## 7. Routine and milestones

| Day type | What to do |
|----------|------------|
| **Normal day (10–15 min)** | Review if anything is due, then 1 lesson |
| **Busy day (2–5 min)** | Review only |
| **Free day (30 min+)** | Review, then 2–3 lessons |
| **Back after a break** | Review only until little is due |

Rule of thumb: **don't start a new lesson if more than ~40 flashcards are due.**

- **After P01:** all four tones. **After P03:** the hardest tone contrasts (2nd/3rd, 1st/4th).
- **After P06:** every initial, including z c s, zh ch sh r and j q x. **After P08:** you can hear them apart in a random mix.
- **After P18:** every simple final, ai ei ao ou, and -n / -ng; you can hear most syllables you meet.
- **After P24:** the whole chart: hear and read any Pinyin with the right sounds and tones, and about 100 words.

At ~1 lesson a day the chart takes about 4 weeks (the mixed lessons may need a second go).
