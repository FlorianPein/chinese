# Plan: Word flashcards (Anki-style)

A new part of the app for learning Chinese words (since 2026-11-22: **the words of the Spoonfed deck, in its order**, see [section 5](#5-the-words-in-the-order-of-the-spoonfed-deck)): you hear the word and see it in Pinyin and characters, tap to see the English, then say how well you knew it. That answer decides when the word comes back.

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
   ┃ Nǐ hǎo, wǒ jiào Xiǎomíng.   🔊
   ┃ 你好，我叫小明。              🐢
   ┃ Hello, I'm Xiaoming.
   ───────────
   [你 nǐ you] [好 hǎo good]      ← tap one to hear it
   Said "ní hǎo": two 3rd tones in a row, the first becomes a 2nd.

  [Don't know] [Barely know] [Know] [Safely know] [Securely know]
     1 min        10 min       3 d       7 d          14 d
```

- **English** meaning
- **An example sentence**: Pinyin, characters and English, with the word underlined in both the Pinyin and the characters. Short, everyday sentences, mostly built from common words. 🔊 plays the sentence, 🐢 slowly.
- **What each character means**, where it's a word of its own (你 = you · 好 = good): one button per character, tap it to hear it.
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

*"1 min, then 1 d"*: the word comes back about 1 minute later in the same session (after 3–5 other cards), and keeps coming back until you pick *Know* or higher. Then it's done for today and returns after the second time. A second *Don't know* sets the word aside until you study it ([section 4](#words-set-aside-dont-know-twice)).

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

## 4. Sessions, and new words

The Words tab has **one button: Start**. A session asks the words that are due and brings new words, in the order of the word list ([section 5](#5-the-words-in-the-order-of-the-spoonfed-deck)), up to **10 new words a day** (⚙︎ → *Words: new words a day*: 5, 10, 15, 20, 30 or 50). When nothing is due and today's new words are done, the button says **10 more new words** and starts a session with 10 more.

**Order of the next card** (`SRS.pickNextOrNew` in `docs/srs.js`):

1. A word you just got wrong whose 1 or 10 minutes are up
2. A due word: first the *open* ones (you said *Don't know* and haven't known them on a later day yet), then words studied but not reviewed yet, then the one waiting longest
3. A new word, while the session still has new words to bring: first a word set aside (see below) that you didn't answer today, then the next word you've never seen
4. If only words waiting their minutes are left, the one that's back soonest

When none of these is left, the session ends. So a word you get wrong comes back after a few new ones.

**A new word shows everything at once:** its sound (it plays by itself), Pinyin, characters, English, the sentence it first comes in and what each character means. You learn it there and pick how well you know it now; the buttons work as for any new word (*Don't know*: 1 min, *Know*: 1 d, *Safely know*: 3 d, …). It counts as studied that day (`studied`), which is how the app counts today's new words.

### Words set aside: *Don't know* twice

A word you say *Don't know* to **twice** is **set aside**: it no longer comes up as a review. Both times count, whether in the same session (the repeat after 1 minute) or on different days. On a later day it comes back **as a new word** (*Learn it again*), before the words you've never seen, showing everything again; its count then starts again. The count also starts again when you pick *Know* or better on a later day.

**Top of the tab:** how many words are due, how many new words are left today, how many of the list you've seen, and **Start**. You can stop any time; the screen then shows how many you did and how many are due tomorrow.

*Earlier versions had a **Study** table (the next 10 words, studied before they came into sessions) and **Practise today's Know words**. Both are gone: new words come in through the session itself. `SRS.studyWords` and `SRS.practiceWords` stay in `srs.js` for the Sentences tab, which still has both.*

---

## 5. The words: in the order of the Spoonfed deck

**Now:** the word list is every word of the Anki deck [Spoonfed Chinese](https://ankiweb.net/shared/info/1271086873) (the **Sentences** tab), **in the order the deck brings them in**: each sentence brings about one new word, and the word comes with that sentence as its example (🔊 and 🐢 play the deck's recording; the word is highlighted, and every word of the sentence is a button that plays it). That's 6923 words, then the 59 words of `data/words.json` that the deck doesn't have. `tools/spoonfed.py build` writes `docs/words.json`; each word there has the id of its sentence (`sf`) and where the word is in it (`mark`), and the app takes the sentence from `docs/spoonfed.json`.

- A word that's also in `data/words.json` (474 of them) keeps its English, notes, what each character means and its recording from there; the sentence is the deck's.
- The other words: Pinyin as the deck writes it, English from CC-CEDICT, a recording made by the same voice (`python tools/spoonfed.py words-audio`, in `docs/audio/sw/<code points>.mp3`, tone-checked like the others). A word the voice can't say (a syllable it never learned) has no recording: its card plays the sentence instead and says so.
- Progress is kept by the characters, as before, so words you'd already seen keep their progress.

**Before (still `data/words.json`, which the grammar sessions use):** the most common words first:


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
- **Audio of the example sentences:** one MP3 per sentence, made like the grammar sentences (`docs/audio/g-<hash>.mp3`; a sentence in both shares the file). Where the voice never learned a spoken tone change (*gěi wǒ* → *géi wǒ*), it says that syllable with its written tone.
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
| `last` | the last button picked (1–5) |
| `miss` | open: said *Don't know*, not yet known on a later day ([section 4](#4-sessions-and-new-words)). Cards from before this field count as open while on step 1 |
| `dk` | *Don't know* answers since the word was last studied or known on a later day; at 2 it's set aside |
| `studied` | the day it was last learnt as a new word (or in the Study table of earlier versions). A studied word you haven't reviewed yet is on `step` 0 |
| `at` | time of the last change, for sync |

- **Sync:** `words` is added to the synced keys. When two devices disagree about a word, the later `at` wins.
- **Log:** answers go into the activity log in batches of 20, `{t: "words", total, grades: [how many of each button], new}`, so a long session doesn't push the lesson mistakes out of the log. Hard words come from each word's `lapses`: **Copy progress for Claude** lists the words forgotten twice or more, and `tools/progress.py` keeps them in `data/progress.json`.

---

## 7. What's where

| Part | File |
|------|------|
| The word list: the Spoonfed deck's words, in its order | `data/spoonfed.json`, `tools/spoonfed.py` (`build`, `words-audio`) |
| The 533 common words (meanings, notes, recordings; the grammar sessions use them) | `data/words.json` |
| Checks and audio of those, app data (`docs/words.json`, through `tools/spoonfed.py`) | `tools/build.py` |
| When a word comes back, which card is next | `docs/srs.js` |
| Test of every rule and every cell of the table in section 3 | `node tools/test_srs.js` |
| The Words tab | `docs/index.html` |
| Words in Claude's progress summary | `tools/progress.py` |

### Later, if useful

- **The other way round:** English → say or pick the Chinese
- **Listening only:** sound without Pinyin or characters on the front
- **Typing the Pinyin** instead of just revealing (`ni3 hao3` or `nǐ hǎo` both accepted)
- **Single characters** with their parts, once there are enough words
