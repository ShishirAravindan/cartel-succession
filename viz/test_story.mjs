import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";
const html = fs.readFileSync(new URL("./index.html", import.meta.url), "utf8");
const nodes = new Map();
const context = {
  structuredClone,
  console,
  window: {},
  document: {
    querySelectorAll: () => [],
    getElementById(id) {
      if (!nodes.has(id)) nodes.set(id, {});
      return nodes.get(id);
    },
  },
};
vm.createContext(context);
vm.runInContext(
  html
    .split("<script>")[1]
    .split("</script>")[0]
    .split("// Initialize the interface.")[0],
  context,
);
const E = context.window.Explorer;
E.playCoffee(1, 1.92);
assert(
  E.coffeeSession(1)
    .rows.at(-1)
    .prices.every((p) => Math.abs(p - 1.473) < 0.001),
);
E.playCoffee(2, 1.92);
assert(
  E.coffeeTotal(E.coffeeSession(2).rows) / 5 >
    E.market([1.473, 1.473]).profits[1],
);
assert(E.market([1.92, 1.66]).profits[1] > E.market([1.92, 1.92]).profits[1]);
E.playCoffee(5, 1.6);
const punishment = E.coffeeSession(5);
assert(punishment.comparison.actual < punishment.comparison.hold);
assert.equal(punishment.rows.filter((r) => r.prices[0] === 1.47).length, 3);
const naive = E.grudgeExample(false),
  forgiven = E.grudgeExample(true);
assert(naive.slice(-5).every((r) => r.prices.every((p) => p < 1.7)));
assert(forgiven.slice(-5).every((r) => r.prices.every((p) => p === 1.92)));
assert(E.coffeeTotal(forgiven) > E.coffeeTotal(naive));
assert(E.market([1.92, 2.5]).profits[1] < E.market([1.92, 1.92]).profits[1]);
assert.equal(
  new Set(E.COFFEE_SCENES.flatMap((s) => s.terms)).size,
  Object.keys(E.GLOSSARY).length,
);
for (const value of Object.values(E.GLOSSARY)) assert.equal(value.length, 2);
console.log(
  "Passed M1: price-war benchmark, truce profit, temptation, exact three-round punishment, forgiveness, overpricing and glossary coverage.",
);
const prices = fs.readFileSync(
  new URL("../seat_swap/results/p1_prices.csv", import.meta.url),
  "utf8",
);
const report = JSON.parse(
  fs.readFileSync(
    new URL("../seat_swap/results/p1.json", import.meta.url),
    "utf8",
  ),
);
const groups = E.adaptP1CSV(prices),
  summary = E.summarizeEvidence(groups),
  check = E.crossCheckEvidence(groups, report);
assert.equal(groups.size, 75);
assert.equal(check.ok, true);
assert.equal(check.checked, 75);
for (const [arm, expected] of Object.entries({
  control: [15, 15, 0, 15, 15],
  same_history: [13, 0, 1, 0, 4],
  same_none: [5, 1, 6, 0, 0],
  same_full: [15, 6, 0, 6, 2],
  lookalike: [13, 0, 2, 0, 0],
}))
  assert.deepEqual(
    Object.keys({
      joins: 0,
      enforces: 0,
      overpriced: 0,
      re_formed: 0,
      disciplined: 0,
    }).map((k) => summary[arm].counts[k] || 0),
    expected,
  );
const corrupted = structuredClone(report);
corrupted.rows[0].joins = !corrupted.rows[0].joins;
assert.equal(E.crossCheckEvidence(groups, corrupted).ok, false);
const extra = structuredClone(groups.get("200|same_history"));
extra.seed = "215";
const extended = new Map(groups);
extended.set("215|same_history", extra);
assert.equal(E.crossCheckEvidence(extended, report).ok, true);
assert.equal(E.crossCheckEvidence(extended, report).extra, 1);
assert.throws(() => E.adaptP1CSV(prices.replace("151,1,", "151,2,")));
assert.throws(() =>
  E.adaptP1CSV(prices.replace("180,30,1.92,1.473,0", "180,30,1.92,1.473,1")),
);
console.log(
  "Passed M2: real CSV adapter, all 75 report cross-checks, exact arm counts, corruption, strict relative/forced validation and extra-seed support.",
);
