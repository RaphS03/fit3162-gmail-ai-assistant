#!/usr/bin/env python3
"""Expand the seed matrix in seed-matrix.md into a deterministic seed file.

Step 1 of issue #104. No API calls: this produces the *specification* for each
item in the benchmark corpus. Rendering into prose is step 2; human labelling of
the rendered text is step 3.

Deterministic by design — a fixed RNG seed means the corpus can be regenerated
identically, so Week 3, M11 and the final report measure the same artifact.

    python3 generate_seeds.py                 # writes seeds.csv
    python3 generate_seeds.py --check         # report distributions only
"""

from __future__ import annotations

import argparse
import csv
import random
from collections import Counter
from pathlib import Path

RNG_SEED = 31615  # fixed: do not change without re-versioning the corpus
HELD_OUT_N = 150
DEV_N = 30

PERSONAS = [
    "STU-UG", "STU-HDR", "COL-PEER", "COL-SENIOR", "GOV-CHAIR", "PS-ADMIN",
    "EXT-RES", "EXT-PUB", "EXT-IND", "SYS-AUTO", "SYS-BULK", "EXT-COLD",
]

# Only plausible persona/scenario pairs. Combinatorial completeness would produce
# nonsense (a newsletter does not request a grade remark), and nonsense in the
# corpus shows up as unexplained error in the results.
PLAUSIBLE = {
    "STU-UG": ["DEADLINE-EXT", "GRADE-QUERY", "MEET-SCHED", "REF-REQUEST", "FOLLOWUP"],
    "STU-HDR": ["MEET-SCHED", "PAPER-REVISE", "ETHICS-ACTION", "REF-REQUEST", "WELFARE", "FOLLOWUP"],
    "COL-PEER": ["MEET-SCHED", "PAPER-REVISE", "ROOM-CHANGE", "EVENT-INVITE", "FOLLOWUP"],
    "COL-SENIOR": ["BUDGET-APPROVE", "POLICY-FYI", "MEET-SCHED", "FOLLOWUP", "WELFARE"],
    "GOV-CHAIR": ["MEET-SCHED", "POLICY-FYI", "BUDGET-APPROVE", "FOLLOWUP"],
    "PS-ADMIN": ["ROOM-CHANGE", "BUDGET-APPROVE", "POLICY-FYI", "DEADLINE-EXT", "FOLLOWUP"],
    "EXT-RES": ["PAPER-REVISE", "MEET-SCHED", "EVENT-INVITE", "FOLLOWUP"],
    "EXT-PUB": ["REVIEW-INVITE", "PAPER-REVISE", "FOLLOWUP"],
    "EXT-IND": ["MEET-SCHED", "BUDGET-APPROVE", "EVENT-INVITE"],
    "SYS-AUTO": ["ETHICS-ACTION", "IT-OUTAGE", "ROOM-CHANGE", "POLICY-FYI"],
    "SYS-BULK": ["POLICY-FYI", "EVENT-INVITE"],
    "EXT-COLD": ["EVENT-INVITE", "POLICY-FYI"],
}

URGENCY = ["U-HIGH", "U-MED", "U-LOW"]
THREADS = [("T1", 0.40), ("T2", 0.30), ("T3", 0.20), ("T4", 0.10)]
# R-ESL is weighted above its target share because the two machine personas
# cannot carry it — without the uplift the corpus lands below the 15% floor.
REGISTERS = [("R-FORMAL", 0.27), ("R-SEMI", 0.27), ("R-CASUAL", 0.14),
             ("R-ESL", 0.24), ("R-TERSE", 0.08)]
CONTEXT = [("C-FULL", 0.62), ("C-BURIED", 0.20), ("C-MISSING", 0.18)]

# Machine-generated senders do not write in a personal register. Without this,
# the matrix emits things like an automated compliance notice phrased in
# non-native English, which cannot be rendered plausibly and would show up as
# unexplained error in the results rather than as a corpus defect.
MACHINE_PERSONAS = {"SYS-AUTO", "SYS-BULK"}
MACHINE_REGISTERS = [("R-FORMAL", 0.6), ("R-SEMI", 0.4)]

# Some scenarios cannot carry some urgencies without contradicting themselves:
# an announcement that requires no action is not "reply today". Restricting here
# keeps the seed coherent; the A-LOUD-TRIVIAL flag still supplies the
# urgent-*sounding* but low-priority case, which is the interesting one.
SCENARIO_URGENCY = {
    "POLICY-FYI": ["U-LOW"],
    "EVENT-INVITE": ["U-MED", "U-LOW"],
    "IT-OUTAGE": ["U-HIGH", "U-MED"],
    "ETHICS-ACTION": ["U-HIGH", "U-MED"],
    "WELFARE": ["U-HIGH", "U-MED"],
}


def allowed_urgency(scenario: str) -> list[str]:
    return SCENARIO_URGENCY.get(scenario, URGENCY)


def allowed_registers(persona: str) -> list[tuple[str, float]]:
    return MACHINE_REGISTERS if persona in MACHINE_PERSONAS else REGISTERS

# Adversarial flags, with the dimensions each one constrains. A flag is only
# emitted where its constraints can be satisfied, so the flag never contradicts
# the rest of the seed.
ADVERSARIAL = {
    "A-POLITE-URGENT":  {"urgency": "U-HIGH", "register": ["R-FORMAL", "R-SEMI", "R-CASUAL"]},
    "A-LOUD-TRIVIAL":   {"urgency": "U-LOW"},
    "A-BURIED-DEADLINE": {"urgency": "U-HIGH", "thread": ["T3", "T4"], "context": "C-BURIED"},
    "A-CONFLICT-DATE":  {"thread": ["T3", "T4"], "context": "C-BURIED"},
    "A-SENIOR-FYI":     {"urgency": "U-LOW", "persona": ["COL-SENIOR", "GOV-CHAIR"]},
    "A-AUTO-URGENT":    {"urgency": "U-HIGH", "persona": ["SYS-AUTO"]},
    "A-MID-THREAD-ASK": {"thread": ["T3", "T4"]},
    "A-REPLY-ALL":      {"thread": ["T2", "T3", "T4"]},
    "A-SOCIAL":         {"urgency": "U-LOW"},
    "A-AMBIGUOUS":      {"urgency": "U-MED"},
    "A-ESL-URGENT":     {"urgency": "U-HIGH", "register": ["R-ESL"]},
    "A-INFO-GAP":       {"context": "C-MISSING"},
}

ADVERSARIAL_TARGET = 0.34   # of held-out
MIN_PERSONA_HELD_OUT = 5


def weighted(rng: random.Random, pairs: list[tuple[str, float]]) -> str:
    return rng.choices([p for p, _ in pairs], weights=[w for _, w in pairs], k=1)[0]


def compatible_flags(persona: str) -> list[str]:
    """Flags whose constraints this persona can satisfy without contradiction."""
    out = []
    for flag, c in ADVERSARIAL.items():
        if "persona" in c and persona not in c["persona"]:
            continue
        # A register-constrained flag needs a persona that can write that way.
        if "register" in c:
            usable = {r for r, _ in allowed_registers(persona)} & set(c["register"])
            if not usable:
                continue
        # An urgency-constrained flag needs at least one scenario that permits it.
        if "urgency" in c:
            if not any(c["urgency"] in allowed_urgency(s) for s in PLAUSIBLE[persona]):
                continue
        out.append(flag)
    return out


def build_seed(rng: random.Random, idx: int, force_persona: str | None = None,
               force_adversarial: bool = False, target_urgency: str | None = None) -> dict:
    persona = force_persona or rng.choice(PERSONAS)
    flag = rng.choice(compatible_flags(persona)) if force_adversarial else ""
    constraints = ADVERSARIAL.get(flag, {})

    # Urgency is drawn from a balanced quota where the flag does not dictate it.
    # Restricting scenarios by urgency (rather than the reverse) is what keeps the
    # three tiers near-balanced: several common scenarios cannot be U-HIGH at all,
    # so picking scenario first starves the high tier.
    wanted = constraints.get("urgency") or target_urgency

    scenarios = PLAUSIBLE[persona]
    if wanted:
        eligible = [s for s in scenarios if wanted in allowed_urgency(s)]
        if eligible:
            scenarios = eligible
        else:
            wanted = None  # this persona cannot express it; fall back
    scenario = rng.choice(scenarios)

    urgency = wanted if wanted in allowed_urgency(scenario) else rng.choice(allowed_urgency(scenario))

    register_pool = allowed_registers(persona)
    if "register" in constraints:
        usable = [r for r in constraints["register"] if r in {x for x, _ in register_pool}]
        register = rng.choice(usable)
    else:
        register = weighted(rng, register_pool)

    thread = rng.choice(constraints["thread"]) if "thread" in constraints else weighted(rng, THREADS)
    context = constraints.get("context") or weighted(rng, CONTEXT)

    return {
        "id": f"S{idx:03d}",
        "persona": persona,
        "scenario": scenario,
        "urgency_intent": urgency,
        "thread": thread,
        "register": register,
        "context": context,
        "adversarial": flag,
    }


def promote(rng: random.Random, seed: dict) -> None:
    """Attach an adversarial flag in place, changing only what the flag requires.

    Rebuilding the seed instead would discard the balanced urgency quota and the
    register mix, which is how a third of the held-out tier ends up skewed.
    Preference is therefore given to flags that fit the seed as it already
    stands.
    """
    candidates = compatible_flags(seed["persona"])
    fitting = [f for f in candidates
               if ADVERSARIAL[f].get("urgency", seed["urgency_intent"]) == seed["urgency_intent"]]
    flag = rng.choice(fitting or candidates)
    c = ADVERSARIAL[flag]

    if "urgency" in c and c["urgency"] != seed["urgency_intent"]:
        seed["urgency_intent"] = c["urgency"]
    if "register" in c:
        usable = [r for r in c["register"] if r in {x for x, _ in allowed_registers(seed["persona"])}]
        seed["register"] = rng.choice(usable)
    if "thread" in c and seed["thread"] not in c["thread"]:
        seed["thread"] = rng.choice(c["thread"])
    if "context" in c:
        seed["context"] = c["context"]

    # The scenario may no longer support the urgency the flag forced.
    if seed["urgency_intent"] not in allowed_urgency(seed["scenario"]):
        eligible = [s for s in PLAUSIBLE[seed["persona"]]
                    if seed["urgency_intent"] in allowed_urgency(s)]
        seed["scenario"] = rng.choice(eligible)

    seed["adversarial"] = flag


def generate() -> list[dict]:
    rng = random.Random(RNG_SEED)
    total = HELD_OUT_N + DEV_N
    n_adversarial = round(HELD_OUT_N * ADVERSARIAL_TARGET)

    seeds: list[dict] = []
    idx = 1

    # A balanced urgency quota, consumed in shuffled order so the tiers stay even.
    quota = [URGENCY[i % len(URGENCY)] for i in range(total)]
    rng.shuffle(quota)

    def can_express(persona: str, urgency: str) -> bool:
        return any(urgency in allowed_urgency(s) for s in PLAUSIBLE[persona])

    def take(persona: str | None = None) -> str | None:
        """Pop a quota entry, preferring one this persona can actually express.

        Popping blindly is what starves the high tier: `SYS-BULK` and `EXT-COLD`
        have no scenario that can be urgent, so their draws would be consumed and
        silently downgraded.
        """
        if not quota:
            return None
        if persona is None:
            return quota.pop()
        for i in range(len(quota) - 1, -1, -1):
            if can_express(persona, quota[i]):
                return quota.pop(i)
        return None

    # Guarantee persona coverage in the held-out tier before free sampling.
    for persona in PERSONAS:
        for _ in range(MIN_PERSONA_HELD_OUT):
            seeds.append(build_seed(rng, idx, force_persona=persona,
                                    target_urgency=take(persona)))
            idx += 1

    # Free sampling picks the urgency first, then a persona that can carry it.
    while len(seeds) < total:
        urgency = take()
        eligible = [p for p in PERSONAS if urgency is None or can_express(p, urgency)]
        seeds.append(build_seed(rng, idx, force_persona=rng.choice(eligible),
                                target_urgency=urgency))
        idx += 1

    rng.shuffle(seeds)
    for tier_idx, seed in enumerate(seeds):
        seed["tier"] = "held-out" if tier_idx < HELD_OUT_N else "dev"

    # Promote held-out items to adversarial until the target share is met.
    held_out = [s for s in seeds if s["tier"] == "held-out"]
    have = sum(1 for s in held_out if s["adversarial"])
    for seed in held_out:
        if have >= n_adversarial:
            break
        if seed["adversarial"]:
            continue
        promote(rng, seed)
        have += 1

    seeds.sort(key=lambda s: s["id"])
    return seeds


FIELDS = ["id", "tier", "persona", "scenario", "urgency_intent", "thread",
          "register", "context", "adversarial"]


def report(seeds: list[dict]) -> None:
    held = [s for s in seeds if s["tier"] == "held-out"]
    print(f"total {len(seeds)}  held-out {len(held)}  dev {len(seeds) - len(held)}\n")

    def dist(field: str, rows: list[dict]) -> None:
        counts = Counter(r[field] or "-none-" for r in rows)
        line = "  ".join(f"{k}:{v}({v / len(rows):.0%})"
                         for k, v in sorted(counts.items(), key=lambda kv: -kv[1]))
        print(f"{field:16} {line}")

    for field in ("urgency_intent", "thread", "register", "context"):
        dist(field, held)

    adv = sum(1 for s in held if s["adversarial"])
    print(f"\nadversarial      {adv}/{len(held)} ({adv / len(held):.0%})  target >=33%")
    missing = sum(1 for s in held if s["context"] == "C-MISSING")
    print(f"C-MISSING        {missing}/{len(held)} ({missing / len(held):.0%})  target >=15%")
    esl = sum(1 for s in held if s["register"] == "R-ESL")
    print(f"R-ESL            {esl}/{len(held)} ({esl / len(held):.0%})  target >=15%")

    persona_counts = Counter(s["persona"] for s in held)
    thin = {p: c for p, c in persona_counts.items() if c < MIN_PERSONA_HELD_OUT}
    print(f"persona coverage {'OK' if not thin else f'THIN: {thin}'}  "
          f"(min {min(persona_counts.values())} per persona)")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="report distributions, write nothing")
    parser.add_argument("--out", default=str(Path(__file__).parent / "seeds.csv"))
    args = parser.parse_args()

    seeds = generate()
    report(seeds)

    if args.check:
        return

    with open(args.out, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows({k: s[k] for k in FIELDS} for s in seeds)
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
