# Examples

This folder contains illustrative records for Continuous Reasoning Acquisition (CRA).

| File | Description |
|---|---|
| [`complete-reasoning-trace.json`](./complete-reasoning-trace.json) | A complete example record including Sources, Elicitation History, Reasoning Units, Grounding, Derivation, Verification, and Confidence. |

The example is constructed for explanation only. **It is not derived from real user data.**

---

## Validating the example

The example conforms to the schema in [`/schema/reasoning-trace.schema.json`](../schema/reasoning-trace.schema.json).

For example, using `check-jsonschema`:

```text
pip install check-jsonschema
check-jsonschema --schemafile schema/reasoning-trace.schema.json examples/complete-reasoning-trace.json
```

Note that the schema does not check whether referenced identifiers (such as `grounding.source_ids`) actually exist in the record. Referential integrity should be validated separately.

---

## Scenario

A B2B salesperson (the Subject) visited an existing customer and had planned to present a price increase.

During the meeting, the Subject decided **not** to present it.

The only initial record was a short work note:

> "Postponed the price increase discussion this time. Will raise it at the next meeting."

This note tells us **what** happened, but not **why**.

---

## What happened during acquisition

### 1. Initial state

From the work note (`source_001`), only the action was known.

Three Gaps were detected:

| Gap | Target | Meaning |
|---|---|---|
| `gap_001` | `reason_for_action` | Why was the price increase postponed? |
| `gap_002` | `situation_recognition` | What situation influenced the decision? |
| `gap_003` | `decision_criterion` | What criterion was used to decide? |

### 2. First question

The system asked about `gap_001`:

> "Why did you decide not to raise the price increase this time?"

The Subject answered (`source_002`):

> "The person in charge seemed to be under pressure from their manager, and the atmosphere was tense."

This single answer resolved **two** Gaps:

- `gap_001` — directly, because it was the target of the question
- `gap_002` — incidentally, because the answer also described the situation

The answer also revealed a new Gap:

- `gap_004` — how the Subject interpreted that tense situation

### 3. Second question

The system asked about `gap_004`:

> "What made you think this was not a good timing to raise the price increase?"

The Subject answered (`source_003`):

> "I thought that even if I raised it then, they probably would not be able to get internal approval."

This resolved `gap_004`.

### 4. Stopping

Acquisition stopped because the maximum number of elicitation steps (2) was reached.

`gap_003` (decision criterion) was detected but **never asked about**.

---

## Final Gap states

| Gap | Source state | Elicitation state | Resolved by |
|---|---|---|---|
| `gap_001` | `not_observed` | `elicited_and_resolved` | `elicitation_001` |
| `gap_002` | `not_observed` | `elicited_and_resolved` | `elicitation_001` (incidental) |
| `gap_003` | `not_observed` | **`not_elicited`** | — |
| `gap_004` | `observed_but_insufficient` | `elicited_and_resolved` | `elicitation_002` |

`gap_004` is `observed_but_insufficient` because `source_002` already described the tense situation, but did not yet contain the Subject's interpretation of it.

---

## Reasoning Units

| Unit | Type | Derivation | Verification | Confidence |
|---|---|---|---|---|
| `unit_001` | `action` | `direct` | `unconfirmed` | `high` |
| `unit_002` | `situation_recognition` | `extracted` | `unconfirmed` | `high` |
| `unit_003` | `interpretation` | `extracted` | **`confirmed`** | `medium` |
| `unit_004` | `decision_rule` | **`inferred`** | `unconfirmed` | `medium` |
| `unit_005` | `outcome` | `direct` | `unconfirmed` | `high` |

---

## What to notice

### Derivation, Verification, and Confidence are independent

- `unit_003` was **extracted** from the Subject's answer, has only **medium** confidence because the answer contains hedging ("probably"), and was later **confirmed** by the Subject.
- `unit_004` was **inferred** by the system, yet its confidence is **medium**, not low.

Inferred does not mean low confidence, and medium confidence does not mean unconfirmed.

### A Unit can exist even when its Gap was never elicited

`unit_004` is a decision rule:

> "If internal approval appears unlikely under the current conditions, defer raising the price increase until a more suitable opportunity."

The Subject never stated this rule. The system inferred it from `source_002` and `source_003`.

At the same time, the related Gap (`gap_003`) is `not_elicited`.

The record therefore preserves both facts:

```text
the decision rule exists as a Reasoning Unit
+
the Subject was never asked about it
```

Without the Elicitation History, `unit_004` could easily be mistaken for something the Subject said.

### Providing a Source is not the same as confirming a Unit

`unit_002` is grounded in the Subject's own answer, but its Verification is still `unconfirmed`.

The Subject provided the Source; the Subject has not reviewed the Unit the system produced from it.

Only `unit_003` went through a separate review (`subject_review`).

### Extracted Units preserve attribution

`unit_002` and `unit_003` are written as what the Subject perceived or interpreted, not as objective facts.

For example, `unit_003` states that the Subject interpreted the situation as one in which internal approval was unlikely — not that approval *was* unlikely.

See [Derivation, Verification, and Confidence](../docs/derivation-and-verification.md) for the rationale.

---

## Related documents

- [Data Model](../docs/data-model.md)
- [Elicitation History](../docs/elicitation-history.md)
- [Derivation, Verification, and Confidence](../docs/derivation-and-verification.md)
- [Schema](../schema/reasoning-trace.schema.json)
- [Repository README](../README.md)
