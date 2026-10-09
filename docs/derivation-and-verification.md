# Continuous Reasoning Acquisition — Derivation, Verification, and Confidence

This document describes how Continuous Reasoning Acquisition (CRA) distinguishes:

- **Source**
- **Grounding**
- **Derivation**
- **Verification**
- **Confidence**

These dimensions answer different questions and should not be collapsed into a single status or score.

For the broader conceptual model, see:

[`/docs/data-model.md`](./data-model.md)

For a complete illustrative record, see:

[`/examples/complete-reasoning-trace.json`](../examples/complete-reasoning-trace.json)

---

## 1. Why these dimensions are separate

A reasoning-related statement may be:

- directly stated by the Subject,
- extracted from a longer response,
- inferred by a system,
- derived from multiple Sources,
- confirmed by the Subject,
- unconfirmed,
- high-confidence,
- low-confidence.

These properties are not interchangeable.

For example:

```text
Inferred
≠
Unconfirmed
≠
Low confidence
```

A system may produce an inference with high confidence that has never been verified.

Similarly, a directly stated claim may later be contradicted by another Source.

CRA therefore treats these dimensions independently.

---

## 2. Overview

At a high level:

```text
Source --(Derivation)--> Reasoning Unit
Reasoning Unit --(Grounding)--> Source(s)

Reasoning Unit
   ├── Verification
   └── Confidence
```

Each component answers a different question.

| Dimension | Question |
| ----- | ----- |
| Source | What original information is available? |
| Grounding | Which Source supports this Reasoning Unit? |
| Derivation | How was this Reasoning Unit produced? |
| Verification | Was the resulting Unit later confirmed or challenged? |
| Confidence | How certain is the extraction or inference? |

Grounding is not a processing stage between Source and Unit. It is the traceable relationship from a Reasoning Unit back to the information on which it is based.

---

## 3. Source

A **Source** is the original information available to the system.

Examples include:

- subject input
- elicitation response
- conversation transcript
- document
- operational record
- sensor data
- action record
- outcome record

Example:

```json
{
  "id": "source_003",
  "type": "elicitation_response",
  "origin": "subject",
  "elicitation_id": "elicitation_002",
  "content": "I thought they probably would not be able to get internal approval."
}
```

A model-generated interpretation is not automatically a Source.

If an LLM reads the Source and generates a new interpretation:

```text
original statement
→ Source

LLM-produced interpretation
→ derived Reasoning Unit
```

The transformation belongs to Derivation.

---

## 4. Grounding

**Grounding** links a Reasoning Unit to the Source or Sources on which it is based.

Example:

```json
{
  "grounding": {
    "source_ids": [
      "source_003"
    ]
  }
}
```

More precise Grounding may retain Source spans:

```json
{
  "grounding": {
    "source_ids": [
      "source_003"
    ],
    "spans": [
      {
        "source_id": "source_003",
        "start": 0,
        "end": 74
      }
    ]
  }
}
```

Depending on the Source type, Grounding may reference:

- text spans
- conversation turns
- document sections
- structured fields
- timestamps
- sensor intervals

Grounding answers:

> What information supports this Unit?

Grounding does not establish that the Unit is correct.

It only preserves traceability to the supporting information.

For higher-level Derivations such as abstraction or synthesis, Grounding may also reference existing Reasoning Units in addition to primary Sources, while preserving traceability from those Units back to their original Sources.

---

## 5. Derivation

**Derivation** describes how a Reasoning Unit was produced.

Illustrative Derivation types include:

- `direct`
- `extracted`
- `inferred`
- `abstracted`
- `synthesized`

These labels are not required to form a closed ontology.

Applications may extend or replace them while preserving the distinction between Source and transformation.

---

## 6. Direct

A Unit may be classified as **Direct** when substantially the same information already exists in the Source.

Example:

```text
Source:
"Postponed the price increase."

Reasoning Unit:
"Postponed the planned price increase."
```

Possible representation:

```json
{
  "derivation": {
    "type": "direct",
    "actor": "system"
  }
}
```

`direct` does not mean:

- verified
- correct
- high-confidence

It only describes the relationship between Source and Unit.

---

## 7. Extracted

A Unit is **Extracted** when the relevant information is explicitly available in the Source but has been selected, normalized, or structurally represented without introducing a new substantive claim.

Example:

```text
Source:
"I thought that even if I raised it then,
they probably would not be able to get internal approval."

Reasoning Unit:
"The Subject interpreted the situation as one in which internal approval
for the price increase was unlikely."
```

Possible representation:

```json
{
  "derivation": {
    "type": "extracted",
    "actor": "system"
  }
}
```

The extracted Unit may still be:

- `unconfirmed`
- `confirmed`
- `conflicting`
- `undetermined`

depending on later Verification.

**Extraction should preserve attribution and hedging.**

If a Source states what the Subject believed, guessed, suspected, or interpreted, an Extracted Unit should not restate that content as an objective fact.

For example:

```text
Source:
"I thought approval was probably difficult."

Valid Extracted Unit:
"The Subject judged that approval was probably difficult."

Not equivalent:
"Approval was difficult."
```

Changing attribution or certainty introduces information not explicitly preserved from the Source and is therefore closer to Inference than Extraction.

---

## 8. Inferred

A Unit is **Inferred** when it introduces a proposition that is not explicitly stated in its supporting Sources.

Example:

```text
Source 1:
"The atmosphere was tense."

Source 2:
"I thought they probably could not get internal approval."

Inferred Unit:
"If internal approval appears unlikely,
defer the price increase discussion."
```

Possible representation:

```json
{
  "derivation": {
    "type": "inferred",
    "actor": "system",
    "method": "llm_inference",
    "model": "example-model",
    "model_version": "example-1.0",
    "derived_at": "2026-09-01T17:35:00+09:00"
  }
}
```

An Inferred Unit should preserve Grounding to the Sources used for the inference.

---

## 9. Abstracted and Synthesized

A system may create a higher-level representation from multiple Sources or Reasoning Units.

Examples include:

- generalizing a recurring decision pattern
- combining multiple observations into one interpretation
- forming a reusable decision rule
- summarizing several Event-level Units

Depending on implementation, these may be represented as:

- `abstracted`
- `synthesized`

or another application-specific Derivation type.

Existing Reasoning Units may themselves be used as inputs to a higher-level Derivation.

In that case, Grounding may reference those Units while preserving a traceable path back to their original Sources.

The important requirement is that the transformation path remains recoverable.

---

## 10. Derivation provenance

For system-generated Units, Derivation may retain additional provenance.

Example:

```json
{
  "derivation": {
    "type": "inferred",
    "actor": "system",
    "method": "llm_inference",
    "model": "example-model",
    "model_version": "example-1.0",
    "derived_at": "2026-09-01T17:35:00+09:00"
  }
}
```

Possible metadata includes:

- actor
- method
- model
- model version
- prompt or rule version identifier
- pipeline version
- processing timestamp

CRA does not require production prompts themselves to be stored in the reasoning dataset.

An implementation may preserve only the identifier needed to reproduce or audit the transformation.

---

## 11. Verification

**Verification** records whether and how the resulting Reasoning Unit has been checked after it was produced.

Verification is separate from both Source and Derivation.

Suggested high-level statuses are:

- `confirmed`
- `unconfirmed`
- `conflicting`
- `undetermined`

---

## 12. Confirmed

`confirmed` means that a verification process produced positive confirmation of the Unit.

Example:

```json
{
  "verification": {
    "status": "confirmed",
    "method": "subject_review",
    "verified_at": "2026-09-02T09:00:00+09:00"
  }
}
```

Possible verification methods include:

- `subject_review`
- `expert_review`
- `cross_source_confirmation`
- `system_check`

The verification method should be stored separately from the status where practical.

### What Subject confirmation means

`confirmed` via `subject_review` indicates that the Subject agrees that the generated Unit accurately represents what they meant, recalled, or currently endorse.

It does **not** establish that the Unit is an objectively true reconstruction of the Subject's actual cognitive process at the time of the Event.

Self-reports may be:

- incomplete
- selective
- retrospectively reconstructed
- affected by later interpretation

Therefore:

```text
Subject-confirmed
≠
cognitively verified
```

Subject review validates correspondence with the Subject's report, not direct access to internal cognition.

---

## 13. Unconfirmed

`unconfirmed` means that no completed verification result is available.

For example:

```text
system extracts Unit
→ no later review occurs
→ unconfirmed
```

Example:

```json
{
  "verification": {
    "status": "unconfirmed"
  }
}
```

`unconfirmed` does not mean the Unit is likely incorrect.

It means that Verification has not produced a result.

---

## 14. Conflicting

`conflicting` means that Verification identified evidence inconsistent with the Unit.

Example:

```text
Unit:
"The customer rejected the proposal because of price."

Later Subject review:
"Price was not the reason. The implementation risk was the issue."
```

Possible representation:

```json
{
  "verification": {
    "status": "conflicting",
    "method": "subject_review",
    "verified_at": "2026-09-02T09:00:00+09:00"
  }
}
```

The original Unit does not necessarily need to be deleted.

Keeping both the original representation and the later conflicting evidence may be useful for provenance and revision history.

---

## 15. Undetermined

`undetermined` means that Verification was attempted but did not produce a determinate result.

Example:

```text
System:
"Was this interpretation accurate?"

Subject:
"I'm not sure anymore."
```

Possible representation:

```json
{
  "verification": {
    "status": "undetermined",
    "method": "subject_review",
    "verified_at": "2026-09-02T09:00:00+09:00"
  }
}
```

The distinction is:

- `unconfirmed` = no completed verification result is available
- `undetermined` = verification was attempted, but no determinate conclusion could be reached

This is separate from the Elicitation state `elicited_but_unresolved`, which refers to acquisition of the underlying reasoning information rather than Verification of a generated Reasoning Unit.

---

## 16. Verification is not Source attribution

Consider:

```text
Subject response:
"I thought internal approval would be difficult."
```

The response becomes a Source.

The system then generates:

```text
Reasoning Unit:
"The Subject judged that internal approval would be difficult."
```

with Derivation `extracted`.

Unless the Subject later reviews the generated Unit, its Verification remains `unconfirmed`.

Therefore:

```text
Subject provided the Source
≠
Subject confirmed the generated Unit
```

This distinction is central to CRA.

---

## 17. Verification is not Grounding

A Reasoning Unit may be strongly Grounded but still incorrect.

For example:

```text
Source:
"The customer asked about implementation risk several times."

Inferred Unit:
"Implementation risk was the primary objection."
```

The Source clearly supports why the inference was made.

That establishes Grounding.

It does not prove that the inference is true.

Therefore:

```text
Grounding
≠
Verification
```

---

## 18. Confidence

**Confidence** represents the estimated certainty associated with an extraction, inference, or other transformation.

Example:

```json
{
  "confidence": "medium"
}
```

Confidence may be represented as:

- low / medium / high
- numeric score
- probability-like score
- human-assigned estimate
- model-specific score

CRA does not prescribe a universal Confidence scale.

Where Confidence is used, the method by which it was produced should ideally remain identifiable.

For example:

```json
{
  "confidence": {
    "value": "medium",
    "method": "model_estimate"
  }
}
```

An implementation may use a simpler scalar representation where appropriate, but should avoid making confidence values appear comparable across systems unless they were generated under compatible methods.

---

## 19. Confidence is independent from Derivation

An Inferred Unit does not necessarily have low Confidence.

For example:

- Derivation: `inferred`
- Confidence: `high`

may occur when multiple independent Sources strongly support the inference.

Conversely:

- Derivation: `extracted`
- Confidence: `low`

may occur when the original Source is ambiguous.

Therefore:

```text
Derivation
≠
Confidence
```

---

## 20. Confidence is independent from Verification

Confidence is also separate from Verification.

All of the following combinations are possible:

- `high` confidence + `unconfirmed`
- `low` confidence + `confirmed`
- `high` confidence + `conflicting`
- `medium` confidence + `undetermined`

For example:

- system confidence: `high`
- Subject review: `conflicting`

means the system was highly certain about an interpretation that the Subject later rejected.

This is valuable information and should not be collapsed into a single score.

---

## 21. Example combinations

### `extracted` + `unconfirmed`

```json
{
  "derivation": {
    "type": "extracted"
  },
  "verification": {
    "status": "unconfirmed"
  }
}
```

Meaning:

> the Unit was extracted from explicit Source content, but no later verification was completed.

---

### `extracted` + `confirmed`

```json
{
  "derivation": {
    "type": "extracted"
  },
  "verification": {
    "status": "confirmed",
    "method": "subject_review"
  }
}
```

Meaning:

> the Unit was extracted from a Source and later confirmed as an accurate representation of the Subject's report.

---

### `inferred` + `unconfirmed`

```json
{
  "derivation": {
    "type": "inferred"
  },
  "verification": {
    "status": "unconfirmed"
  }
}
```

Meaning:

> the system inferred the Unit, and no verification result is available.

---

### `inferred` + `confirmed`

```json
{
  "derivation": {
    "type": "inferred"
  },
  "verification": {
    "status": "confirmed",
    "method": "subject_review"
  }
}
```

Meaning:

> the system inferred information that was not directly stated in the Source, and the Subject later confirmed that the resulting Unit represented their intended or endorsed interpretation.

This does not establish direct access to the Subject's original cognitive process.

---

## 22. Example complete Unit

```json
{
  "id": "unit_004",
  "type": "decision_rule",
  "content": "If internal approval appears unlikely under the current conditions, defer raising the price increase until a more suitable opportunity.",
  "related_gap_ids": [
    "gap_003"
  ],
  "grounding": {
    "source_ids": [
      "source_002",
      "source_003"
    ]
  },
  "derivation": {
    "type": "inferred",
    "actor": "system",
    "method": "llm_inference",
    "model": "example-model",
    "model_version": "example-1.0",
    "derived_at": "2026-09-01T17:35:00+09:00"
  },
  "verification": {
    "status": "unconfirmed"
  },
  "confidence": {
    "value": "medium",
    "method": "model_estimate",
    "note": "Inferred from two sources without direct elicitation of the decision criterion."
  }
}
```

This example means:

- the Unit exists
- the Unit is supported by two Sources
- the Unit was inferred rather than explicitly stated
- the Unit has not been verified
- the system assigned medium confidence
- the related Gap (`gap_003`) was not elicited

Each fact is represented independently.

---

## 23. Revision and re-derivation

Reasoning representations may change over time.

For example:

```text
new Source added
→ existing inference becomes questionable
→ Unit is revised
```

or:

```text
new model version
→ Reasoning Unit is re-derived
```

An implementation may preserve:

- previous Unit
- new Unit
- revision relationship
- Derivation metadata for each version
- Verification state for each version

rather than silently overwriting the previous representation.

Possible relationship:

```json
{
  "from": "unit_008_v2",
  "type": "revises",
  "to": "unit_008_v1"
}
```

CRA does not require a specific versioning mechanism, but provenance should remain recoverable where revisions materially affect interpretation.

---

## 24. Application-specific policy

Different systems may choose different policies for when Verification is required.

For example:

```text
low-risk coaching application
→ verification may be optional

research dataset
→ selected Units may require Subject confirmation

high-impact decision support
→ inferred Units may require additional review
```

CRA does not prescribe a universal Verification policy.

It defines the structure needed to represent whether and how Verification occurred.

---

## 25. What this specification does not define

This document does not define:

- how inference confidence is calculated
- which Units must be verified
- which verification method is authoritative
- how disagreements should be resolved
- which model should perform extraction or inference
- production prompts
- inference thresholds
- automatic acceptance rules

These decisions are implementation-specific.

---

## 26. Current Specification Status

This document describes an implementation-facing conceptual model.

It is not currently intended as a finalized interoperability standard.

Future versions may formalize:

- Derivation enums
- Verification enums
- Confidence representation
- provenance fields
- revision semantics
- Grounding span formats
- cross-record references

while preserving the independence of the core dimensions described here.

---

## Related Resources

- [README](../README.md)
- [Complete Reasoning Trace Example](../examples/complete-reasoning-trace.json)
- [Data Model](./data-model.md)
- [Elicitation History](./elicitation-history.md)
- [JSON Schema](../schema/reasoning-trace.schema.json)
- Preprint: [10.5281/zenodo.23215881](https://doi.org/10.5281/zenodo.23215881)
