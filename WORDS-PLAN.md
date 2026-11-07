# Plan: Word flashcards (Anki-style)

A new part of the app for learning **words**: you see the word in characters and Pinyin and hear it, tap to see the English, then say how well you knew it. That answer decides when the word comes back.

Status: **plan only**, nothing built yet. The open questions are at the end.

---

## 1. Where it lives

A new **Words** tab in the existing app (`docs/index.html`), between *Practice* and *Listen*. That way it:

- works on the phone like the rest, offline after the first load
- uses the same offline voice and tone-checked audio as the lessons (`tools/build.py`)
- syncs between devices through the `progress` branch, like lessons
- appears in **Copy progress for Claude**, so Claude can see which words keep going wrong

This changes two decisions in [PLAN.md](PLAN.md#decisions): *Words: none for now* and *Characters: hidden everywhere*. The sound lessons carry on as they are. Words run alongside them as a separate daily review.

---

## 2. One card

**Front** (the question)

```
        你好
       nǐ hǎo
       ni3 hao3          ← tone numbers, if switched on in ⚙︎
      🔊   🐢
   [ Show answer ]
```

- **Characters**: large, at the top
- **Pinyin** with tone marks, tone numbers small underneath (same setting as the rest of the app)
- **Pronunciation**: the audio plays by itself when the card appears. 🔊 plays it again, 🐢 plays it slowly. On a computer, **P** replays it.
- Tap the card, or press **Space**/**Enter**, to turn it over

**Back** (the answer)

```
        你好
       nǐ hǎo
   hello
   ───────────
   Said "ní hǎo": two 3rd tones in a row, the first becomes a 2nd.
   你 = you · 好 = good

  [Don't know] [Barely know] [Know] [Safely know] [Securely know]
     1 min        10 min       3 d       7 d          1 mo
```

- **English** meaning, plus an optional note (tone changes, a German or English comparison, what the characters mean)
- **Five buttons**. Each one shows **when the word will come back** if you pick it, like Anki, so you always know what a button does. Keys **1–5** on a computer.

---

## 3. When a word comes back

### The idea

Every word keeps an **interval**: how long it waits before you see it again.

- **Don't know** and **Barely know** bring it back **in the same session**, a few cards later
- **Know**, **Safely know** and **Securely know** send it away for **days**
- Each of the top three buttons has its own **ladder** of times. Picking the same button again at the next review moves the word **one step up** that ladder, so the gap grows the more often you know it.

### Suggested times

| Button | Comes back | Pick it again next time… |
|--------|------------|--------------------------|
| **1 Don't know** | in **1 min** (after about 3–5 other cards) | stays at 1 min until you know it. The word starts again from the bottom of the ladders |
| **2 Barely know** | in **10 min** (later this session) | the word's interval is **halved** (a 2-month word drops to 1 month) |
| **3 Know** | **1 d → 3 d → 7 d → 14 d → 1 mo → 2 mo → 4 mo → 8 mo → 1 yr** | one step up each time |
| **4 Safely know** | **3 d → 7 d → 3 wk → 6 wk → 3 mo → 6 mo → 1 yr** | one step up each time |
| **5 Securely know** | **7 d → 1 mo → 3 mo → 6 mo → 1 yr** | one step up each time |

The ladders as days (what the app stores):

```
Know           1  3  7  14  30  60  120  240  365
Safely know    3  7  21  45  90  180  365
Securely know  7  30  90  180  365
```

Roughly, **Know** doubles the gap each time (Anki's *Good* is about ×2.5). **Safely know** and **Securely know** jump further at first (×3 to ×4) and then also slow to about ×2, so even a well-known word is still checked once or twice a year.

### The rules exactly

1. **Moving between buttons.** A word doesn't have to stay on one ladder. When you pick Know, Safely or Securely, the new interval is the **first step on that button's ladder that's longer than the word's current interval**. So moving up never sets a word back, and picking *Know* on a word that's already at 3 months still gives it a longer gap (4 months).
2. **Only real reviews climb.** A word climbs only when you review it on or after the day it was due. When a word comes back in the same session after *Don't know* or *Barely know*, the answer only decides whether it's done for today. Tapping *Know* five times in one sitting doesn't push a word to 2 months.
3. **Done for today.** A word you got wrong leaves the session as soon as you pick Know or higher. It then comes back after its (reset or halved) interval, at least 1 day.
4. **Brand-new words.** The first time you see a word counts as a review: Know → 1 d, Safely → 3 d, Securely → 7 d ("I already knew this one").
5. **Late reviews count fully.** If a 7-day word is reviewed after 12 days and you still know it, it climbs from 12 days, not 7.
6. **A little randomness.** Intervals of 3 days or more are moved by up to ±5%, so words learned together don't always come back on the same day.
7. **Ceiling: 1 year.** No word waits longer than 365 days (can be changed in ⚙︎).
8. **Day boundary at 4 am**, so a late-night session counts as the day before.

### Example

| Review | Button | Interval before | Comes back in |
|--------|--------|-----------------|---------------|
| new word | Know | 0 | 1 d |
| day 1 | Know | 1 d | 3 d |
| day 4 | Safely know | 3 d | 7 d |
| day 11 | Securely know | 7 d | 1 mo |
| day 41 | Know | 1 mo | 2 mo |
| day 101 | Barely know | 2 mo | 10 min, then halved → 1 mo |
| day 131 | Don't know | 1 mo | 1 min, starts again → then 1 d |

### Words that keep going wrong

A word you've got wrong (*Don't know*) **6 times** is marked as a **hard word** (Anki calls it a *leech*). It shows ⚑ on the card, is listed in **Copy progress for Claude**, and Claude can add a memory aid or split it into smaller words.

---

## 4. A day's session

- **Top of the tab:** `Due 18 · New 5 · Learning 2`, and a **Start** button
- **Order:** words that came back after a mistake first (once their minutes are up), then due words (most overdue first), then new words mixed in among them
- **New words per day: 10** (setting, 0–30). Rule of thumb: daily reviews settle at roughly **8–10× the new words per day**, so 10 new words means about 80–100 reviews (≈ 10–15 min).
- **Reviews per day: no limit** by default (setting), so nothing piles up unseen
- **End screen:** how many you reviewed, how many you knew, and when the next words are due ("12 tomorrow")

That fits the [daily routine](README.md#daily-routine): Words first, then Practice or a lesson.

---

## 5. The words

New file `data/words.json`, one entry per word:

```json
{
  "id": "nihao",
  "hanzi": "你好",
  "pinyin": "nǐ hǎo",
  "english": "hello",
  "note": "Said \"ní hǎo\": two 3rd tones in a row, the first becomes a 2nd.",
  "parts": "你 = you · 好 = good",
  "deck": "U01",
  "order": 1
}
```

- **First deck:** about 100 words for the first conversation units (hello and politeness, who are you, questions, numbers), including the words from the old lessons in `archive/` (*wǒ*, *nǐ*, *hǎo*, *xièxie*, *shì*, *bù*, *hē*, *jiào*, *míngzi* …)
- **New words come in `order`**, so the first ones are the most useful, and a deck can be switched on or off in ⚙︎
- Claude adds words to the file when you ask (*"add the words for family"*) and rebuilds

### Build (`tools/build.py`)

- **Checks:** every word has characters, Pinyin with valid tone marks and English; ids are unique; the number of syllables matches the number of characters; the voice can say every syllable (same rule as for lesson words)
- **Audio:** one MP3 per word from the same offline voice, with the spoken tone changes (*nǐ hǎo* → *ní hǎo*, *bù shì* → *bú shì*), tone-checked like the lesson audio. Files go to `docs/audio/w-<id>.mp3`
- **Output:** the words go into the app's data (`docs/words.json`, loaded by the Words tab)

---

## 6. What the app stores

Per word, in the existing progress state, under a new key `words` (the old `cards` key stays for older copies of the app):

```json
"words": {
  "nihao": { "iv": 7, "due": "2026-11-14", "last": "2026-11-07", "reps": 4, "lapses": 0, "at": "2026-11-07T18:02:11" }
}
```

| Field | Meaning |
|-------|---------|
| `iv` | current interval in days (0 = learning) |
| `due` | the day it's next shown |
| `last` | the day of the last real review |
| `reps`, `lapses` | how often reviewed, how often *Don't know* |
| `at` | time of the last change, for sync |

- **Sync:** `words` is added to the synced keys. When two devices disagree, the word with the later `at` wins (the same rule the old flashcards used).
- **Log:** each answer adds `{t: "word", id, g}` (g = 1–5) to the activity log, so **Copy progress for Claude** can report the hard words, and `tools/progress.py` can show them in PROGRESS.md.

---

## 7. Steps to build it

| Step | What | Done when |
|------|------|-----------|
| 1 | `data/words.json` with the first ~100 words; checks and audio in `tools/build.py` | build passes, every word has tone-checked audio |
| 2 | The scheduler as one small function, `schedule(word, button, today)`, with the ladders from section 3 as a table at the top | a test script runs the example in section 3 and the rules 1–8 |
| 3 | The **Words** tab: card, flip, five buttons with their times, the session queue, end screen | a full session works on the phone and with keys 1–5 |
| 4 | Sync, log and **Copy progress for Claude**; hard words in `tools/progress.py` | progress made on the phone shows up on the computer |
| 5 | Settings (new words per day, decks, ceiling, autoplay); README, PLAN.md decisions | docs describe the tab |

### Later, if useful

- **The other way round:** English → say or pick the Chinese
- **Listening cards:** audio only, no characters or Pinyin, for training the ear
- **Typing the Pinyin** instead of just revealing (`ni3 hao3` or `nǐ hǎo` both accepted, as in the lessons)
- **Character cards:** single characters with their parts, once there are enough words

---

## 8. Open questions

1. **A Words tab in the existing app**, or a separate page?
2. **Which words first:** the conversation-unit words (hello, names, questions, numbers) or the HSK 1 list?
3. **New words per day:** 10, or start smaller with 5?
4. **Characters on the front from the start**, or Pinyin first and characters only on the back?
5. **The times above:** shorter at the start (e.g. Know = 1 d → 2 d → 4 d) if words fade too fast, or keep them as suggested?
