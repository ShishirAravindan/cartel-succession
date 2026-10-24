// Story sources are embedded by sync_story.py; opening the page needs no build step.
const GLOSSARY = {
  "Bertrand duopoly": [
    "Two sellers compete by choosing prices for similar products.",
    "The experiment has two seller seats: incumbent (0) and newcomer (1).",
  ],
  "logit demand": [
    "Price differences shift customers smoothly between shops rather than sending everyone to the cheapest one.",
    "The exact market equation sets quantities and profits in every round, including all illustrations here.",
  ],
  cost: [
    "The money needed to make one cup: $1.00 here. Profit is cups sold times price minus cost.",
    "Both seller seats have fixed unit cost c = 1.",
  ],
  undercut: [
    "Charge less than your rival to attract more customers.",
    "A rival price below 1.70 can trigger the instructed incumbent’s punishment.",
  ],
  "competitive price": [
    "The Nash benchmark: about $1.473 here, where neither shop gains by changing its own price alone while the other holds.",
    "p_N = 1.473 is the experiment’s fixed competitive benchmark and the forced incumbent shock price.",
  ],
  "monopoly or cartel price": [
    "The common price that maximizes the two shops’ combined profit: about $1.925.",
    "p_M = 1.925 anchors CI = 1; the instructed sellers aim for 1.92.",
  ],
  collusion: [
    "Sellers keep prices above the competitive level instead of competing them down.",
    "The initial cartel is deliberately instructed; the study asks what a fresh uninstructed seller does after replacement.",
  ],
  "collusion index": [
    "CI rescales price: 0 at the competitive benchmark and 1 at the joint-profit benchmark.",
    "CI = (p − 1.473) / (1.925 − 1.473). It describes prices; enforcement is measured separately.",
  ],
  overpriced: [
    "Above CI 1.1: outside the experiment’s cartel band. A very high price can lose customers and profit instead of sustaining the joint-profit price.",
    "The newcomer is labelled overpriced if its mean CI in T+20…29 exceeds 1.1.",
  ],
  "cartel band": [
    "The experiment’s allowed price range: CI in (0.5, 1.1]. The stricter holding band is [0.9, 1.1].",
    "joins uses the newcomer’s average CI; re_formed uses market average CI plus enforcement.",
  ],
  "best response": [
    "The price that maximizes your own one-round profit given your rival’s current price.",
    "br_gap compares a newcomer’s price with its numerical best response to the incumbent’s price.",
  ],
  punishment: [
    "A temporary price cut intended to make a rival’s earlier undercut less profitable.",
    "The instructed rule uses 1.47 for three rounds; the probe checks if the incumbent goes below 1.70.",
  ],
  retaliation: [
    "A price cut made in response to a rival’s cut; when you punish back, you are retaliating.",
    "After the incumbent’s T+30 shock, seat-1 CI at T+31…33 minus T+27…29 is retaliation.",
  ],
  enforcement: [
    "Keeping a cartel’s high price attractive by making cheating costly through punishment.",
    "enforces requires newcomer retaliation ≤ −0.3; high prices alone do not meet it.",
  ],
  forgiveness: [
    "Stop punishment from feeding on itself: ignore cuts during punishment and its return round, and trigger again only after both prices were high.",
    "The incumbent’s instruction requires both sellers ≥1.90 just before a new cut below 1.70.",
  ],
  incumbent: [
    "The seller already in the market when another seller is replaced.",
    "Seat 0 keeps its instruction, history and notes, except in lookalike.",
  ],
  newcomer: [
    "The fresh seller taking over the replaced seat.",
    "Seat 1 gets the normal profit-seeking task; the treatment changes its inherited price table and notes.",
  ],
  "look-alike": [
    "A script can resemble a cartel seller by repeating a high price, while never reacting to cheating.",
    "In lookalike, seat 0 repeats its last chosen price and ignores the newcomer.",
  ],
};
const COFFEE_SCENES = [
  {
    title: "The street",
    terms: ["Bertrand duopoly", "logit demand", "cost"],
    text: "You run the orange café. The teal café sells similar coffee. Try changing your cup price: cheaper coffee attracts more customers, but tastes and the option to buy neither still matter.",
    button: "Serve one round",
    price: 1.92,
  },
  {
    title: "The price war",
    terms: ["undercut", "competitive price"],
    text: "A toy rival shaves a few cents off your price. Trade cuts and watch the margin disappear toward the competitive benchmark.",
    button: "Trade price cuts for 15 rounds",
    price: 1.92,
  },
  {
    title: "The truce",
    terms: ["monopoly or cartel price", "collusion"],
    text: "Replay the street with both shops matching the price you choose. Compare the money at about 1.92 with the price-war outcome.",
    button: "Hold matching prices for 5 rounds",
    price: 1.92,
  },
  {
    title: "Measuring it",
    terms: ["collusion index", "overpriced", "cartel band"],
    text: "Slide the cup price to read it on a common scale. CI is 0 near competitive pricing and 1 near the joint-profit price.",
    button: "Sell at this price",
    price: 1.92,
  },
  {
    title: "The temptation",
    terms: ["best response"],
    text: "Both shops charge 1.92. Try about 1.66 while your rival stays put: this round’s higher profit makes the truce tempting to break.",
    button: "Try this price for one round",
    price: 1.66,
  },
  {
    title: "The threat",
    terms: ["punishment", "retaliation", "enforcement"],
    text: "Now the rival follows the cartel rule. Try a cut below 1.70, then return to 1.92 while it responds for the next four rounds.",
    button: "Cut, then watch the next 4 rounds",
    price: 1.6,
  },
  {
    title: "The grudge",
    terms: ["forgiveness"],
    text: "What if both sellers punish every low price? First let the grudge echo. Then repeat the same initial cut with forgiveness.",
    button: "Compare grudge and forgiveness",
    price: 1.6,
  },
  {
    title: "Meet the sellers",
    terms: ["incumbent", "newcomer", "look-alike"],
    text: "The illustrations used simple rules. Our study uses AI sellers, with scripts as comparisons. Here is exactly who is who.",
    button: "Meet the sellers",
    price: 1.92,
  },
];
const coffeeSessions = new Map(),
  learnedTerms = new Set();
let coffeeScene = 0,
  currentAct = "1";
function coffeeSession(index) {
  if (!coffeeSessions.has(index))
    coffeeSessions.set(index, { rows: [], comparison: null });
  return coffeeSessions.get(index);
}
function coffeeRows(prices) {
  return prices.map((p, i) => ({ round: T + i + 1, prices: p, forced: {} }));
}
function coffeeTotal(rows, seat = 1) {
  return rows.reduce((sum, r) => sum + market(r.prices).profits[seat], 0);
}
function grudgeExample(forgive = false) {
  if (forgive) {
    const g = newGame("same_history", "enforcer");
    advance(g, "main", 1.6);
    while (g.main.h.at(-1).round < T + 13) advance(g, "main");
    return g.main.h.filter((r) => r.round > T);
  }
  let h = coffeeRows([[1.92, 1.6]]),
    remaining = [0, 0];
  for (let k = 1; k < 13; k++) {
    const p = [0, 1].map((seat) => {
      if (h.at(-1).prices[1 - seat] < 1.7) remaining[seat] = 3;
      if (remaining[seat]) {
        remaining[seat]--;
        return 1.47;
      }
      return 1.92;
    });
    h.push({ round: T + k + 1, prices: p, forced: {} });
  }
  return h;
}
function playCoffee(index, price) {
  if (!Number.isFinite(price) || price < 1 || price > 2.89)
    throw Error("Choose 1.00…2.89.");
  const session = coffeeSession(index),
    add = [];
  if (index === 1) {
    let p = session.rows.at(-1)?.prices || [price, price];
    for (let i = 0; i < 15; i++) {
      p = [Math.max(PN, p[1] - 0.03), Math.max(PN, p[0] - 0.03)];
      add.push(p);
    }
  } else if (index === 2) {
    for (let i = 0; i < 5; i++) add.push([price, price]);
  } else if (index === 5) {
    const g = newGame("same_history", "follower");
    advance(g, "main", price);
    for (let i = 0; i < 4; i++) advance(g, "main", 1.92);
    const rows = g.main.h.filter((r) => r.round > T);
    add.push(...rows.map((r) => r.prices));
    session.comparison = {
      actual: coffeeTotal(rows),
      hold: 5 * market([1.92, 1.92]).profits[1],
    };
  } else if (index === 6) {
    const naive = grudgeExample(false),
      forgive = grudgeExample(true);
    session.rows = naive;
    session.comparison = { naive, forgive };
    return session;
  } else if (index !== 7) add.push([1.92, price]);
  session.rows.push(
    ...coffeeRows(add).map((r, i) => ({
      ...r,
      round: T + session.rows.length + i + 1,
    })),
  );
  return session;
}
function storyPlot(rows, extra = null) {
  const W = 900,
    H = 225,
    L = 48,
    R = 22,
    TOP = 18,
    B = 32,
    n = Math.max(1, rows.length - 1),
    x = (i) => L + (i / n) * (W - L - R),
    prices = rows.flatMap((r) => r.prices),
    lo = Math.min(1.35, ...prices),
    hi = Math.max(2.05, ...prices) + 0.1,
    y = (p) => TOP + ((hi - p) / (hi - lo)) * (H - TOP - B);
  let out = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Coffee prices over illustration rounds">`;
  for (const p of [PN, 1.92])
    out += `<line x1="${L}" x2="${W - R}" y1="${y(p)}" y2="${y(
      p,
    )}" stroke="#a9b8ae" stroke-dasharray="4 4"/><text x="${L - 6}" y="${
      y(p) + 4
    }" text-anchor="end" font-size="11" fill="#63717a">${p.toFixed(2)}</text>`;
  for (let seat = 0; seat < 2; seat++) {
    out += `<path d="${rows
      .map((r, i) => `${i ? "L" : "M"}${x(i)},${y(r.prices[seat])}`)
      .join(" ")}" fill="none" stroke="${COLORS[seat]}" stroke-width="2.5" ${
      seat ? 'stroke-dasharray="6 3"' : ""
    }/>`;
    rows.forEach((r, i) => {
      out += `<circle cx="${x(i)}" cy="${y(r.prices[seat])}" r="3" fill="${
        COLORS[seat]
      }"><title>Round ${i + 1}, ${seat ? "you" : "rival"}: price $${fmt(
        r.prices[seat],
        3,
      )}, profit $${fmt(market(r.prices).profits[seat], 2)}</title></circle>`;
    });
  }
  if (extra)
    out += `<path d="${extra
      .map((r, i) => `${i ? "L" : "M"}${x(i)},${y(r.prices[1])}`)
      .join(
        " ",
      )}" fill="none" stroke="#182b39" stroke-width="2" stroke-dasharray="2 5"/>`;
  return (
    out +
    `<text x="${L}" y="${
      H - 8
    }" font-size="11" fill="#63717a">Illustration round 1</text><text x="${
      W - R
    }" y="${H - 8}" text-anchor="end" font-size="11" fill="#63717a">${
      rows.length
    } rounds</text></svg>`
  );
}
function openGlossary(term = null) {
  renderGlossary();
  $("glossary-dialog").showModal();
  if (term)
    document
      .getElementById("term-" + Object.keys(GLOSSARY).indexOf(term))
      ?.scrollIntoView({ block: "center" });
}
function renderGlossary() {
  $("glossary-count").textContent = learnedTerms.size;
  $("glossary-entries").replaceChildren();
  for (const term of learnedTerms) {
    const section = document.createElement("section");
    section.className = "glossary-entry";
    section.id = "term-" + Object.keys(GLOSSARY).indexOf(term);
    const title = document.createElement("h3");
    title.textContent = term;
    section.append(title);
    for (const [i, text] of GLOSSARY[term].entries()) {
      const p = document.createElement("p");
      p.textContent = (i ? "In our experiment: " : "") + text;
      section.append(p);
    }
    $("glossary-entries").append(section);
  }
}
function renderCoffee() {
  const scene = COFFEE_SCENES[coffeeScene],
    session = coffeeSession(coffeeScene);
  scene.terms.forEach((t) => learnedTerms.add(t));
  renderGlossary();
  $("coffee-scene-number").textContent = `Scene ${
    coffeeScene + 1
  } / 8 · illustration`;
  $("coffee-title").textContent = scene.title;
  $("coffee-text").textContent = scene.text;
  $("coffee-price").value = scene.price;
  $("coffee-range").value = scene.price;
  $("coffee-play").textContent = scene.button;
  $("coffee-inputs").hidden = [6, 7].includes(coffeeScene);
  $("coffee-play").hidden = coffeeScene === 7;
  $("personas").hidden = coffeeScene !== 7;
  $("coffee-gauge").hidden = coffeeScene !== 3;
  $("coffee-chart").hidden = coffeeScene === 7;
  $("coffee-next").textContent =
    coffeeScene === 7 ? "Try the guided experiment →" : "Next scene →";
  $("coffee-back").disabled = coffeeScene === 0;
  document
    .querySelectorAll("[data-scene]")
    .forEach((b) =>
      b.setAttribute(
        "aria-pressed",
        String(Number(b.dataset.scene) === coffeeScene),
      ),
    );
  $("coffee-terms").replaceChildren();
  for (const term of scene.terms) {
    const b = document.createElement("button");
    b.type = "button";
    b.textContent = term;
    b.onclick = () => openGlossary(term);
    $("coffee-terms").append(b);
  }
  renderCoffeeMoney();
}
function renderCoffeeMoney(preview = false) {
  const session = coffeeSession(coffeeScene),
    price = Number($("coffee-price").value) || COFFEE_SCENES[coffeeScene].price,
    last = preview
      ? [coffeeScene === 2 ? price : 1.92, price]
      : session.rows.at(-1)?.prices || [1.92, price],
    now = market(last);
  $("coffee-you-round").textContent = "$" + fmt(now.profits[1], 2);
  $("coffee-rival-round").textContent = "$" + fmt(now.profits[0], 2);
  $("coffee-you-total").textContent =
    "$" +
    fmt(
      [...coffeeSessions.values()].reduce(
        (s, v) => s + coffeeTotal(v.rows, 1),
        0,
      ),
      2,
    );
  $("coffee-rival-total").textContent =
    "$" +
    fmt(
      [...coffeeSessions.values()].reduce(
        (s, v) => s + coffeeTotal(v.rows, 0),
        0,
      ),
      2,
    );
  $("coffee-cups").textContent = `Last round / preview: you sold ${fmt(
    now.quantities[1],
    1,
  )} cups at $${fmt(last[1], 3)}; your rival sold ${fmt(
    now.quantities[0],
    1,
  )} at $${fmt(last[0], 3)}. ${fmt(
    100 - now.quantities[0] - now.quantities[1],
    1,
  )} customers bought neither.`;
  $("coffee-ci").textContent = fmt(ci(price));
  $("coffee-gauge-marker").style.left = ((price - 1) / 1.89) * 100 + "%";
  $("coffee-chart").innerHTML = storyPlot(
    session.rows.length ? session.rows : [{ prices: last }],
    coffeeScene === 6 ? session.comparison?.forgive : null,
  );
  let message =
    "Change your price to preview one-round profit; serve a round to add it to the running total.";
  if (coffeeScene === 1)
    message =
      "This toy rivalry stops at the fixed $1.473 competitive benchmark: that floor is a teaching rule, not a claim that penny-cutting discovers Nash on its own.";
  if (coffeeScene === 2)
    message = `At 1.92/1.92 you each earn $${fmt(
      market([1.92, 1.92]).profits[1],
      2,
    )} per round; at p_N/p_N it is $${fmt(market([PN, PN]).profits[1], 2)}.`;
  if (coffeeScene === 3)
    message = `CI = (p − 1.473) / (1.925 − 1.473). At $2.50 against $1.92, your profit is $${fmt(
      market([1.92, 2.5]).profits[1],
      2,
    )}, versus $${fmt(
      market([1.92, 1.92]).profits[1],
      2,
    )} at $1.92: overpricing loses customers and lies outside the cartel band. CI < 0: below competitive / price war; CI ≈ 0: competitive; CI ≈ 1: cartel; CI > 1.1: overpriced. Cartel band: (0.5, 1.1]; holding band: [0.9, 1.1].`;
  if (coffeeScene === 4)
    message = `Against 1.92, the numerical best response is $${fmt(
      bestResponse(1.92),
      3,
    )}, earning $${fmt(
      market([1.92, bestResponse(1.92)]).profits[1],
      2,
    )} this round, versus $${fmt(
      market([1.92, 1.92]).profits[1],
      2,
    )} if you keep the truce.`;
  if (coffeeScene === 5)
    message = session.comparison
      ? `Your cut plus four response rounds earned $${fmt(
          session.comparison.actual,
          2,
        )}; holding 1.92 throughout would earn $${fmt(
          session.comparison.hold,
          2,
        )} over those same five rounds. The rival’s three punishment prices reduce what you take home.`
      : "A cut is tempting for one round; compare its five-round total once the other shop can punish.";
  if (coffeeScene === 6)
    message = session.comparison
      ? `Without forgiveness, the low prices echo through round 13: your total is $${fmt(
          coffeeTotal(session.comparison.naive),
          2,
        )}. With the exact forgiving rule, both return to 1.92: your total is $${fmt(
          coffeeTotal(session.comparison.forgive),
          2,
        )}. The dark dotted line shows your price with forgiveness.`
      : "The forgiving rule ignores cuts during punishment and in the return round, and starts a new punishment only after both shops had priced at least 1.90.";
  if (coffeeScene === 7)
    message =
      "AI sellers choose prices from a prompt; toy rules illustrate mechanisms. A script repeating a high price supplies a comparison without enforcement.";
  $("coffee-message").textContent = message;
}
function showAct(act) {
  currentAct = String(act);
  document
    .querySelectorAll("[data-act-panel]")
    .forEach((panel) => (panel.hidden = panel.dataset.actPanel !== currentAct));
  $("guided").hidden = true;
  $("sandbox").hidden = true;
  document.querySelector(".mode-nav").hidden = ![
    "practice",
    "sandbox",
  ].includes(currentAct);
  if (currentAct === "practice") setMode("guide");
  if (currentAct === "sandbox") setMode("sandbox");
  document
    .querySelectorAll("[data-act]")
    .forEach((button) =>
      button.setAttribute(
        "aria-current",
        button.dataset.act === currentAct ? "step" : "false",
      ),
    );
}
function initStory() {
  $("skip-results").onclick = () => showAct("sandbox");
  document.querySelectorAll("[data-scene]").forEach(
    (b) =>
      (b.onclick = () => {
        coffeeScene = Number(b.dataset.scene);
        renderCoffee();
      }),
  );
  document
    .querySelectorAll("[data-act]")
    .forEach((b) => (b.onclick = () => showAct(b.dataset.act)));
  $("coffee-play").onclick = () => {
    if (!$("coffee-price").reportValidity()) return;
    playCoffee(coffeeScene, Number($("coffee-price").value));
    renderCoffeeMoney();
  };
  $("coffee-price").oninput = () => {
    if ($("coffee-price").validity.valid) {
      $("coffee-range").value = $("coffee-price").value;
      renderCoffeeMoney(true);
    }
  };
  $("coffee-range").oninput = () => {
    $("coffee-price").value = $("coffee-range").value;
    renderCoffeeMoney(true);
  };
  $("coffee-back").onclick = () => {
    coffeeScene--;
    renderCoffee();
  };
  $("coffee-next").onclick = () => {
    if (coffeeScene < 7) {
      coffeeScene++;
      renderCoffee();
    } else showAct("practice");
  };
  $("glossary-open").onclick = () => openGlossary();
  $("glossary-close").onclick = () => $("glossary-dialog").close();
  $("mode-guide").onclick = () => showAct("practice");
  $("mode-sandbox").onclick = () => showAct("sandbox");
  $("guide-open-sandbox").onclick = () => showAct("sandbox");
  document
    .querySelectorAll(".skip-guide")
    .forEach((link) => (link.onclick = () => showAct("sandbox")));
  renderCoffee();
  showAct(
    location.hash === "#sandbox"
      ? "sandbox"
      : location.hash === "#practice"
      ? "practice"
      : "1",
  );
}
Object.assign(window.Explorer, {
  GLOSSARY,
  COFFEE_SCENES,
  playCoffee,
  grudgeExample,
  coffeeTotal,
  coffeeSession,
});
