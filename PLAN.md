# Learning Plan: Mandarin through the Pinyin chart

**Learner:** total beginner; explanations in English, pronunciation compared to English *and* German
**Goal:** talking to people. The first step is to hear and say every sound of Mandarin
**Script:** Pinyin only (no characters for now)
**Time:** one lesson is about 10–12 min; skip days, or do several lessons at once
**Focus for now:** listening only: telling the tones and the sounds apart. No words yet

### Decisions

| Topic | Decision |
|-------|----------|
| Course structure | For now the lessons work through the **Pinyin chart** (like the [Yabla chart](https://chinese.yabla.com/chinese-pinyin-chart.php)). First **one group of initials per lesson** (P01–P06), then **two recap lessons**, then **mixed lessons** that combine several groups and finals and get faster. Everything else is in [future plans](#6-future-plans) |
| Lesson size | P01–P08: one group of initials with one final (e.g. *bo po mo fo*). From P09: 3–15 chart blocks around one contrast (e.g. *an vs ang* everywhere). About 37 short steps |
| Exercises | All **listening**: which tone, which sound, same or different, odd one out, two to four sounds in a row, match the sounds, write what you hear. Speaking comes back later |
| Words | **None for now** (decided 2026-10-24): the lessons are only sounds and tones, and the time words took goes into extra listening exercises. Words come back with the conversation units |
| Repetition | From the 2nd lesson on, every lesson starts with a warm-up on earlier sounds and mixes them into its exercises. Finished lessons' sounds go into the app's **Practice** drill |
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
- **All four tones from the start, never separated**: P01 introduces all four side by side. From then on every chart shows all four tones and every tone question offers all four, because the tones are learned by hearing them against each other. Each early lesson also trains one hard contrast: P02 the 2nd against the 3rd, P03 the 4th against the 3rd (low, dips and comes back up) and the 1st (stays high).
- **Tones in a row**: from P01 on, lessons play two to four syllables one after another (*mō mǒ*, *bō pǒ mò*), so you learn to catch each tone on the way, not only one syllable at a time.
- **The neutral tone and tone changes** (*bù → bú*, *yī → yí*, two 3rd tones in a row) only happen inside words, so they wait for the words.

**The order: 24 lessons in 7 topics.** The full list, with the chart showing which lesson teaches each of the 404 syllables, is in **[CHART.md](CHART.md)** (generated from `data/course.json`).

| Topic | Lessons | What's new |
|-------|---------|-----------|
| One group of initials per lesson | P01 | bo po mo fo · wo; the four tones |
| | P02 | de te ne le · e; d vs t; 2nd vs 3rd |
| | P03 | ge ke he; 4th vs 3rd and 1st |
| | P04 | ze ce se; s is always sharp (German ß) |
| | P05 | zhe che she re; z vs zh, s vs sh, r vs l |
| | P06 | ji qi xi; x = German *ich* |
| Recap | P07 | the puff of air: b/p d/t g/k z/c zh/ch j/q |
| | P08 | z, zh or j? c, ch or q? s, sh or x? |
| Simple finals, mixed | P09–P12 | the a row everywhere · zi zhi, er · i vs u · u vs ü |
| ai ei ao ou, mixed | P13–P15 | ai vs ei · ao vs ou · z c s vs zh ch sh with all four |
| -n and -ng, mixed | P16–P18 | an vs ang · an ang ong with z/zh · en vs eng |
| Finals starting with i, mixed | P19–P21 | ia ie iao · iu ian · in ing iang iong |
| Finals starting with u and ü, mixed | P22–P24 | ua uo uai · ui uan un · uang weng and üe üan ün |

What each lesson drills is adjusted to what you find hard (see `PROGRESS.md`).

---

## 2. Slide types

A lesson is a sequence of slides. Some teach, most are exercises. Every slide that shows a sound can play it.

### Teaching slides

| Slide | What it does | Status |
|-------|--------------|--------|
| **tip** (`intro`) | A short explanation with English and German comparisons, a tone diagram, and rows of sounds to tap (▶ plays a row) | ✅ |
| **chart** (`chart`) | The lesson's block as a grid: syllables down, tones across. Tap a square, a row (one syllable in every tone) or a column (one tone down the block) | ✅ |
| **new word** (`new`) | The word with audio and slow audio, its meaning, a pronunciation note, and its syllable in all four tones | not used for now |
| **new phrase** (`new`) | A short sentence with a word-by-word breakdown you can tap | not used for now |

### Exercises on sounds

| Slide | What you do | Answer | Status |
|-------|-------------|--------|--------|
| **listen** (`hear`) | Hear a sound, pick the Pinyin (e.g. *bā* or *pā*) | buttons | ✅ |
| **which tone** (`tone`) | Hear a sound, pick its tone | tone buttons | ✅ |
| **same or different** (`same`) | Hear two sounds, say whether they're the same (*bà* / *pà*) | 2 buttons | ✅ |
| **odd one out** (`odd`) | Hear three sounds, two of them the same; pick the one that's different (*bō bō pō*) | 3 buttons | 🆕 |
| **in a row** (`order`) | Hear 2–4 sounds one after another, pick the Pinyin that says them in that order (*mō mǒ* or *mǒ mō*?) | buttons | 🆕 |
| **read and listen** (`audio`) | See the Pinyin, listen to 2–3 sounds, pick the one that says it | buttons | ✅ |
| **match sounds** (`match`, sound mode) | Match 4 sounds to their Pinyin | tapping pairs | ✅ |
| **listen and type** (`type`, from audio) | Type what you hear | `ma1` or `mā` | ✅ |
| **say it aloud** (`speak`) | Listen, repeat, record yourself and compare with the original | — | ✅ |

### Exercises on words (not used for now)

The app still has them, for when words come back: **meaning** (`meaning`), **say it in Pinyin** (`pinyin`), **match the pairs** (`match`, Pinyin ↔ meaning), **build the sentence** (`build`) and **type it** (`type`, from English).

Every exercise you get wrong comes back at the end of the lesson (up to twice).

### Ideas for later

| Slide | What you'd do | When it's useful |
|-------|---------------|------------------|
| **spell it** | Hear a syllable, build it from buttons: initial + final + tone (no typing) | Once there are many finals (from P17) |
| **speed round** | 10 quick tone or sound questions in a row | Review lessons |
| **chart review** | The whole chart so far, learned blocks highlighted, tap anything | After each topic |
| **tone pairs** | Hear two syllables, pick both tones (*3rd + 4th*) from a grid | Once the tones are steady (after P08) |
| **fill the gap**, **listen and answer**, **dialogue** | Word and sentence exercises | With the conversation units |

---

## 3. The first lessons

All eight are listening only: no words, no speaking. Each has the same parts: a warm-up on the lesson before, the new sounds one at a time with English and German comparisons, the chart block, a practice round (one old sound mixed in), and an **extra listening** round where the words used to be: odd one out, sounds in a row, and more tone and sound questions, aimed at what you find hard.

### P01: bo po mo fo · wo (37 steps, ≈ 12 min)

**Blocks:** `o` with b p m f, and `wo`. **Tones:** all four.

| Part | Slides |
|------|--------|
| 1. The chart | **tip**: initial + final + tone; today's block; the *o* after b p m f has a little *w* in it (*bo* ≈ *b-wo*), open like British *law* / German *Sonne* |
| 2. b vs p | **tip** (the puff of air, hand in front of the mouth) → **listen** *bō/pō* → **same or different** *bò/pò* → **listen** *bó/pó/mó* → **odd one out** *bō bō pō* |
| 3. Tones | **tip**: *mo* in all four tones, just listening → **tip** for each tone, each with *mō mó mǒ mò* to compare → **same or different** *mó/mǒ* → **chart** bo po mo fo × all four tones |
| 4. Practise the block | 4× **which tone** · **same or different** *pō/pò* · **read and listen** *pǒ* · **match sounds** (one per tone) · **listen** *mó* (from all four) · **listen and type** *pò* |
| 5. wo | **tip**: wo in all four tones, mo/wo, bo/wo → **which tone** *wǒ* → **listen** *wò* (from *mò wò bò*) |
| 6. Tones in a row | **tip**: two or three sounds in a row → **in a row** *mō mǒ*, *pò pó*, *bō pǒ mò* · **odd one out** *fó/fǒ*, *mō/mò*, *pǒ/bǒ* · **which tone** *fó* · **same or different** *wó/wǒ* · **listen** *fó* (from all four) · **match sounds** · **listen and type** *wǒ* |

### P02: de te ne le · e (38 steps, ≈ 10 min)

**Blocks:** `e` with d t n l, `e` alone, and `me` (only mentioned: it's always neutral, so it waits for words). **Tones:** all four; the contrast to train is the 2nd (rising) against the 3rd (low).

| Part | Slides |
|------|--------|
| 1. Warm-up (P01) | **tip** with P01's block in all four tones → **listen** *bò/pò* → **which tone** *fó* → **odd one out** *mǒ/mó* → **in a row** *wǒ pò* |
| 2. The vowel e | **tip** (say *o*, then smile: a deep *uh*; not the e of *bed* / *Bett*) with *ē é ě è* and *wo* against *e* → **listen** *wò/è* → **same or different** *wō/ē* → **odd one out** *é/wó* |
| 3. d vs t | **tip** (same puff as b/p) → **listen** *dè/tè* → **same or different** *dé/té* → **listen** *nè/lè/dè* → **odd one out** *dē/tē* |
| 4. 2nd or 3rd? | **tip** (where the tone starts: mid and up, or low) with *dé/dě*, *né/ně*, *mó/mǒ* → **same or different** *lé/lě* → **chart** de te ne le × all four tones |
| 5. Practise the block | 4× **which tone** (one old: *pǒ*) · **same or different** · **read and listen** *lě* · **match sounds** · **listen** *né* (from dé té né lé) · **listen and type** *dě* |
| 6. Extra listening | **tip**: rising and low in a row → **in a row** *né ně*, *lě dé*, *tē dè ě* · **odd one out** *ě/é*, *nè/lè* · 2× **which tone** · **listen** *té* · **match sounds** · **same or different** *tě/dě* · **listen and type** *è* |

### P03–P08 in short

| Lesson | Explanations | Contrasts drilled | Extra listening |
|--------|--------------|-------------------|-----------------|
| P03 | 3rd vs 4th first (your weak spot); g/k (the puff a third time); h is rough like German *ach*; 4th vs 1st (both start high: stay or drop) | gē/kē, kē/hē, lě/lè, kē/kè | 3rd, 4th and 1st in a row (*hě hè*, *gē kè*, *lè ně hē*); odd one out *kè/kě*, *hē/hè*, *gě/kě* |
| P04 | z = soft ts (German *Zeit*, no puff); c = ts with a puff, never k or s; s always sharp like *ß* | dé/zé, zè/cè, tè/cè, zè/cè/sè | same tone, different initial: odd one out *cè/zè*, *sē/cē*, *té/cé*; in a row *zè cè*, *dē zě cè* |
| P05 | zh ch sh r with the tongue curled back (German *dsch, tsch, sch*; r like English *run*) | zhè/chè, ze/zhe, ce/che, se/she, rè/lè | bright or dark: odd one out *zhè/zè*, *shé/sé*, *chě/zhě*; in a row *sē shē*, *zhē ré shè*; r vs l |
| P06 | the vowel i; j q x with a flat tongue; x = German *ich*; three tongue positions side by side | jì/qì, she/xi, sè/shè/xì | flat, curled or at the teeth: odd one out *xì/shè*, *jǐ/qǐ*; in a row up to four (*jī xí qǐ jì*) |
| P07 | recap: the six puff pairs, then puff and tone at once | b/p d/t g/k z/c zh/ch j/q, random order | puff in a row: *kě lè*, *pō té kě*, *jì dě*; odd one out *dè/tè*, *qí/jí* |
| P08 | recap: three tongue positions; s/sh/x and r | z/zh/j, c/ch/q, s/sh/x, faster | three in a row: *zē zhé jǐ*, *shè sē xǐ ré*; odd one out *zhè/zè*, *shě/sě*, *cé/ché* |

**Audio note:** *o* on its own (the interjection *ó / ò*, "oh?") isn't used: the speech model says it unclearly. Neutral syllables aren't played on their own, because alone they come out with a full tone. Syllables the model never heard in a tone (*fō fǒ fò*, *dě dè*, *tē té tě*, …) are pitch-edited from a tone it knows (*fó*), because said directly they sound like another syllable.

---

## 4. Repetition and tracking progress

- **In the lessons:** every lesson after P01 starts with a warm-up on the sounds of the lesson before, and mixes older sounds into its exercises.
- **Practice:** the app's **Practice** tab is an endless listening drill with the sounds of every lesson you've finished: which tone, which sound (from others with the same tone, similar ones first), or same or different. A sound you get wrong comes back a few questions later.
- **Weak spots** (sounds and tones that keep going wrong) go in [PROGRESS.md](PROGRESS.md), and the next lessons repeat them more.
- **How Claude learns your progress:** the app keeps a log of finished lessons (with scores), every wrong answer (what was asked and what you picked, in lessons and in Practice) and how many Practice questions you answered. **⚙︎ → Copy progress for Claude** (also on the *Lesson complete* screen) copies a short summary plus the new log entries; paste it into a chat, or turn on sync. Claude merges it with `tools/progress.py` into `data/progress.json` and `data/progress-log.jsonl`, updates PROGRESS.md, and plans the next lessons around your mistakes.

---

## 5. Tools in this repository

| Tool | What it is |
|------|------------|
| **Web app** (`docs/`, GitHub Pages) | **Learn**: the lessons in chart order. **Practice**: a listening drill with the sounds you've learned. **Listen**: all audio of a lesson. Progress is saved in your browser and can be synced through GitHub (⚙︎) |
| **Course** (`data/course.json`) | The chart (initial groups, finals) and all 24 lessons: blocks, focus |
| **Lessons** (`data/P01.json`, …) | A built lesson's exact slides (and its words, once there are any) |
| **Progress** (`data/progress.json`) | The lessons you've done, for CHART.md |
| **Build** (`tools/build.py`) | Checks everything (each chart block taught once, no lesson plays a syllable before it's taught, every tone question has all four tones, …), makes the audio, writes the app data, lesson notes and CHART.md |
| **Audio** (`docs/audio/`) | One MP3 per sound, made offline and tone-checked |

```
PLAN.md  README.md  PROGRESS.md  CHART.md
data/      course.json  P01.json … P08.json  progress.json
lessons/   P01.md … P08.md          ← generated notes
docs/      index.html  cards.json  audio/
tools/     build.py  chart.py  pinyin.py
archive/   earlier versions of the course
```

---

## 6. Future plans

Moved out of the course for now. They come back once the chart is done (or earlier, mixed in, if you want a break from sounds).

**Words and conversation units** (the earlier Track B). The words that used to be in P01–P08 (*wǒ*, *hē*, *kě*, *gēge*, *zhège*, *qìchē* …) and the planned ones (*nǐ*, *hǎo*, *xièxie*, *jiào*, *míngzi*, *péngyou*, *xǐhuan* …) come back here, together with the neutral tone and the tone changes. By then you can hear every sound, so the units can go faster.

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
- **Chart checkpoints:** a short review lesson after each topic, if Practice isn't enough

**Later still:** characters, chat role-plays with Claude, an in-app chart of every syllable with audio.

The first versions of the tone lessons (A01-L01, A01-L02) and of U01-L01 are in `archive/`. Their explanations and phrases get reused.

---

## 7. Routine and milestones

| Day type | What to do |
|----------|------------|
| **Normal day (10–15 min)** | A few minutes of Practice, then 1 lesson |
| **Busy day (2–5 min)** | Practice only |
| **Free day (30 min+)** | Practice, then 2–3 lessons |
| **Back after a break** | Practice, then the last lesson again |

Rule of thumb: **if a lesson came out below about 70% right first time, do it again before the next one.**

- **After P01:** all four tones. **After P03:** the hardest tone contrasts (2nd/3rd, 1st/4th).
- **After P06:** every initial, including z c s, zh ch sh r and j q x. **After P08:** you can hear them apart in a random mix.
- **After P18:** every simple final, ai ei ao ou, and -n / -ng; you can hear most syllables you meet.
- **After P24:** the whole chart: hear and read any Pinyin with the right sounds and tones. Then words.

At ~1 lesson a day the chart takes about 4 weeks (the mixed lessons may need a second go).
