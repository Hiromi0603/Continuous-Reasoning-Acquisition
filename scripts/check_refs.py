"""Referential-integrity check for a CRA reasoning-trace record.

The JSON Schema does not check whether referenced identifiers exist.
This script checks that every ID reference in a record points to an existing
object, and reports a few semantic inconsistencies as warnings.

Usage:
    python scripts/check_refs.py [path/to/record.json]

Exits with status 1 if any reference error is found.
"""
import json
import pathlib
import sys

DEFAULT = pathlib.Path(__file__).resolve().parent.parent / "examples" / "complete-reasoning-trace.json"
path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT
rec = json.load(open(path, encoding="utf-8"))
errors, warnings = [], []
eh = rec.get("elicitation_history", {})
rt = rec["reasoning_trace"]

source_ids = [s["id"] for s in rec.get("sources", [])]
gap_ids = [g["id"] for g in eh.get("gaps", [])]
step_ids = [s["id"] for s in eh.get("elicitation_steps", [])]
unit_ids = [u["id"] for u in rt.get("reasoning_units", [])]

all_ids = {}
for kind, ids in [("source", source_ids), ("gap", gap_ids), ("elicitation_step", step_ids), ("unit", unit_ids),
                  ("subject", [rec["subject"]["id"]]), ("event", [rec["event"]["id"]]),
                  ("trace", [rt["id"]]),
                  ("action", [rec["action"]["id"]] if "action" in rec else []),
                  ("outcome", [rec["outcome"]["id"]] if "outcome" in rec else [])]:
    for i in ids:
        if i in all_ids:
            errors.append(f"duplicate id {i!r} ({all_ids[i]} / {kind})")
        all_ids[i] = kind

def ref(path, value, allowed, label):
    if value is None:
        return
    ok = value in allowed
    print(f"  [{'OK' if ok else 'NG'}] {path} -> {value!r} ({label})")
    if not ok:
        errors.append(f"{path}: {value!r} is not an existing {label}")

S, G, E, U = set(source_ids), set(gap_ids), set(step_ids), set(unit_ids)

ref("reasoning_trace.subject_id", rt.get("subject_id"), {rec["subject"]["id"]}, "subject.id")
ref("reasoning_trace.event_id", rt.get("event_id"), {rec["event"]["id"]}, "event.id")
ref("representation.derived_from_trace", rec.get("representation", {}).get("derived_from_trace"), {rt["id"]}, "reasoning_trace.id")

for i, s in enumerate(rec.get("sources", [])):
    ref(f"sources[{i}].elicitation_id", s.get("elicitation_id"), E, "elicitation step")

init = eh.get("initial_state", {})
for j, x in enumerate(init.get("available_sources", [])):
    ref(f"initial_state.available_sources[{j}]", x, S, "source")
for j, x in enumerate(init.get("active_gap_ids", [])):
    ref(f"initial_state.active_gap_ids[{j}]", x, G, "gap")

for i, g in enumerate(eh.get("gaps", [])):
    ref(f"gaps[{i}].detected_at", g.get("detected_at"), E | {"initial"}, "elicitation step or 'initial'")

for i, st in enumerate(eh.get("elicitation_steps", [])):
    p = f"elicitation_steps[{i}]"
    ref(f"{p}.triggered_by_gap", st.get("triggered_by_gap"), G, "gap")
    ref(f"{p}.response_source", st.get("response_source"), S, "source")
    for k in ("resolved_gaps", "new_gaps_detected"):
        for j, x in enumerate(st.get(k, [])):
            ref(f"{p}.{k}[{j}]", x, G, "gap")
    # back-link: response source should point back to this step
    rs = st.get("response_source")
    src = next((s for s in rec["sources"] if s["id"] == rs), None)
    if src and src.get("elicitation_id") != st["id"]:
        errors.append(f"{p}: response_source {rs} has elicitation_id {src.get('elicitation_id')!r}, expected {st['id']!r}")

for i, gs in enumerate(eh.get("final_gap_states", [])):
    p = f"final_gap_states[{i}]"
    ref(f"{p}.gap_id", gs.get("gap_id"), G, "gap")
    ref(f"{p}.resolved_by", gs.get("resolved_by"), E, "elicitation step")
    ref(f"{p}.elicitation_id", gs.get("elicitation_id"), E, "elicitation step")
    # consistency: resolved_by step must list this gap in resolved_gaps
    rb = gs.get("resolved_by")
    step = next((s for s in eh.get("elicitation_steps", []) if s["id"] == rb), None)
    if step and gs["gap_id"] not in step.get("resolved_gaps", []):
        errors.append(f"{p}: {rb}.resolved_gaps does not contain {gs['gap_id']}")

stp = eh.get("stopping", {})
for k in ("remaining_unresolved_gaps", "remaining_not_elicited_gaps"):
    for j, x in enumerate(stp.get(k, [])):
        ref(f"stopping.{k}[{j}]", x, G, "gap")

for i, u in enumerate(rt.get("reasoning_units", [])):
    p = f"reasoning_units[{i}]({u['id']})"
    gr = u.get("grounding", {})
    for j, x in enumerate(gr.get("source_ids", [])):
        ref(f"{p}.grounding.source_ids[{j}]", x, S, "source")
    for j, x in enumerate(gr.get("unit_ids", [])):
        ref(f"{p}.grounding.unit_ids[{j}]", x, U - {u["id"]}, "other unit")
    for j, sp in enumerate(gr.get("spans", [])):
        ref(f"{p}.grounding.spans[{j}].source_id", sp.get("source_id"), set(gr.get("source_ids", [])), "source listed in grounding.source_ids")
    for j, x in enumerate(u.get("related_gap_ids", [])):
        ref(f"{p}.related_gap_ids[{j}]", x, G, "gap")
    if "action_id" in u:
        ref(f"{p}.action_id", u["action_id"], {rec.get("action", {}).get("id")}, "action.id")
    if "outcome_id" in u:
        ref(f"{p}.outcome_id", u["outcome_id"], {rec.get("outcome", {}).get("id")}, "outcome.id")

for i, r in enumerate(rt.get("relations", [])):
    ref(f"relations[{i}].from", r.get("from"), U, "unit")
    ref(f"relations[{i}].to", r.get("to"), U, "unit")

# --- semantic cross-checks (warnings) ---
final = {g["gap_id"]: g for g in eh.get("final_gap_states", [])}
if set(final) != G:
    warnings.append(f"final_gap_states covers {sorted(final)} but gaps are {sorted(G)}")
ne = sorted(g for g, s in final.items() if s["elicitation_state"] == "not_elicited")
if ne != sorted(stp.get("remaining_not_elicited_gaps", [])):
    warnings.append(f"remaining_not_elicited_gaps {stp.get('remaining_not_elicited_gaps')} != not_elicited gaps {ne}")
nu = sorted(g for g, s in final.items() if s["elicitation_state"] == "elicited_but_unresolved")
if nu != sorted(stp.get("remaining_unresolved_gaps", [])):
    warnings.append(f"remaining_unresolved_gaps {stp.get('remaining_unresolved_gaps')} != elicited_but_unresolved gaps {nu}")
if stp.get("completed_elicitation_steps") not in (None, len(step_ids)):
    warnings.append(f"completed_elicitation_steps={stp['completed_elicitation_steps']} but {len(step_ids)} steps recorded")
seqs = [s["sequence"] for s in eh.get("elicitation_steps", [])]
if seqs != list(range(1, len(seqs) + 1)):
    warnings.append(f"elicitation step sequences not 1..n: {seqs}")
for g in eh.get("gaps", []):
    if g["detected_at"] == "initial" and g["id"] not in init.get("active_gap_ids", []):
        warnings.append(f"{g['id']} detected 'initial' but not in initial_state.active_gap_ids")
    if g["detected_at"] != "initial":
        st = next((s for s in eh["elicitation_steps"] if s["id"] == g["detected_at"]), None)
        if st and g["id"] not in st.get("new_gaps_detected", []):
            warnings.append(f"{g['id']} detected_at {g['detected_at']} but not in its new_gaps_detected")
referenced = set()
for r in rt.get("relations", []):
    referenced |= {r["from"], r["to"]}
for u in unit_ids:
    if u not in referenced:
        warnings.append(f"{u} is not referenced by any relation (informational)")

print("\nERRORS:" if errors else "\nERRORS: none")
for e in errors: print("  -", e)
print("WARNINGS:" if warnings else "WARNINGS: none")
for w in warnings: print("  -", w)
sys.exit(1 if errors else 0)
