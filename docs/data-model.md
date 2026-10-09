# Continuous Reasoning Acquisition — Data Model

This document describes the conceptual data model used by Continuous Reasoning Acquisition (CRA).

The purpose of the model is not to prescribe a specific database schema.

It defines the information that should remain distinguishable when reasoning-related data is acquired, derived, verified, and accumulated across real-world events.

For a complete illustrative record, see:

[`/examples/complete-reasoning-trace.json`](../examples/complete-reasoning-trace.json)

---

## 1. Design Goals

The CRA data model is designed to preserve:

1. **who** the reasoning data belongs to,
2. **which event** it relates to,
3. **what reasoning-related information** was represented,
4. **which source** supports each representation,
5. **how** each Reasoning Unit was generated,
6. whether the generated Unit was later **verified**,
7. the estimated **confidence** of extraction or inference where applicable,
8. what information was **elicited, not elicited, or unresolved**,
9. when the event, acquisition, and transformation occurred.

A key design principle is that these dimensions should not be collapsed into a single field.

For example:

```text
Source
≠
Derivation
≠
Verification
≠
Confidence
```

and:

```text
Reasoning Unit does not exist
≠
information was not elicited
```

---

## 2. Conceptual Overview

At a high level:

```text
Subject
  │
  └── Event
        │
        ├── Action
        ├── Outcome
        ├── Source(s)
        │
        └── Reasoning Trace
              │
              └── Reasoning Unit(s)
                    │
                    ├── Grounding → Source(s)
                    ├── Derivation
                    ├── Verification
                    ├── Confidence
                    └── related Gap(s)

Event
  │
  └── Elicitation History
        │
        ├── Gap(s)
        ├── Elicitation Step(s)
        └── Stopping
```

The acquisition process and the final reasoning representation are deliberately separated.

---

## 3. Core Entities

### 3.1 Subject

A **Subject** is the person whose reasoning-related information is being acquired.

Minimum conceptual fields:

```json
{
  "id": "subject_001"
}
```

Optional metadata may include:

- pseudonymous identifier
- role
- organization
- domain
- cohort

CRA does not require real names.

For longitudinal analysis, the important requirement is that multiple Reasoning Traces belonging to the same Subject can be linked.

---

### 3.2 Event

An **Event** is the real-world occurrence around which reasoning information is acquired.

Examples include:

- sales conversation
- support interaction
- clinical judgment
- operational incident
- design decision
- research decision
- management decision

An Event provides the context to which a Reasoning Trace is grounded.

Example:

```json
{
  "id": "event_001",
  "type": "customer_meeting",
  "occurred_at": "2026-09-01T10:00:00+09:00"
}
```

CRA does not require a fixed Event taxonomy.

Different applications may define Event boundaries differently.

---

### 3.3 Reasoning Trace

A **Reasoning Trace** groups reasoning-related information associated with an Event.

It is not intended to represent a complete reconstruction of the Subject's internal cognition.

A Reasoning Trace represents:

> the reasoning-related information that could be acquired and represented for a particular Event.

Conceptually:

```text
Event
→ Reasoning Trace
→ Reasoning Units
```

A single Event may contain one or more Reasoning Traces depending on the implementation.

---

### 3.4 Reasoning Unit

A **Reasoning Unit** is a semantically distinguishable unit of reasoning-related information.

Possible examples include:

- observation
- situation recognition
- interpretation
- hypothesis
- decision rule
- rationale
- action
- outcome

These types are illustrative.

CRA does not require a universal Reasoning Unit taxonomy.

Example:

```json
{
  "id": "unit_003",
  "type": "interpretation",
  "content": "The Subject interpreted the situation as one in which internal approval for the price increase was unlikely."
}
```

The semantic type of a Reasoning Unit belongs to the Representation Layer and may be reclassified later.

---

### 3.5 Source

A **Source** is the original information on which a Reasoning Unit is based.

Examples:

- subject input
- elicitation response
- conversation
- document
- operational log
- action record
- outcome record
- sensor data

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

An elicitation response is stored as a Source and may be linked back to the corresponding Elicitation History through `elicitation_id`.

A model-generated interpretation is **not** itself a Source merely because a model produced it.

For example:

```text
conversation transcript = Source
LLM inference from transcript = Derivation
```

---

### 3.6 Action

An **Action** represents a choice or behavior taken in relation to the Event.

Example:

```json
{
  "id": "action_001",
  "content": "Postponed presenting the planned price increase."
}
```

A Reasoning Unit may refer to the same Action:

```json
{
  "type": "action",
  "action_id": "action_001"
}
```

This allows the Reasoning representation to reference the underlying domain object rather than creating an unrelated duplicate.

---

### 3.7 Outcome

An **Outcome** represents an observed result or state change associated with the Event or Action.

Example:

```json
{
  "id": "outcome_001",
  "content": "The price increase was not discussed during the meeting."
}
```

As with Action, a Reasoning Unit may reference the underlying Outcome entity.

---

### 3.8 Temporal Information

CRA distinguishes the timing of:

- Event occurrence
- Source capture
- Elicitation
- Reasoning Unit derivation
- Verification
- Trace construction

These timestamps may differ.

Example:

```text
Event occurred:
2026-09-01 10:00

Subject entered record:
2026-09-01 17:30

System inferred Reasoning Unit:
2026-09-01 17:35

Subject verified Unit:
2026-09-02 09:00
```

Preserving these distinctions is useful for longitudinal and provenance analysis.

---

## 4. Grounding

**Grounding** represents the traceable relationship between a Reasoning Unit and one or more Sources.

Conceptually:

```text
Reasoning Unit
→ grounded in
→ Source(s)
```

Simple example:

```json
{
  "grounding": {
    "source_ids": [
      "source_002",
      "source_003"
    ]
  }
}
```

Grounding may also point to finer-grained regions of a Source.

Example:

```json
{
  "grounding": {
    "source_ids": [
      "source_002"
    ],
    "spans": [
      {
        "source_id": "source_002",
        "start": 0,
        "end": 58
      }
    ]
  }
}
```

Depending on the Source type, fine-grained Grounding may refer to:

- text spans
- document sections
- log fields
- timestamps
- conversation turns
- sensor intervals

If a grounding list would be empty, omit the key instead of providing an empty array. A Reasoning Unit with Grounding must be grounded in at least one Source or Reasoning Unit.

Grounding answers:

> What information was this Reasoning Unit based on?

It does **not** answer:

> Was the Reasoning Unit correct?

and it does **not** answer:

> How was the Reasoning Unit generated?

Those are handled separately.

---

## 5. Derivation

**Derivation** describes how a Reasoning Unit was produced from its Source or Sources.

Illustrative types include:

### Direct

The Source already contains substantially the same information.

```text
Source:
"Postponed the price increase."

Unit:
"Postponed the planned price increase."
```

### Extracted

The information is explicitly present in the Source but has been normalized, reorganized, or structurally extracted.

### Inferred

The Unit contains information that is not explicitly stated in the Source and is inferred from one or more Sources or contextual information.

### Abstracted / Synthesized

The Unit combines or generalizes information from multiple Sources or existing Reasoning Units.

These values are not required to form a closed taxonomy.

Applications may extend or replace them.

---

## 6. Derivation Provenance

For system-generated Units, Derivation may optionally retain information about the transformation process.

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

Possible provenance fields include:

- actor
- method
- model
- model version
- rule or algorithm version
- processing timestamp

The exact implementation is application-specific.

---

## 7. Verification

**Verification** records whether and how a generated Reasoning Unit has been confirmed.

Verification is independent from Derivation.

For example:

```text
extracted + unconfirmed
extracted + confirmed
inferred  + unconfirmed
inferred  + confirmed
```

are all conceptually valid combinations.

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

Suggested high-level statuses include:

- `confirmed`
- `unconfirmed`
- `conflicting`
- `undetermined`

`unconfirmed` means that no verification has been completed or no verification result is available.

`undetermined` means that verification was attempted, but the verification result could not be determined.

The verification method should be represented separately where needed.

Examples:

- `subject_review`
- `expert_review`
- `cross_source_confirmation`
- `system_check`

CRA does not assume that Grounding implies Verification.

A Unit may be well grounded in a Source while still being an incorrect interpretation of that Source.

---

## 8. Confidence (optional)

**Confidence** represents the estimated certainty of an extraction, inference, or other Derivation.

Confidence is independent from both Derivation and Verification.

An Inferred Unit does not necessarily have low confidence, and a Direct Unit is not necessarily correct.

Example:

```json
{
  "confidence": "medium"
}
```

Possible implementations may use:

- categorical values
- numeric scores
- model-specific confidence
- human-assigned confidence

CRA does not prescribe a universal confidence scale.

Where Confidence is used, the method by which it was produced should ideally remain identifiable.

---

## 9. Gap

A **Gap** represents information that is considered missing, ambiguous, uncertain, unsupported, or otherwise insufficient for the current acquisition objective.

Examples:

- missing reason
- missing context
- missing interpretation
- missing decision criterion
- ambiguity
- unsupported inference
- conflicting information

Example:

```json
{
  "id": "gap_003",
  "type": "missing_decision_criterion",
  "target": "decision_criterion",
  "detected_at": "initial"
}
```

A Gap belongs to the acquisition process.

It is not itself a Reasoning Unit.

---

## 10. Elicitation History

**Elicitation History** records how the acquisition process changed over time.

This is particularly important in adaptive acquisition because different Events may receive different questions.

The associated preprint refers to this question-driven acquisition process as *Adaptive Micro-Elicitation*; this repository uses the shorter term *Adaptive Elicitation* for the same process.

An Elicitation History may preserve:

- detected Gap
- question
- target information
- response / non-response
- resolved Gap
- new Gap
- remaining Gap
- stopping reason

Example:

```json
{
  "id": "elicitation_001",
  "triggered_by_gap": "gap_001",
  "question": "Why did you decide not to raise the price increase this time?",
  "resolved_gaps": [
    "gap_001",
    "gap_002"
  ],
  "new_gaps_detected": [
    "gap_004"
  ]
}
```

A single answer may resolve multiple Gaps.

A question may also reveal a new Gap that was not identifiable before the response.

Question wording should be preserved because different phrasings of the same Gap may produce different responses and therefore become relevant when interpreting the acquired data.

---

## 11. Missingness and Gap State

Missingness should be interpreted through both Source availability and Elicitation History rather than simply through the absence of a Reasoning Unit.

CRA distinguishes at least two related dimensions.

### Source state

- `not_observed`
- `observed_but_insufficient`

`not_observed` — The target information was not present in the available Sources at the relevant point in the acquisition process.

`observed_but_insufficient` — Related information exists in the available Sources, but it is insufficient for the current acquisition objective because it is, for example:

- ambiguous
- incomplete
- conflicting
- unsupported
- too general

### Elicitation state

- `not_elicited`
- `elicited_and_resolved`
- `elicited_but_unresolved`

`not_elicited` — No follow-up was attempted for the Gap.

`elicited_and_resolved` — The Gap was resolved by a response, either through a question directly targeting that Gap or incidentally through a response targeting another Gap.

`elicited_but_unresolved` — Follow-up was attempted, but the Subject could not answer, did not answer, or the response did not resolve the Gap.

A Gap may be both:

```text
not_observed
+
not_elicited
```

These dimensions describe different stages of acquisition.

For example, a decision criterion may initially be `not_observed` because no existing Source contains it, and later become either:

- `elicited_and_resolved`
- `not_elicited`
- `elicited_but_unresolved`

depending on what happens during Adaptive Elicitation.

### Explicit denial is not Missingness

If the Subject explicitly states that the relevant reasoning did not exist, the statement should be retained as a Source-based observation rather than treated as missing information.

For example:

> "I didn't have a specific rule."

is itself acquired information.

It is different from:

> the system never asked whether a rule existed

or:

> the Subject was asked but could not answer

### A Unit may exist even when the corresponding Gap was not elicited

For example:

```text
Source state:
not_observed

Elicitation state:
not_elicited

Reasoning Unit:
decision rule exists

Derivation:
inferred

Verification:
unconfirmed
```

This means:

> the system inferred a possible decision rule from other available Sources, but the Subject was never directly asked to provide or confirm that criterion.

Therefore:

```text
Gap state
≠
Reasoning Unit existence
```

---

## 12. Stopping

Adaptive acquisition requires an explicit stopping condition.

Possible reasons include:

- `sufficient_information_acquired`
- `max_elicitation_steps_reached`
- `low_expected_information_gain`
- `subject_unable_to_continue`
- `cost_threshold_reached`
- `event_importance_threshold`

Example:

```json
{
  "stopping": {
    "reason": "max_elicitation_steps_reached",
    "max_elicitation_steps": 2,
    "remaining_not_elicited_gaps": [
      "gap_003"
    ]
  }
}
```

Stopping information is part of acquisition provenance.

Without it, an analyst may incorrectly interpret unelicited information as absent reasoning.

---

## 13. Acquisition Layer vs. Representation Layer

CRA separates two conceptual layers.

### Acquisition Layer

Preserves:

- Sources
- Gaps
- Questions
- Responses
- Grounding
- Elicitation History
- Derivation provenance
- Verification

Its purpose is to retain what was actually acquired and how it was obtained.

### Representation Layer

Maps acquired information into a structure suitable for analysis or application use.

Examples might include:

- observation
- interpretation
- decision criterion
- reason
- action
- outcome

or a completely different domain-specific schema.

This separation prevents the dataset from being permanently bound to the representation used when it was originally acquired.

Conceptually:

```text
Real-world Event
      ↓
Acquisition Layer
      ↓
Sources + Elicitation History
      ↓
Reasoning Units
      ↓
Representation Layer
      ↓
Application-specific representation
```

---

## 14. Relationships

A Reasoning Trace may contain semantic relationships between Reasoning Units.

Examples include:

- `supports`
- `leads_to`
- `tests`
- `contradicts`
- `revises`

Example:

```json
{
  "from": "unit_002",
  "type": "supports",
  "to": "unit_003"
}
```

Applications may define additional relation types where necessary.

CRA does not require these relationships to form a fixed ontology.

---

## 15. Extensibility

The conceptual data model intentionally leaves several dimensions open.

Implementations may define:

- domain-specific Event schemas
- Reasoning Unit taxonomies
- Gap taxonomies
- Derivation taxonomies
- Verification methods
- Confidence scales
- Reasoning relationships
- Representation schemas
- storage architecture

The core requirement is not that all systems use identical labels.

The requirement is that important distinctions remain recoverable.

In particular:

- Source
- Grounding
- Derivation
- Verification
- Elicitation History
- Subject
- Event
- Time

should not be irreversibly collapsed into a single generated output.

---

## 16. Storage Model

CRA does not prescribe a storage technology.

Possible implementations include:

- relational databases
- document databases
- graph databases
- event stores
- data warehouses
- hybrid architectures

For example, an implementation may store:

```text
Events and Subjects → relational tables
Sources → object/document storage
Reasoning Units → relational or graph structure
Elicitation History → append-only event records
```

The examples in this repository use JSON for readability only.

JSON is not a requirement of CRA.

---

## 17. What this specification does not define

This specification intentionally does not define:

- production Gap Detection logic
- production prompts
- question-generation algorithms
- optimal stopping logic
- scoring thresholds
- application-specific Reasoning schemas
- model selection
- model orchestration
- UI behavior
- internal Lessonary architecture

These belong to implementation-specific systems rather than the general CRA data model.

---

## 18. Current Specification Status

This document describes a conceptual specification derived from the Continuous Reasoning Acquisition methodological proposal.

It should currently be treated as:

> an implementation-facing conceptual data model, not a finalized interoperability standard.

Future versions may formalize:

- required vs. optional fields
- controlled vocabularies
- JSON Schema definitions
- identifier rules
- versioning rules
- cross-record references
- serialization conventions

without changing the conceptual distinctions described here.

---

## Related Resources

- [README](../README.md)
- [Complete Reasoning Trace Example](../examples/complete-reasoning-trace.json)
- [JSON Schema](../schema/reasoning-trace.schema.json)
- Preprint: [10.5281/zenodo.23215881](https://doi.org/10.5281/zenodo.23215881)
