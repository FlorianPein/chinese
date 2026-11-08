# Plan: Word flashcards (Anki-style)

A new part of the app for learning the **most common Chinese words**: you hear the word and see it in Pinyin and characters, tap to see the English, then say how well you knew it. That answer decides when the word comes back.

Status: **built**: the **Words** tab in the app. [Section 7](#7-whats-where) says where everything is.

---

## 1. Where it lives

A new **Words** tab in the existing app (`docs/index.html`), between *Practice* and *Listen*. That way it:

- works on the phone like the rest, offline after the first load
- uses the same offline voice and tone-checked audio as the lessons (`tools/build.py`)
- syncs between devices through the `progress` branch, like lessons
- appears in **Copy progress for Claude**, so Claude can see which words keep going wrong

This changes two decisions in [PLAN.md](PLAN.md#decisions): *Words: none for now* and *Characters: hidden everywhere*. Both are updated there. The sound lessons carry on as they are; words run alongside them.

---

## 2. One card

**Front** (the question): sound on top, then Pinyin, then characters.

```
          🔊   🐢           ← plays by itself when the card appears
        nǐ hǎo
        ni3 hao3            ← tone numbers, if switched on in ⚙︎
         你好
    [ Show answer ]
```

- **Sound**: plays automatically. 🔊 plays it again, 🐢 slowly. **P** replays it on a computer.
- **Pinyin** with tone marks, tone numbers small underneath (same setting as the rest of the app)
- **Characters** underneath
- Tap the card, or press **Space**/**Enter**, to turn it over

**Back** (the answer)

```
          🔊   🐢
        nǐ hǎo
         你好
   hello
   ┃ Nǐ hǎo, wǒ jiào Xiǎomíng.
   ┃ 你好，我叫小明。
   ┃ Hello, I'm Xiaoming.
   ───────────
   Said "ní hǎo": two 3rd tones in a row, the first becomes a 2nd.
   你 = you · 好 = good

  [Don't know] [Barely know] [Know] [Safely know] [Securely know]
     1 min        10 min       3 d       7 d          14 d
```

- **English** meaning
- **An example sentence**: Pinyin, characters and English, with the word underlined in both the Pinyin and the characters. Short, everyday sentences, mostly built from common words.
- An optional note (tone changes, a German or English comparison, what the characters mean, an example for words like 的 or 了 that don't translate on their own)
- **Five buttons**, each showing **when the word comes back** if you pick it. Keys **1–5** on a computer.

---

## 3. When a word comes back

### One ladder

Every word sits on one step of a ladder. The step is how long it waits before you see it again:

```
step     1     2     3     4      5      6      7      8      9
wait    1 d   3 d   7 d   14 d   1 mo   2 mo   4 mo   8 mo   1 yr
        └start┘└──── days ────┘  └──────────── months ────────────┘
```

Each button moves the word **up**, **down**, or **keeps** it where it is. How far depends on how long the word has been waiting already:

| Button | Start (1 d) | Days (3 d – 14 d) | Months (1 mo and more) |
|--------|-------------|-------------------|------------------------|
| **1 Don't know** | again in **1 min**, then back to **1 d** | same | same |
| **2 Barely know** | again in **10 min**, then **1 d** | again in **10 min**, then **2 steps down** | again in **10 min**, then **2 steps down** |
| **3 Know** | **1 step up** | **stays** (not advancing) | **1 step down** (shorter) |
| **4 Safely know** | **2 steps up** | **1 step up** | **stays** (not advancing) |
| **5 Securely know** | **3 steps up** | **2 steps up** | **1 step up** |

So:

- **Know** only gets a word off the first day. After that, *Know* keeps it coming back at the same gap, and on months it brings it back sooner.
- **Safely know** moves a word through the days, but on months it no longer advances it.
- Only **Securely know** moves a word through the months.

### When the word reappears, for every button

Find the word's current wait on the left; the row shows when it comes back for each button. These are also the times printed on the buttons.

| Waiting now | Don't know | Barely know | Know | Safely know | Securely know |
|-------------|------------|-------------|------|-------------|---------------|
| **new word** | 1 min, then 1 d | 10 min, then 1 d | 1 d | 3 d | 7 d |
| **1 d** | 1 min, then 1 d | 10 min, then 1 d | 3 d | 7 d | 14 d |
| **3 d** | 1 min, then 1 d | 10 min, then 1 d | 3 d | 7 d | 14 d |
| **7 d** | 1 min, then 1 d | 10 min, then 1 d | 7 d | 14 d | 1 mo |
| **14 d** | 1 min, then 1 d | 10 min, then 3 d | 14 d | 1 mo | 2 mo |
| **1 mo** | 1 min, then 1 d | 10 min, then 7 d | 14 d | 1 mo | 2 mo |
| **2 mo** | 1 min, then 1 d | 10 min, then 14 d | 1 mo | 2 mo | 4 mo |
| **4 mo** | 1 min, then 1 d | 10 min, then 1 mo | 2 mo | 4 mo | 8 mo |
| **8 mo** | 1 min, then 1 d | 10 min, then 2 mo | 4 mo | 8 mo | 1 yr |
| **1 yr** | 1 min, then 1 d | 10 min, then 4 mo | 8 mo | 1 yr | 1 yr |

*"1 min, then 1 d"*: the word comes back about 1 minute later in the same session (after 3–5 other cards), and keeps coming back until you pick *Know* or higher. Then it's done for today and returns after the second time.

### Rules

1. **Only due reviews move the ladder.** When a word comes back in the same session after *Don't know* or *Barely know*, your answer only decides whether it's done for today. It doesn't climb.
2. **Late reviews:** the wait counts from the day you actually review it, by the table above. Reviewing a 7-day word after 12 days and picking *Safely know* brings it back 14 days later; being late gives no bonus and no penalty.
3. **No spreading out:** words learned together may come back on the same day. That's fine: do as many as you can, and the rest are still waiting next session.
4. **No daily limits.** A session has no fixed end. Stop whenever you like; words you didn't get to stay due, and words waiting their 1 or 10 minutes come first next time.
5. **Day boundary at 4 am**, so a late-night session still counts as that day.
6. **Ceiling: 1 year.**

### Example

| Review | Button | Waiting before | Comes back in |
|--------|--------|----------------|---------------|
| new word | Know | – | 1 d |
| day 1 | Know | 1 d | 3 d |
| day 4 | Know | 3 d | 3 d (stays) |
| day 7 | Safely know | 3 d | 7 d |
| day 14 | Securely know | 7 d | 1 mo |
| day 44 | Safely know | 1 mo | 1 mo (stays) |
| day 74 | Securely know | 1 mo | 2 mo |
| day 134 | Know | 2 mo | 1 mo (shorter) |
| day 164 | Barely know | 1 mo | 10 min, then 7 d |
| day 171 | Don't know | 7 d | 1 min, then 1 d |

### Words that keep going wrong

A word you've marked *Don't know* **6 times** becomes a **hard word** (Anki calls it a *leech*). It shows ⚑ on the card, is listed in **Copy progress for Claude**, and Claude can add a memory aid or a better example.

---

## 4. New words mixed in with old ones

New words keep coming **as long as you keep going**, mixed in among the old words. How many depends on how many old words are **due right now**: many due means almost no new words, few due means many new words, none due means only new words.

**Order of the next card:**

1. A word you just got wrong whose 1 or 10 minutes are up
2. Otherwise, by the mix below: a due word (the one waiting longest first) or a new word (most common first)

**The mix** (counted again after every card):

| Old words due now | New words |
|-------------------|-----------|
| 50 or more | 1 in every 20 cards |
| 20–49 | 1 in every 10 cards |
| 10–19 | 1 in every 5 cards |
| 5–9 | 1 in every 3 cards |
| 1–4 | every 2nd card |
| 0 | only new words |

**One brake: at most 5 open words.** A word is *open* from the moment you say *Don't know* until you pick *Know* or better when it comes back **on a later day** (picking *Know* on the repeat in the same session only finishes it for today). Words waiting their 1 or 10 minutes count as open too. While 5 words are open, no new words come in: the open ones cycle (again after 1 minute, then the next day) until you know some of them, and each one you know lets one new word in. Among due words, the open ones come first. If only open words are left and none is due, the session ends; the tab says why.

Because the mix is counted after every card, it shifts by itself: a session that starts with 60 due words is almost all review, and as you work them down, more and more new words come in. A day with lots of new words fills the next days with reviews, and those days then automatically bring fewer new ones.

**Top of the tab:** `Due 18 · Learning 2 · Learned 240 of 2000` and a **Start** button. You can stop any time; the screen then shows how many you did and how many are due tomorrow.

---

## 5. The words: most common first

New file `data/words.json`, ordered by **how common the word is in everyday speech**.

- **Order from a word count of film and TV subtitles**: [OpenSubtitles 2018](https://github.com/hermitdave/FrequencyWords) (CC BY-SA 4.0), with traditional forms merged into simplified. It's close to how people talk: its top words are 的, 我, 你, 了, 是, 在, 我们, 他, 吗, 不, 什么, 好, 有, 就, 吧. (The first idea was SUBTLEX-CH, also a subtitle count, but its website can't be reached from the build machine.)
- **Cleaned up:** left out are names, swear words, subtitle artefacts (我要, 我会 are "I want", "I will", not words), written-only words (之, 于, 而), 儿 forms the voice can't say (哪儿: 哪里 is in), and most action-film words (枪, 尸体, 监狱). Words that only make sense together stay together (谢谢, 对不起, 没关系).
- **First batch: 533 words**, then more in batches of about 500 when you get near the end
- **English and notes written for learning:** short meanings, the tone changes, and an example where the word alone doesn't say much (的, 了, 吧, 呢)
- **An example sentence for every word**, written in Pinyin the way the words' own Pinyin is written: tone marks without the 3rd-tone change, but with the changes of 一 and 不 (yí ge, bú shì), and light syllables unmarked (péngyou)

One entry:

```json
{
  "id": "nihao",
  "hanzi": "你好",
  "pinyin": "nǐ hǎo",
  "english": "hello",
  "note": "Two 3rd tones: said ní hǎo.",
  "example": {"hanzi": "你好，我叫小明。", "pinyin": "Nǐ hǎo, wǒ jiào Xiǎomíng.", "english": "Hello, I'm Xiaoming."},
  "rank": 188
}
```

`rank` is the word's place in the subtitle count; the order of the list is the order new words come in. What each character means (你 = you · 好 = good) is added by the build, from the words that are single characters.

### Build (`tools/build.py`)

- **Checks:** every word has characters, Pinyin with valid tone marks and English; ids are unique; one syllable per character; the voice can say every syllable (same rule as for lesson words). The example sentence has all three parts, one syllable per character, and contains the word with the word's own Pinyin (only 一 and 不 may change tone, and a syllable may be light, as in 三个 sān ge)
- **Audio:** one MP3 per word from the same offline voice, with the spoken tone changes (*nǐ hǎo* → *ní hǎo*, *bù shì* → *bú shì*), tone-checked like the lesson audio, in `docs/audio/w-<code points>.mp3` (你好 → `w-4f60-597d.mp3`). In words like *wǒmen* the voice doesn't stop between syllables, so the check splits the word evenly to measure each tone; that's only used to pick the best take. Light (neutral) syllables aren't checked. Where no take clearly has the right tones (35 of 533 words), the card says *The recording may not have every tone right: go by the Pinyin.*
- **Output:** `docs/words.json`, loaded by the Words tab. Each example gets the place of the word in the characters and in the Pinyin, so the card can underline it

---

## 6. What the app stores

Per word, in the existing progress state, under a new key `words` (the old `cards` key stays for older copies of the app):

```json
"words": {
  "你好": { "step": 3, "due": "2026-11-14", "learning": 0, "reps": 4, "lapses": 0, "at": "2026-11-07T18:02:11" }
}
```

| Field | Meaning |
|-------|---------|
| `step` | the step on the ladder (1 = 1 d … 9 = 1 yr) |
| `due` | the day it's next shown |
| `learning` | when it's waiting its 1 or 10 minutes: the time it's back, in ms (else 0) |
| `reps`, `lapses` | how often reviewed, how often *Don't know* |
| `miss` | open: said *Don't know*, not yet known on a later day ([section 4](#4-new-words-mixed-in-with-old-ones)). Cards from before this field count as open while on step 1 |
| `at` | time of the last change, for sync |

- **Sync:** `words` is added to the synced keys. When two devices disagree about a word, the later `at` wins.
- **Log:** answers go into the activity log in batches of 20, `{t: "words", total, grades: [how many of each button], new}`, so a long session doesn't push the lesson mistakes out of the log. Hard words come from each word's `lapses`: **Copy progress for Claude** lists the words forgotten twice or more, and `tools/progress.py` keeps them in `data/progress.json`.

---

## 7. What's where

| Part | File |
|------|------|
| The words | `data/words.json` |
| Checks, audio, app data (`docs/words.json`) | `tools/build.py` |
| When a word comes back, which card is next | `docs/srs.js` |
| Test of every rule and every cell of the table in section 3 | `node tools/test_srs.js` |
| The Words tab | `docs/index.html` |
| Words in Claude's progress summary | `tools/progress.py` |

### Later, if useful

- **The other way round:** English → say or pick the Chinese
- **Listening only:** sound without Pinyin or characters on the front
- **Typing the Pinyin** instead of just revealing (`ni3 hao3` or `nǐ hǎo` both accepted)
- **Single characters** with their parts, once there are enough words
