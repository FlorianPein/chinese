// Word flashcards: when a word comes back, and which card is next.
// The rules are in WORDS-PLAN.md (sections 3 and 4); tools/test_srs.js checks them.
//
// A word's progress: { step, due, learning, reps, lapses, at }
//   step      0 = new, 1–9 = a step on the ladder (1 d … 1 yr)
//   due       the day ("YYYY-MM-DD", days start at 4 am) it's next shown
//   learning  while it waits its 1 or 10 minutes after Don't know / Barely know:
//             the time (ms) it's back; 0 otherwise
//   reps, lapses   real reviews, and how many of them were Don't know
//   at        time of the last change (for sync: the later one wins)
(function (root) {
"use strict";

const LADDER = [1, 3, 7, 14, 30, 60, 120, 240, 365];   // days, steps 1–9
const LABELS = ["1 d", "3 d", "7 d", "14 d", "1 mo", "2 mo", "4 mo", "8 mo", "1 yr"];
const AGAIN_MINUTES = { 1: 1, 2: 10 };                  // Don't know, Barely know
const GRADES = ["Don't know", "Barely know", "Know", "Safely know", "Securely know"];
// How far Know (3), Safely know (4) and Securely know (5) move a word, by how
// long it's been waiting: start = 1 d (and new words), days = 3–14 d, months = 1 mo+
const MOVES = { start: { 3: 1, 4: 2, 5: 3 }, days: { 3: 0, 4: 1, 5: 2 }, months: { 3: -1, 4: 0, 5: 1 } };
const HARD = 6;           // this many Don't know: a hard word ⚑
const DAY_STARTS = 4;     // hours: a session after midnight still counts as the day before
const MIN_GAP = 3;        // a word you just got wrong waits at least this many other cards

const band = step => step <= 1 ? "start" : step <= 4 ? "days" : "months";
const clamp = step => Math.max(1, Math.min(LADDER.length, step));

// the step a real review moves a word to
function nextStep(step, grade) {
  if (grade === 1) return 1;
  if (grade === 2) return band(step) === "start" ? 1 : clamp(step - 2);
  return clamp(step + MOVES[band(step)][grade]);
}

const pad = n => String(n).padStart(2, "0");
function dayOf(ms) {
  const d = new Date(ms - DAY_STARTS * 3600000);
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}
function addDays(day, n) {
  const [y, m, d] = day.split("-").map(Number);
  return new Date(Date.UTC(y, m - 1, d + n)).toISOString().slice(0, 10);
}

// A real review is a new word, or a word whose day has come. A word coming back
// in the same session after Don't know / Barely know doesn't climb: the answer
// only decides whether it's done for today (Don't know still sends it to step 1).
function answer(card, grade, now) {
  const c = { step: 0, due: "", learning: 0, reps: 0, lapses: 0, ...(card || {}) };
  const today = dayOf(now);
  if (!c.learning) {
    c.reps++;
    if (grade === 1 && c.step > 0) c.lapses++;
    c.step = nextStep(c.step, grade);
  } else if (grade === 1) {
    c.step = 1;
  }
  if (grade <= 2) {
    c.learning = now + AGAIN_MINUTES[grade] * 60000;
    c.due = today;
  } else {
    c.learning = 0;
    c.due = addDays(today, LADDER[c.step - 1]);   // late or not: counted from today
  }
  c.at = new Date(now).toISOString().slice(0, 19);
  return c;
}

// what a button would do, for its label: "1 min", "10 min", "3 d" …
function preview(card, grade) {
  if (grade <= 2) return `${AGAIN_MINUTES[grade]} min`;
  const c = card || { step: 0, learning: 0 };
  return LABELS[(c.learning ? c.step : nextStep(c.step, grade)) - 1];
}

// one new word in every N cards, by how many old words are due
function newEvery(due) {
  return due >= 50 ? 20 : due >= 20 ? 10 : due >= 10 ? 5 : due >= 5 ? 3 : due >= 1 ? 2 : 1;
}

function sortWords(words, cards, now) {
  const today = dayOf(now), learning = [], due = [], fresh = [];
  for (const w of words) {
    const c = cards[w];
    if (!c) fresh.push(w);
    else if (c.learning) learning.push(w);
    else if (c.due <= today) due.push(w);
  }
  learning.sort((a, b) => cards[a].learning - cards[b].learning);
  due.sort((a, b) => cards[a].due < cards[b].due ? -1 : cards[a].due > cards[b].due ? 1 : 0);   // longest waiting first
  return { learning, due, fresh };
}

// The next card. words: all words in order (most common first); cards: progress
// by word; session: { sinceNew, recent } (cards since the last new word, the last
// few words shown). Returns { word, kind: "again" | "due" | "new" } or null.
function pickNext(words, cards, now, session) {
  const { learning, due, fresh } = sortWords(words, cards, now);
  const recent = session.recent || [];
  // 1. a word you just got wrong whose minutes are up
  const ready = learning.find(w => cards[w].learning <= now && !recent.includes(w));
  if (ready) return { word: ready, kind: "again" };
  // 2. the mix: many due means almost no new words, none due means only new words;
  //    no new words while 5 or more wrong ones are waiting
  const wantNew = fresh.length && learning.length < 5 &&
                  (!due.length || session.sinceNew >= newEvery(due.length) - 1);
  if (wantNew) return { word: fresh[0], kind: "new" };
  if (due.length) return { word: due[0], kind: "due" };
  // 3. nothing else left: the waiting word that's back soonest
  const waiting = learning.find(w => !recent.includes(w)) || learning[0];
  return waiting ? { word: waiting, kind: "again" } : null;
}

function counts(words, cards, now) {
  const { learning, due, fresh } = sortWords(words, cards, now);
  const tomorrow = addDays(dayOf(now), 1);
  return { due: due.length, learning: learning.length, fresh: fresh.length, learned: words.length - fresh.length,
           tomorrow: words.filter(w => cards[w] && (cards[w].learning || cards[w].due <= tomorrow)).length };
}

const SRS = { LADDER, LABELS, GRADES, HARD, MIN_GAP, nextStep, answer, preview, newEvery, pickNext, counts, dayOf, addDays };
if (typeof module !== "undefined") module.exports = SRS;
else root.SRS = SRS;
})(this);
