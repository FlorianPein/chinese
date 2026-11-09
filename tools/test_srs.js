// Checks docs/srs.js against the rules in WORDS-PLAN.md (sections 3 and 4).
//   node tools/test_srs.js
"use strict";
const assert = require("assert");
const SRS = require("../docs/srs.js");

let failed = 0;
function test(name, fn) {
  try { fn(); console.log(`ok    ${name}`); }
  catch (e) { failed++; console.log(`FAIL  ${name}\n      ${e.message}`); }
}

const DAY = 86400000;
const T0 = new Date(2026, 10, 7, 18, 0).getTime();   // 7 Nov 2026, 6 pm local time
const at = days => T0 + days * DAY;
const MIN = 60000;
const K = { "Don't know": 1, "Barely know": 2, "Know": 3, "Safely know": 4, "Securely know": 5 };
const daysUntil = (card, now) => (Date.parse(card.due) - Date.parse(SRS.dayOf(now))) / DAY;
const label = days => SRS.LABELS[SRS.LADDER.indexOf(days)];

// a word that's waiting `days` (on that step), reviewed on its due day
function waiting(days) {
  if (days === 0) return null;
  return { step: SRS.LADDER.indexOf(days) + 1, due: SRS.dayOf(T0), learning: 0, reps: 3, lapses: 0 };
}

// Section 3, "When the word reappears, for every button": waiting now -> [Barely, Know, Safely, Securely]
const TABLE = {
  0:   ["1 d", "1 d", "3 d", "7 d"],
  1:   ["1 d", "3 d", "7 d", "14 d"],
  3:   ["1 d", "3 d", "7 d", "14 d"],
  7:   ["1 d", "7 d", "14 d", "1 mo"],
  14:  ["3 d", "14 d", "1 mo", "2 mo"],
  30:  ["7 d", "14 d", "1 mo", "2 mo"],
  60:  ["14 d", "1 mo", "2 mo", "4 mo"],
  120: ["1 mo", "2 mo", "4 mo", "8 mo"],
  240: ["2 mo", "4 mo", "8 mo", "1 yr"],
  365: ["4 mo", "8 mo", "1 yr", "1 yr"],
};

for (const [days, row] of Object.entries(TABLE)) {
  const name = days === "0" ? "new word" : `waiting ${label(+days)}`;
  test(`table: ${name}`, () => {
    const card = waiting(+days);
    // Don't know: back in 1 min, then 1 d once you know it
    let c = SRS.answer(card, 1, T0);
    assert.equal(c.learning, T0 + MIN, "Don't know: back in 1 min");
    assert.equal(SRS.preview(card, 1), "1 min");
    c = SRS.answer(c, 3, T0 + 2 * MIN);
    assert.equal(label(daysUntil(c, T0)), "1 d", "Don't know, then Know: 1 d");
    // Barely know: back in 10 min, then the table's time
    c = SRS.answer(card, 2, T0);
    assert.equal(c.learning, T0 + 10 * MIN, "Barely know: back in 10 min");
    assert.equal(SRS.preview(card, 2), "10 min");
    c = SRS.answer(c, 3, T0 + 11 * MIN);
    assert.equal(label(daysUntil(c, T0)), row[0], "Barely know, then Know");
    // Know, Safely know, Securely know: what the button says, and when it comes back
    for (const [i, grade] of [3, 4, 5].entries()) {
      assert.equal(SRS.preview(card, grade), row[i + 1], `button ${SRS.GRADES[grade - 1]}`);
      const done = SRS.answer(card, grade, T0);
      assert.equal(done.learning, 0);
      assert.equal(label(daysUntil(done, T0)), row[i + 1], SRS.GRADES[grade - 1]);
    }
  });
}

test("example in section 3", () => {
  const steps = [   // [day, button, comes back in]
    [0, "Know", "1 d"], [1, "Know", "3 d"], [4, "Know", "3 d"], [7, "Safely know", "7 d"],
    [14, "Securely know", "1 mo"], [44, "Safely know", "1 mo"], [74, "Securely know", "2 mo"],
    [134, "Know", "1 mo"], [164, "Barely know", "7 d"], [171, "Don't know", "1 d"],
  ];
  let c = null;
  for (const [day, button, want] of steps) {
    assert.equal(c ? c.due : SRS.dayOf(at(0)), SRS.dayOf(at(day)), `due on day ${day}`);
    c = SRS.answer(c, K[button], at(day));
    if (c.learning) c = SRS.answer(c, 3, c.learning);   // back in the session: now Know
    assert.equal(label(daysUntil(c, at(day))), want, `day ${day}, ${button}`);
  }
  assert.equal(c.lapses, 1);
  assert.equal(c.reps, 10);
});

test("same-session repeats don't climb", () => {
  let c = SRS.answer(waiting(30), 2, T0);           // Barely: 1 mo -> 7 d after the repeat
  assert.equal(SRS.preview(c, 5), "7 d", "Securely know on the repeat shows the halved time");
  c = SRS.answer(c, 5, T0 + 11 * MIN);
  assert.equal(label(daysUntil(c, T0)), "7 d");
  assert.equal(c.reps, 4, "only the first answer counts as a review (3 before)");
});

test("Don't know on a repeat still sends the word back to the start", () => {
  let c = SRS.answer(waiting(60), 2, T0);           // Barely: step down to 14 d
  c = SRS.answer(c, 1, T0 + 11 * MIN);              // forgot it after all
  c = SRS.answer(c, 3, T0 + 13 * MIN);
  assert.equal(label(daysUntil(c, T0)), "1 d");
});

test("late reviews: counted from the day of the review, no bonus", () => {
  const c = SRS.answer({ ...waiting(7), due: SRS.dayOf(at(-5)) }, 4, T0);   // 5 days late
  assert.equal(daysUntil(c, T0), 14);
});

test("day starts at 4 am", () => {
  const late = new Date(2026, 10, 8, 2, 30).getTime();   // 2:30 am on the 8th counts as the 7th
  assert.equal(SRS.dayOf(late), "2026-11-07");
  assert.equal(SRS.dayOf(new Date(2026, 10, 8, 4, 0).getTime()), "2026-11-08");
});

test("hard word after 6 Don't know", () => {
  let c = waiting(3);
  for (let i = 0; i < 6; i++) {
    c = SRS.answer(c, 1, at(i * 2));
    c = SRS.answer(c, 3, at(i * 2) + 2 * MIN);
  }
  assert.equal(c.lapses, SRS.HARD);
});

// ---- section 4: sessions, and the Study table ----
const WORDS = Array.from({ length: 300 }, (_, i) => `w${i}`);
function deck(nDue, nLearning = 0) {
  const cards = {};
  WORDS.slice(0, nDue).forEach(w => cards[w] = { step: 2, due: SRS.dayOf(at(-1)), learning: 0, reps: 1, lapses: 0 });
  WORDS.slice(nDue, nDue + nLearning).forEach(w => cards[w] = { step: 1, due: SRS.dayOf(T0), learning: T0 + 10 * MIN, reps: 1, lapses: 0 });
  return cards;
}
// a session: answer every card with grade(word, kind) until nothing is left
function session(cards, now, grade) {
  const s = { recent: [] }, shown = [];
  for (let next; (next = SRS.pickNext(WORDS, cards, now, s)) && shown.length < 200; ) {
    cards[next.word] = SRS.answer(cards[next.word], grade(next.word, next.kind), now);
    shown.push(next.word);
    s.recent = [next.word, ...s.recent].slice(0, SRS.MIN_GAP);
    now += 2 * MIN;
  }
  return shown;
}
const studyAll = (cards, now) => { for (const w of SRS.studyWords(WORDS, cards)) cards[w] = SRS.study(cards[w], now); };

test("sessions never bring new words", () => {
  assert.equal(SRS.pickNext(WORDS, {}, T0, { recent: [] }), null, "nothing studied: nothing to do");
  const cards = deck(5);
  const shown = session(cards, T0, () => 3);
  assert.deepEqual(shown, ["w0", "w1", "w2", "w3", "w4"]);
  assert.equal(Object.keys(cards).length, 5);
});

test("a wrong word comes back first once its minutes are up, not straight after itself", () => {
  const cards = deck(30);
  cards.w0 = SRS.answer(cards.w0, 1, T0);
  const session = { recent: [] };
  assert.notEqual(SRS.pickNext(WORDS, cards, T0 + 30000, session).word, "w0", "not before 1 min");
  assert.equal(SRS.pickNext(WORDS, cards, T0 + MIN, session).word, "w0");
  assert.notEqual(SRS.pickNext(WORDS, cards, T0 + MIN, { ...session, recent: ["w0"] }).word, "w0",
                  "not right after it was shown");
});

test("due words: the longest waiting first", () => {
  const cards = deck(30);
  cards.w20.due = SRS.dayOf(at(-9));
  assert.equal(SRS.pickNext(WORDS, cards, T0, { recent: [] }).word, "w20");
});

test("due words: open words first, then words just studied, then the longest waiting", () => {
  const cards = deck(30);
  cards.w3.due = SRS.dayOf(at(-9));
  cards.w100 = SRS.study(null, T0);
  cards.w20.miss = true;
  assert.deepEqual(SRS.pickNext(WORDS, cards, T0, { recent: [] }), { word: "w20", kind: "due" });
  delete cards.w20.miss;
  assert.deepEqual(SRS.pickNext(WORDS, cards, T0, { recent: [] }), { word: "w100", kind: "new" });
});

test("when only waiting words are left, the soonest comes anyway", () => {
  const cards = {};
  for (const w of WORDS) cards[w] = { step: 3, due: SRS.dayOf(at(5)), learning: 0, reps: 1, lapses: 0 };
  cards.w7 = SRS.answer(cards.w7, 2, T0);
  assert.equal(SRS.pickNext(WORDS, cards, T0 + MIN, { recent: [] }).word, "w7");
  cards.w7 = SRS.answer(cards.w7, 3, T0 + 2 * MIN);
  assert.equal(SRS.pickNext(WORDS, cards, T0 + 3 * MIN, { recent: [] }), null);
});

test("study: new words, most common first, come into the next session as new words", () => {
  const cards = {};
  assert.deepEqual(SRS.studyWords(WORDS, cards), WORDS.slice(0, 10));
  studyAll(cards, T0);
  const kinds = [];
  session(cards, T0 + MIN, (w, kind) => (kinds.push(kind), 3));
  assert.deepEqual(kinds, Array(10).fill("new"));
  assert.deepEqual(Object.keys(cards), WORDS.slice(0, 10), "no other words");
  assert.ok(Object.values(cards).every(c => c.step === 1 && c.reps === 1 && daysUntil(c, T0) === 1), "Know on a new word: 1 d");
  assert.deepEqual(SRS.studyWords(WORDS, cards), WORDS.slice(10, 20), "next time: the next 10");
});

test("study: the Don't know words first (set aside ones first), then new words", () => {
  const cards = deck(20);
  cards.w4 = SRS.answer(cards.w4, 1, T0);                       // Don't know once: open
  cards.w9 = SRS.answer(SRS.answer(cards.w9, 1, T0), 1, T0 + 2 * MIN);   // twice: set aside
  cards.w12 = SRS.answer(cards.w12, 2, T0);                     // Barely know: not in the table
  assert.deepEqual(SRS.studyWords(WORDS, cards), ["w9", "w4", ...WORDS.slice(20, 28)]);
  for (let i = 0; i < 12; i++) cards[`w${30 + i}`] = { step: 1, due: SRS.dayOf(at(1)), learning: 0, reps: 1, lapses: 0 };   // open (step 1)
  assert.equal(SRS.studyWords(WORDS, cards).length, 10, "10 at most");
  assert.ok(SRS.studyWords(WORDS, cards).every(w => cards[w]), "enough Don't know words: no new ones");
});

test("set aside: Don't know twice takes a word out of the sessions until you study it", () => {
  const cards = deck(3);
  // w0: Don't know, and again Don't know when it comes back
  session(cards, T0, w => w === "w0" && !SRS.isParked(cards.w0) ? 1 : 3);
  assert.ok(SRS.isParked(cards.w0));
  assert.equal(cards.w0.dk, 2);
  assert.equal(SRS.counts(WORDS, cards, T0 + 30 * MIN).parked, 1);
  assert.deepEqual(session(cards, at(3), () => 3), ["w1", "w2"], "3 days later: w0 doesn't come");
  assert.equal(SRS.studyWords(WORDS, cards)[0], "w0");
  studyAll(cards, at(3));
  assert.ok(!SRS.isParked(cards.w0));
  assert.equal(SRS.pickNext(WORDS, cards, at(3), { recent: [] }).word, "w0", "studied: back in the session");
});

test("set aside: also over two days, but Know on a later day starts the count again", () => {
  let c = SRS.answer(waiting(7), 1, T0);
  c = SRS.answer(c, 3, T0 + 2 * MIN);
  assert.equal(c.dk, 1);
  const twice = SRS.answer(c, 1, at(1));
  assert.ok(SRS.isParked(twice), "Don't know again the next day");
  c = SRS.answer(c, 3, at(1));                                  // known on a later day
  assert.equal(c.dk, 0);
  assert.ok(!SRS.isParked(SRS.answer(c, 1, at(2))));
});

test("open words: Don't know on a learned word opens it, Know on a later day closes it", () => {
  let c = SRS.answer(waiting(30), 1, T0);
  c = SRS.answer(c, 4, T0 + 2 * MIN);
  assert.ok(SRS.isOpen(c), "still open after Know in the same session");
  c = SRS.answer(c, 3, at(1));
  assert.ok(!SRS.isOpen(c));
});

test("open words: cards from before the change count when still on step 1", () => {
  const old = { step: 1, due: SRS.dayOf(at(1)), learning: 0, reps: 1, lapses: 0 };
  assert.ok(SRS.isOpen(old));
  assert.ok(!SRS.isOpen({ ...old, step: 2 }));
  assert.ok(!SRS.isOpen(SRS.answer(old, 3, at(1))));
});

// ---- practice: today's Know words once more ----
test("practice: the words picked Know today that come back tomorrow", () => {
  const cards = {
    know: SRS.answer(null, 3, T0),                                    // new, Know: tomorrow
    safely: SRS.answer(null, 4, T0),                                  // 3 d
    again: SRS.answer(SRS.answer(null, 1, T0), 3, T0 + 2 * MIN),      // Don't know, then Know: tomorrow
    againSafely: SRS.answer(SRS.answer(null, 1, T0), 4, T0 + 2 * MIN),// tomorrow, but Safely know
    waiting: SRS.answer(null, 1, T0),                                 // still waiting its minute
    yesterday: SRS.answer(null, 3, at(-1)),                           // Know yesterday: due today
    older: SRS.answer(SRS.answer(null, 3, at(-3)), 3, at(-2)),        // Know 2 days ago, 3 d: due tomorrow
  };
  assert.deepEqual(SRS.practiceWords(Object.keys(cards), cards, T0 + 5 * MIN), ["know", "again"]);
  // cards from before `last` was stored: answered today, back tomorrow
  const old = { ...cards.know }; delete old.last;
  assert.deepEqual(SRS.practiceWords(["old"], { old }, T0 + 5 * MIN), ["old"]);
  // not words set aside
  assert.deepEqual(SRS.practiceWords(["know"], { know: { ...cards.know, dk: 2 } }, T0 + 5 * MIN), []);
});

test("practice: Know or better changes nothing, Don't know and Barely know go down", () => {
  const card = SRS.answer(null, 3, T0);
  for (const g of [3, 4, 5]) {
    assert.strictEqual(SRS.practice(card, g, T0 + MIN), card, `${SRS.GRADES[g - 1]} leaves it`);
    assert.equal(SRS.practicePreview(card, g), "1 d");
  }
  let c = SRS.practice(card, 1, T0 + MIN);
  assert.equal(c.learning, T0 + 2 * MIN, "Don't know: once more in the practice");
  assert.ok(SRS.isOpen(c), "and the word is open again");
  assert.equal(c.lapses, 1, "counts as forgotten");
  c = SRS.practice(c, 5, T0 + 3 * MIN);
  assert.equal(c.learning, 0);
  assert.equal(c.step, 1);
  assert.equal(daysUntil(c, T0), 1, "back tomorrow, not later");
  c = SRS.practice(card, 2, T0 + MIN);
  assert.equal(c.learning, T0 + 11 * MIN, "Barely know: once more in the practice");
  assert.equal(SRS.practice(c, 3, T0 + 12 * MIN).step, 1);
});

console.log(failed ? `\n${failed} failed` : "\nAll passed");
process.exit(failed ? 1 : 0);
