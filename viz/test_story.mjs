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
