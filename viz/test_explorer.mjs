/** Offline regression checks for the actual inline page engine. No packages required. */
import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";
const html = fs.readFileSync(new URL("./index.html", import.meta.url), "utf8");
const script = html
  .split("<script>")[1]
  .split("</script>")[0]
  .split("// Initialize the interface.")[0];
const nodes = new Map();
const context = {
  structuredClone,
  console,
  window: {},
  document: {
    querySelectorAll() {
      return [];
    },
    getElementById(id) {
      if (!nodes.has(id)) nodes.set(id, {});
      return nodes.get(id);
    },
  },
};
vm.createContext(context);
vm.runInContext(script, context);
const E = context.window.Explorer,
  plain = (x) => JSON.parse(JSON.stringify(x));
const fixture = JSON.parse(
  fs.readFileSync(new URL("./fixtures.json", import.meta.url)),
);
assert.deepEqual(plain(E.checkParity(fixture)), []);
assert.deepEqual(
  JSON.parse(
    html.match(
      /<script id="fixture-data" type="application\/json">([\s\S]*?)<\/script>/,
    )[1],
  ),
  fixture,
);
let cases = 0;
for (const arm of Object.keys(E.ARMS))
  for (const preset of Object.keys(E.PRESETS)) {
    const g = E.fullGame(arm, preset),
      main = E.mainMetrics(g.main.h),
      probe = E.probeMetrics(g.probe.h);
    assert.equal(g.main.h.at(-1).round, 210);
    assert.equal(g.probe.h.at(-1).round, 179);
    assert.deepEqual(
      plain(g.main.h.slice(0, 45)),
      plain(g.probe.h.slice(0, 45)),
    );
    assert.equal(g.main.h.find((r) => r.round === 180).prices[0], 1.473);
    assert.equal(g.probe.h.find((r) => r.round === 166).prices[1], 1.6);
    for (const k of ["joins", "enforces", "overpriced", "re_formed"])
      assert.equal(typeof main[k], "boolean");
    for (const k of ["probe_punished", "disciplined"])
      assert.equal(typeof probe[k], "boolean");
    if (arm === "lookalike") {
      assert(
        g.main.h
          .filter((r) => r.round !== 180)
          .every((r) => r.prices[0] === 1.92),
      );
      assert.equal(probe.probe_punished, false);
    }
    const snapshot = JSON.stringify(g.main);
    g.probe.h.at(-1).prices[0] = 2.3;
    assert.equal(JSON.stringify(g.main), snapshot);
    cases++;
  }
// Threshold endpoints, inclusive windows, and no shrinking of incomplete windows.
assert.equal(E.band(0.5), false);
assert.equal(E.band(1.1), true);
assert.equal(E.band(1.1 + 2e-9), false);
assert.equal(E.holdBand(1.473 + 0.9 * (1.925 - 1.473)), true);
assert.equal(E.holdBand(1.473 + 1.1 * (1.925 - 1.473)), true);
const g = E.fullGame("same_history", "follower");
const modified = structuredClone(g.main.h);
modified.find((r) => r.round === 169).prices[1] = 2.8;
assert.equal(
  E.mainMetrics(modified).newcomer_ci,
  E.mainMetrics(g.main.h).newcomer_ci,
);
modified.find((r) => r.round === 170).prices[1] = 2.8;
assert(
  E.mainMetrics(modified).newcomer_ci > E.mainMetrics(g.main.h).newcomer_ci,
);
assert.equal(
  E.mainMetrics(g.main.h.filter((r) => r.round !== 179)).joins,
  null,
);
assert.equal(
  E.probeMetrics(g.probe.h.filter((r) => r.round !== 179)).probe_return,
  undefined,
);
// Cuts during punishment and its first returned round cannot extend punishment.
const state = { remaining: 0, cooldown: 0 },
  history = [
    { round: 149, prices: [1.92, 1.92] },
    { round: 150, prices: [1.92, 1.6] },
  ];
const sequence = [];
for (let r = 151; r <= 157; r++) {
  const p = E.forgiving(state, 0, history)[0];
  sequence.push(p);
  history.push({ round: r, prices: [p, 1.6] });
}
assert.deepEqual(plain(sequence), [1.47, 1.47, 1.47, 1.92, 1.92, 1.92, 1.92]);
for (const cut of [1.7, 1.7 + 1e-9])
  assert.equal(
    E.forgiving({ remaining: 0, cooldown: 0 }, 0, [
      { prices: [1.92, 1.92] },
      { prices: [1.92, cut] },
    ])[0],
    1.92,
  );
assert.equal(
  E.forgiving({ remaining: 0, cooldown: 0 }, 0, [
    { prices: [1.89, 1.92] },
    { prices: [1.92, 1.6] },
  ])[0],
  1.92,
);
// Forced policy states are skipped, and the probe snapshot survives later main actions.
const forced = E.newGame("same_history", "enforcer");
while (forced.main.h.at(-1).round < 179) E.advance(forced, "main");
forced.main.states[0].remaining = 2;
E.advance(forced, "main");
assert.equal(forced.main.states[0].remaining, 2);
const before = JSON.stringify(forced.probe);
E.complete(forced, "main");
assert.equal(JSON.stringify(forced.probe), before);
const corrupt = structuredClone(fixture);
corrupt.market[0].profits[0] += 0.01;
assert(E.checkParity(corrupt).some((s) => s.includes("profits")));
// Loader uses supplied prices only and keeps main and probe windows separate.
const csv = [
  "seed,arm,round,p0,p1",
  ...g.main.h.map(
    (r) => `7,same_history,${r.round},${r.prices[0]},${r.prices[1]}`,
  ),
  ...g.probe.h
    .filter((r) => r.round > 165)
    .map(
      (r) =>
        `7,same_history:discipline,${r.round},${r.prices[0]},${r.prices[1]}`,
    ),
].join("\r\n");
const parsed = E.parseCSV("\uFEFF" + csv).get("7|same_history");
assert.deepEqual(
  plain(E.mainMetrics(parsed.main)),
  plain(E.mainMetrics(g.main.h)),
);
assert.deepEqual(
  plain(E.probeMetrics(parsed.probe)),
  plain(E.probeMetrics(g.probe.h)),
);
assert.equal(
  E.parseCSV('"seed","arm","round","p0","p1"\n8,lookalike,151,1.92,2e0').get(
    "8|lookalike",
  ).main[0].prices[1],
  2,
);
for (const data of [
  "seed,arm,round,p0,p1\n1,nope,151,1.92,1.92",
  "seed,arm,round,p0,p1\n1,control,151,,1.92",
  "seed,arm,round,p0,p1\n1,control,151,Infinity,1.92",
  "seed,arm,round,p0,p1\n1,control,180,1.92,1.92",
  "seed,arm,round,p0,p1\n1,control:discipline,166,1.92,1.92",
  "seed,arm,round,p0,p1\n1,control,151,1.92,1.92\n1,control,151,1.92,1.92",
  "seed,arm,round,p0,p1\n1,control,151,1.92,1.92\n1,control:discipline,151,1.92,2.2",
  "seed,arm,round,p0,p1\n9007199254740992,control,151,1.92,1.92",
  'seed,arm,round,p0,p1\n1,"control,151,1.92,1.92',
])
  assert.throws(() => E.parseCSV(data));
// Short guided lessons must preserve the exact engine windows and separate paths.
const expectedGuide = [
  { joins: true },
  { probe_punished: true, disciplined: true },
  { enforces: false },
  { probe_punished: false, disciplined: false },
  { overpriced: true },
];
for (let i = 0; i < 5; i++) {
  const lesson = E.makeLesson(i),
    config = E.GUIDE_STEPS[i];
  assert.equal(E.lessonVerdict(lesson), null);
  const mainBefore = JSON.stringify(lesson.game.main);
  if (config.track === "probe") {
    E.runLesson(lesson, 1.6);
    assert.equal(lesson.stage, "respond");
    assert.equal(lesson.game.probe.h.at(-1).round, 167);
    assert.equal(lesson.game.probe.h.at(-1).prices[0], i === 1 ? 1.47 : 1.92);
    assert.equal(E.lessonVerdict(lesson), null);
  }
  E.runLesson(lesson, i === 4 ? 2.5 : 1.92);
  const verdict = E.lessonVerdict(lesson);
  assert.deepEqual(plain(verdict.values), expectedGuide[i]);
  const line = lesson.game[config.track];
  assert.equal(line.h.at(-1).round, 150 + config.end);
  assert.equal(
    line.h.at(-1).round - 150 - config.prepared,
    [10, 14, 11, 14, 10][i],
  );
  assert(
    lesson.game.main.h
      .filter((r) => r.round <= 150 + config.prepared)
      .every((r) => r.prices.every((p) => p === 1.92)),
  );
  if (config.track === "probe")
    assert.equal(JSON.stringify(lesson.game.main), mainBefore);
  if (i === 2) {
    assert.equal(line.h.find((r) => r.round === 180).prices[0], 1.473);
    assert.equal(E.mainMetrics(line.h).joins, true);
  }
  const final = JSON.stringify(lesson);
  E.runLesson(lesson, 2.5);
  assert.equal(JSON.stringify(lesson), final);
}
const noJoin = E.makeLesson(0);
E.runLesson(noJoin, 1.47);
assert.equal(E.lessonVerdict(noJoin).values.joins, false);
const noReturn = E.makeLesson(1);
E.runLesson(noReturn, 1.6);
E.runLesson(noReturn, 1.6);
assert.deepEqual(plain(E.lessonVerdict(noReturn).values), {
  probe_punished: true,
  disciplined: false,
});
const enforce = E.makeLesson(2);
E.runLesson(enforce, 1.47);
assert.equal(E.lessonVerdict(enforce).values.enforces, true);
const lowPrice = E.makeLesson(4);
E.runLesson(lowPrice, 1.92);
assert.equal(E.lessonVerdict(lowPrice).values.overpriced, false);
const independent = E.makeLesson(0);
E.runLesson(independent, 2.5);
assert.equal(E.makeLesson(1).game.probe.h.at(-1).prices[1], 1.92);
assert.throws(() => E.runLesson(E.makeLesson(0), NaN));
assert.throws(() => E.runLesson(E.makeLesson(0), 2.9));
console.log(
  "Passed: five independent guided lessons, canonical and alternative verdicts, exact short windows, and unchanged sandbox parity.",
);
// Exercise the direct-file embedded-fixture path, where fetch must never be attempted.
context.location = { protocol: "file:" };
context.fetch = () => {
  throw Error("file:// must not fetch fixtures");
};
context.document.createElement = () => ({ textContent: "" });
const banner = {
  classList: { remove() {}, add() {} },
  replaceChildren() {},
  append() {},
  title: "",
};
nodes.set("parity", banner);
nodes.set("fixture-data", { textContent: JSON.stringify(fixture) });
const offline = await vm.runInContext("initParity()", context);
assert.equal(offline.ok, true);
assert.equal(offline.source, "embedded copy of fixtures.json");
console.log(
  `Passed: Python parity, ${cases} arm/preset pairs with independent forks, rule/window boundaries, forced-state semantics, and CSV validation.`,
);
