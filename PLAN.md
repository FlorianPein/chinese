# Learning Plan: Mandarin through the Pinyin chart

**Learner:** total beginner; explanations in English, pronunciation compared to English *and* German
**Goal:** talking to people. The first step is to hear and say every sound of Mandarin
**Script:** Pinyin only (no characters for now)
**Time:** one lesson is about 8–10 min; skip days, or do several lessons at once

### Decisions

| Topic | Decision |
|-------|----------|
| Course structure | For now the lessons work through the **Pinyin chart** (like the [Yabla chart](https://chinese.yabla.com/chinese-pinyin-chart.php)), block by block. Everything else is in [future plans](#6-future-plans) |
| Lesson size | Small: one block of the chart (e.g. *ba pa ma fa*) and 2–5 words. About 25–35 short steps |
| Words | Chosen by importance, and only from syllables and tones you've already learned (checked automatically) |
| Repetition | From the 2nd lesson on, every lesson starts with a warm-up and mixes in older sounds and words. Finished lessons go into spaced-repetition flashcards |
| Where lessons happen | In the web app ([Learn tab](https://florianpein.github.io/chinese/)). Each lesson also has generated notes in `lessons/` |
| Your answers | Mostly buttons. When you type, `ma1` and `mā` both work; neutral tone is `5` or no number |
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

- **At the start, one block per lesson**, because everything is new: the tones, the puff of air on p/t/k, the chart itself.
- **Hard blocks get more room**: j q x get two lessons (with *i* and with *ü*), z c s and zh ch sh r get five, with an extra lesson just for telling them apart.
- **Later, blocks are combined**: once you know all the initials, a new final like *ei* or *eng* is one new idea, so it's taught across the whole chart in one lesson.
- **Tones come in the first lessons**: P01 the 1st and 4th tones (and the light neutral tone in *māma*), P02 the 3rd, P03 the 2nd. P04 is about the neutral tone in little grammar words.
- **Tone changes** are taught where they first come up: *bù → bú* before a 4th tone (P08), *yī → yí* (as soon as *yí gè* appears), and two 3rd tones in a row (*nǐ hǎo*, P20 at the latest).

**The order: 48 lessons in 10 topics.** The full list, with the chart showing which lesson teaches each of the 404 syllables, is in **[CHART.md](CHART.md)** (generated from `data/course.json`).

| Topic | Lessons | What's new | Example words |
|-------|---------|-----------|---------------|
| The a row and the four tones | P01–P03 | ba pa ma fa · da ta na la · ga ka ha; tones | `bàba`, `māma`, `tā`, `dà`, `nǎ` |
| e, o and the neutral tone | P04–P06 | de le ne me · ge ke he · bo po mo fo, wo | `de`, `ma`, `hē`, `gēge`, `wǒ` |
| i, u and ü | P07–P09 | bi di ni, yi · bu du gu, wu · nü lü, yu | `nǐ`, `yī`, `bù`, `wǔ`, `yú` |
| j q x | P10–P11 | ji qi xi · ju qu xu | `qī`, `jǐ`, `qù` |
| z c s and zh ch sh r | P12–P16 | zi ci si · zhi chi shi ri · their a, e, u rows; er | `sì`, `shì`, `chī`, `chá`, `zhè`, `èr` |
| ai ei ao ou | P17–P23 | the diphthongs | `lái`, `mǎi`, `zài`, `méi`, `hǎo`, `dōu` |
| -n and -ng | P24–P31 | an en ang eng ong | `kàn`, `hěn`, `rén`, `shénme`, `néng` |
| Finals starting with i | P32–P39 | ia ie iao iu ian in ing iang iong | `jiā`, `xièxie`, `jiào`, `yǒu`, `míngzi` |
| Finals starting with u | P40–P46 | ua uo uai ui uan un uang | `shuō`, `duì`, `shuǐ`, `xǐhuan`, `wèn` |
| Finals starting with ü | P47–P48 | üe üan ün | `xué`, `yuè`, `yuǎn` |

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

## 3. The first two lessons

### P01: ba pa ma fa (≈ 29 steps, 10 min)

**Block:** `a` with b p m f, and `a` on its own. **Tones:** 1st and 4th; the neutral tone is introduced only as "short and light" for *māma* and *bàba*.

| Part | Slides |
|------|--------|
| 1. The chart | **tip**: initial + final + tone; today's block; the *a* of *Vater* / *father* |
| 2. b vs p | **tip** (the puff of air, hand in front of the mouth) → **listen** *bā/pā* → **same or different** *bà/pà* → **listen** *bā/pā/mā* |
| 3. Tones | **tip**: *ma* in all four tones, just listening → **tip** 1st tone → **tip** 4th tone → **chart** ba pa ma fa × tones 1 and 4 |
| 4. Practise the block | 3× **which tone** · **read and listen** *fà* · **match sounds** · **listen and type** *pà* |
| 5. Words | **new** `bā` (eight) · **new** `pà` (to be afraid) · **meaning** · **tip** neutral tone · **new** `māma` (mum) · **new** `bàba` (dad) · **match** · **say it in Pinyin** · **type it** |
| 6. First sentence | **new** *Bàba pà.* (Dad is scared.) · **build** · **same or different** · **say it aloud** ×2 |

### P02: da ta na la (≈ 33 steps, 10 min)

**Block:** `a` with d t n l. **Tone:** the 3rd (low), next to the 1st and 4th.

| Part | Slides |
|------|--------|
| 1. Warm-up (P01) | **tip** with P01's block → **listen** *bà/pà* → **meaning** *māma* (audio) → **which tone** *fā* → **type it** *pà* |
| 2. d vs t | **tip** (same puff as b/p; n and l as in English/German) → **listen** *dā/tā* → **same or different** *dà/tà* → **listen** *nà/là/dà* |
| 3. 3rd tone | **tip** 3rd tone → **chart** da ta na la × tones 1, 3, 4 |
| 4. Practise the block | 3× **which tone** (one on an old syllable: *pǎ*) · **read and listen** *lǎ* · **match sounds** · **listen and type** *dǎ* |
| 5. Words | **new** `tā` (he / she) · **new** `dà` (big) · **meaning** · **new** `nà` (that) · **new** `nǎ` (which?) · **listen** *nǎ/nà* · **say it in Pinyin** · **match** (with *bàba*) |
| 6. Sentences | **new** *Tā pà.* · **new** *Tā bàba pà.* (His dad is scared.) · **build** · **meaning** (audio) |
| 7. Mixed recap | **type it** *bàba* · **listen** *mā/mǎ/mà* · **listen and type** *tā* · **say it aloud** |

Why these words: *bàba*, *māma* and *tā* are among the first words anyone needs; *bā* starts the numbers; *pà* gives a first verb, so you can make a sentence. *dà*, *nà* and *nǎ* are very common, and *nà* / *nǎ* differ only in the tone, which is exactly what P02 is about.

---

## 4. Repetition and tracking words

- **In the lessons:** every lesson after P01 starts with a warm-up on earlier sounds and words, and mixes old words into its exercises and sentences.
- **Flashcards:** a finished lesson's words and phrases go into the **Review** tab (spaced repetition: read, listen, and type it in Pinyin).
- **Words you've seen:**
  - the app's **Words** tab lists every word and phrase from the lessons you've finished in that browser;
  - **[WORDS.md](WORDS.md)** lists every word per lesson and marks it *seen* once the lesson is in `data/progress.json`. Say *"I finished P01"* and Claude updates it. New lessons are planned from this list: no word is taught twice, and recaps use words you've seen.
- **Weak spots** (sounds or words that keep going wrong) go in [PROGRESS.md](PROGRESS.md), and the next lessons repeat them more.

---

## 5. Tools in this repository

| Tool | What it is |
|------|------------|
| **Web app** (`docs/`, GitHub Pages) | **Learn**: the lessons in chart order. **Review**: flashcards. **Words**: everything you've seen. **Tones**: a tone-hearing quiz. **Listen**: all audio of a lesson. Progress is saved in your browser (export/import in ⚙︎) |
| **Course** (`data/course.json`) | The chart (initial groups, finals) and all 48 lessons: blocks, new tones, focus, candidate words |
| **Lessons** (`data/P01.json`, …) | A built lesson's words, phrases (with hidden characters) and its exact slides |
| **Progress** (`data/progress.json`) | The lessons you've done, for WORDS.md and CHART.md |
| **Build** (`tools/build.py`) | Checks everything (each chart block taught once, every word only uses sounds taught by then, no word tested before it's taught, …), makes the audio, writes the app data, lesson notes, CHART.md and WORDS.md |
| **Audio** (`docs/audio/`) | One MP3 per word, phrase and sound, made offline and tone-checked |

```
PLAN.md  README.md  PROGRESS.md  CHART.md  WORDS.md
data/      course.json  P01.json  P02.json  progress.json
lessons/   P01.md  P02.md          ← generated notes
docs/      index.html  cards.json  audio/
tools/     build.py  chart.py  pinyin.py
archive/   earlier versions of the course
```

---

## 6. Future plans

Moved out of the course for now. They come back once the chart is done (or earlier, mixed in, if you want a break from sounds).

**Conversation units** (the earlier Track B). By the end of the chart you'll know about 170 words, many of them from these units (*nǐ*, *hǎo*, *xièxie*, *jiào*, *míngzi*, *péngyou*, *xǐhuan* …), so the units can go faster.

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

- **After P03:** all four tones, and the a row of the easy initials.
- **After P16:** every initial, including j q x and z c s / zh ch sh r.
- **After P31:** -n and -ng; you can read most syllables you meet.
- **After P48:** the whole chart: read any Pinyin aloud with the right sounds and tones, and about 170 words.

At ~1 lesson a day the chart takes about 7–8 weeks.
