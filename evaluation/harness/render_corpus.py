#!/usr/bin/env python3
"""
Render seeds into emails/threads — step 2 of #104.

Also implements step 5's acceptance criterion: **the dev/held-out split is
enforced in code**, not by convention. Reading the held-out tier requires an
explicit flag and is appended to an audit log, so "held-out was read exactly
three times (Week 3, M11, final)" becomes a checkable claim rather than an
assertion in the report.

No third-party dependencies — stdlib only, so it runs anywhere.

Usage:
    # see what would be sent, call nothing (works with no cloud access)
    ./render_corpus.py --tier dev --dry-run

    # actually render the dev tier
    ./render_corpus.py --tier dev

    # held-out requires the guard flag AND a stated reason for the audit log
    ./render_corpus.py --tier heldout --confirm-heldout --reason "Week 3 checkpoint"
"""

import argparse
import csv
import datetime as dt
import json
import os
import pathlib
import subprocess
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
MATRIX = ROOT / "corpus" / "seed-matrix-v1.csv"
OUT_ROOT = ROOT / "corpus" / "rendered"
AUDIT = ROOT / "corpus" / "heldout-access.log"

PROJECT = os.environ.get("GCP_PROJECT", "frank-gmail-assistant")
LOCATION = os.environ.get("VERTEX_LOCATION", "global")
MODEL = os.environ.get("VERTEX_MODEL", "gemini-2.5-flash")

RENDER_INSTRUCTION = """\
You are generating synthetic email data for an academic benchmark. None of this \
describes real people; do not use real names, addresses, phone numbers or any \
other identifying detail.

For each seed below, write the email or thread it specifies. Follow the seed \
exactly: the sender/recipient roles, the scenario, the number of messages, the \
register, and what context the reader is missing.

Rules:
- Write what a real inbox looks like, not a polished example. Real subject lines, \
real sign-offs, occasional untidiness.
- `context` says what the READER does not have. `missing_prior` means key \
information sits in an earlier message that is NOT included. `missing_referent` \
means something is referred to but never identified. `missing_attachment` means \
an attachment is referenced but absent. Honour it — do not helpfully supply the \
missing information.
- Do NOT state or hint at the priority. `seeded_intent` is a design note, not \
content. Humans label the rendered text later; if the priority is stated the \
label becomes circular and the corpus is worthless.
- Use Australian university context and spelling.

Return JSON only, matching this shape:
{"emails": [{"seed_id": "...", "subject": "...",
             "messages": [{"from": "...", "to": "...", "sent": "...", "body": "..."}]}]}
"""


def load_seeds(tier):
    with MATRIX.open() as fh:
        return [r for r in csv.DictReader(fh) if r["tier"] == tier]


def guard_heldout(args):
    """Step 5: held-out is not readable casually, and every read is recorded."""
    if args.tier != "heldout":
        return
    if not args.confirm_heldout or not args.reason:
        sys.exit(
            "REFUSED: the held-out tier is not for prompt iteration.\n"
            "  Every number in the report comes from this tier, and tuning on it\n"
            "  makes those numbers meaningless. If this really is one of the three\n"
            "  planned runs, pass --confirm-heldout --reason '<why>'."
        )
    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT.open("a") as fh:
        fh.write(json.dumps({
            "when": dt.datetime.now(dt.timezone.utc).isoformat(),
            "reason": args.reason,
            "user": os.environ.get("USER", "unknown"),
            "model": MODEL,
        }) + "\n")
    n = sum(1 for _ in AUDIT.open())
    print(f"[audit] held-out access #{n} recorded: {args.reason}", file=sys.stderr)
    if n > 3:
        print(
            f"[audit] WARNING: {n} held-out reads. The plan plus #102 plan exactly three\n"
            f"        (Week 3, M11, final). Extra reads need explaining in the report.",
            file=sys.stderr,
        )


def build_prompt(batch):
    lines = []
    for s in batch:
        lines.append(
            f"- seed_id={s['seed_id']} from={s['persona_from']} to={s['persona_to']} "
            f"messages={s['thread_length']} register={s['register']} "
            f"context={s['context']}\n  scenario: {s['scenario']}"
        )
    return RENDER_INSTRUCTION + "\nSeeds:\n" + "\n".join(lines)


def access_token():
    try:
        return subprocess.run(
            ["gcloud", "auth", "print-access-token"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        sys.exit(f"could not get a gcloud access token: {exc}")


def call_vertex(prompt):
    host = "aiplatform.googleapis.com" if LOCATION == "global" else f"{LOCATION}-aiplatform.googleapis.com"
    url = (f"https://{host}/v1/projects/{PROJECT}/locations/{LOCATION}"
           f"/publishers/google/models/{MODEL}:generateContent")
    body = json.dumps({
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 1.0},
    }).encode()
    req = urllib.request.Request(url, data=body, headers={
        "Authorization": f"Bearer {access_token()}",
        "Content-Type": "application/json",
    })
    try:
        with urllib.request.urlopen(req) as resp:
            payload = json.load(resp)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode()[:500]
        sys.exit(f"Vertex returned {exc.code}:\n{detail}\n\n"
                 f"If this is 403 SERVICE_DISABLED, enable the API first:\n"
                 f"  gcloud services enable aiplatform.googleapis.com --project {PROJECT}")
    return json.loads(payload["candidates"][0]["content"]["parts"][0]["text"])


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tier", choices=["dev", "heldout"], required=True)
    ap.add_argument("--batch-size", type=int, default=5)
    ap.add_argument("--dry-run", action="store_true",
                    help="write the prompts and call nothing — needs no cloud access")
    ap.add_argument("--confirm-heldout", action="store_true")
    ap.add_argument("--reason", help="why held-out is being read; goes in the audit log")
    args = ap.parse_args()

    guard_heldout(args)

    seeds = load_seeds(args.tier)
    batches = [seeds[i:i + args.batch_size] for i in range(0, len(seeds), args.batch_size)]
    out_dir = OUT_ROOT / args.tier
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"{len(seeds)} seeds -> {len(batches)} calls (batch size {args.batch_size})")

    rendered = 0
    for i, batch in enumerate(batches, 1):
        prompt = build_prompt(batch)
        if args.dry_run:
            (out_dir / f"prompt-{i:03d}.txt").write_text(prompt)
            continue
        print(f"  call {i}/{len(batches)} …", file=sys.stderr)
        for email in call_vertex(prompt).get("emails", []):
            (out_dir / f"{email['seed_id']}.json").write_text(json.dumps(email, indent=2))
            rendered += 1

    if args.dry_run:
        print(f"dry run — {len(batches)} prompts written to {out_dir}. Nothing was called.")
        return

    # Step 6: the corpus is only reproducible if we record what made it.
    (out_dir / "manifest.json").write_text(json.dumps({
        "generated": dt.datetime.now(dt.timezone.utc).isoformat(),
        "model": MODEL, "location": LOCATION, "project": PROJECT,
        "matrix": MATRIX.name, "tier": args.tier,
        "seeds": len(seeds), "rendered": rendered, "calls": len(batches),
    }, indent=2))
    print(f"rendered {rendered}/{len(seeds)} in {len(batches)} calls -> {out_dir}")


if __name__ == "__main__":
    main()
