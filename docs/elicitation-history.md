# Continuous Reasoning Acquisition — Elicitation History

This document describes the **Elicitation History** model used by Continuous Reasoning Acquisition (CRA).

Elicitation History records how reasoning-related information was acquired over time.

It is especially important when acquisition is adaptive, because different Events may receive different questions, and the absence of a Reasoning Unit does not necessarily mean that the underlying reasoning did not exist.

For the broader conceptual data model, see:

[`/docs/data-model.md`](./data-model.md)

For a complete illustrative record, see:

[`/examples/complete-reasoning-trace.json`](../examples/complete-reasoning-trace.json)

---

## 1. Why Elicitation History is needed

In a fixed questionnaire, every Subject is usually asked the same predefined set of questions.

In CRA, acquisition is different.

The system may:

```text
inspect existing Sources
        ↓
detect missing reasoning information
        ↓
ask a targeted question
        ↓
receive a response
        ↓
update the information state
        ↓
detect another Gap
        ↓
ask again or stop
```

As a result, two Events may end with different Reasoning Units for very different reasons.

For example, a decision criterion may be absent, or present only as a system inference, because:

- it was not present in existing Sources
- related information existed but was ambiguous or insufficient
- it was never selected for follow-up
- the Subject was asked but could not answer
- the Subject explicitly stated that no such criterion existed
- the system inferred a possible criterion without asking the Subject
- the information was acquired but omitted by the final Representation

These states should not be collapsed into the same `null` value.

Elicitation History preserves the acquisition process needed to distinguish them.

---

## 2. Core concept

An Elicitation History records the sequence:

```text
Information State
      ↓
Gap Detection
      ↓
Elicitation Step
      ↓
Response / Non-response
      ↓
Updated Information State
      ↓
Gap Resolution / New Gap Detection
      ↓
Stopping
```

Conceptually:

```text
Event
 └── Elicitation History
       ├── Gap(s)
       ├── Elicitation Step(s)
       ├── Source(s) created from responses
       ├── Gap State transitions
       └── Stopping
```

The purpose is not merely to store a conversation transcript.

The purpose is to preserve:

> why a question was asked, what information it targeted, what changed after the response, and why acquisition stopped.

---

## 3. Gap lifecycle

A **Gap** represents information that is missing, ambiguous, uncertain, unsupported, conflicting, or otherwise insufficient for the current acquisition objective.

Example:

```json
{
  "id": "gap_003",
  "type": "missing_decision_criterion",
  "target": "decision_criterion",
  "description": "The decision criterion was not available in the current Sources.",
  "detected_at": "initial"
}
```

A Gap may be detected:

- during Initial Extraction
- after an elicitation response
- after a new Source is added
- after conflicting information is detected
- after a previous inference is challenged

The Gap itself should remain identifiable across later state transitions.

---

## 4. Source state and Elicitation state

CRA distinguishes between:

1. the state of the information in available Sources, and
2. what happened during follow-up acquisition.

These are separate dimensions.

### Source state

- `not_observed`
- `observed_but_insufficient`

#### `not_observed`

The target information is not present in the available Sources.

#### `observed_but_insufficient`

Related information exists in the available Sources, but it is insufficient for the current acquisition objective because it is, for example:

- ambiguous
- incomplete
- conflicting
- unsupported
- too general

### Elicitation state

- `not_elicited`
- `elicited_and_resolved`
- `elicited_but_unresolved`

#### `not_elicited`

No follow-up was attempted for the Gap.

#### `elicited_and_resolved`

Follow-up acquisition produced information sufficient to resolve the Gap.

The Gap may be resolved either:

- **directly**, by a question targeting that Gap, or
- **incidentally**, by a response to another question.

#### `elicited_but_unresolved`

Follow-up was attempted, but the Gap remained unresolved.

Possible reasons include:

- Subject could not answer
- Subject did not answer
- response was too ambiguous
- response introduced conflicting information
- response did not address the target

A Gap may therefore be both:

```text
source_state: not_observed
elicitation_state: not_elicited
```

These describe different stages of acquisition.

---

## 5. One response can resolve multiple Gaps

A response should not be assumed to resolve only the Gap that triggered the question.

For example:

```text
Gap 1:
Why was the action postponed?

Gap 2:
What situation influenced the decision?
```

The system asks:

> "Why did you decide not to raise the price increase this time?"

The Subject answers:

> "The person in charge seemed to be under pressure from their manager, and the atmosphere was tense."

This response may provide both:

```text
reason-related information
+
situation-recognition information
```

The Elicitation Step can therefore record:

```json
{
  "id": "elicitation_001",
  "triggered_by_gap": "gap_001",
  "resolved_gaps": [
    "gap_001",
    "gap_002"
  ]
}
```

This makes incidental Gap resolution explicit.

---

## 6. A response can create a new Gap

An answer may also expose information that requires further clarification.

For example:

```text
Response:
"The atmosphere was tense."
```

may resolve a missing-context Gap while creating a new question:

> How did the Subject interpret that tension?

This can be represented as:

```json
{
  "id": "elicitation_001",
  "resolved_gaps": [
    "gap_001",
    "gap_002"
  ],
  "new_gaps_detected": [
    "gap_004"
  ]
}
```

The newly detected Gap should be defined separately:

```json
{
  "id": "gap_004",
  "type": "missing_interpretation",
  "target": "interpretation_of_situation",
  "description": "The Subject's interpretation of the observed situation was not yet explicit.",
  "detected_at": "elicitation_001"
}
```

This allows the history to represent an adaptive chain rather than a predefined questionnaire.

---

## 7. Elicitation Step

An **Elicitation Step** records one attempt to acquire additional information.

A typical step may include:

- step identifier
- sequence number
- triggering Gap
- target information
- exact question wording
- response Source
- result
- resolved Gaps
- newly detected Gaps
- timestamp

Example:

```json
{
  "id": "elicitation_002",
  "sequence": 2,
  "triggered_by_gap": "gap_004",
  "target_information": "interpretation_of_situation",
  "question": "What made you think this was not a good timing to raise the price increase?",
  "response_source": "source_003",
  "result": "answered",
  "resolved_gaps": [
    "gap_004"
  ],
  "new_gaps_detected": []
}
```

---

## 8. Preserve exact question wording

The exact wording of the question should be preserved where practical.

Two questions may target the same Gap but produce different responses.

For example:

> "Why did you do that?"

and:

> "What did you observe that made you choose that action?"

may both target reasoning related to the same Event, but they can elicit different types and levels of detail.

Question wording is therefore part of acquisition provenance.

The Elicitation History should preserve the actual question presented to the Subject rather than only storing a normalized target label.

---

## 9. Responses become Sources

A response obtained during elicitation should be represented as a Source.

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

This establishes a traceable relationship:

```text
Gap
 ↓
Elicitation Step
 ↓
Question
 ↓
Response
 ↓
Source
 ↓
Reasoning Unit
```

The response itself is the Source.

Any later extraction, normalization, inference, or synthesis from that response is represented through Derivation.

---

## 10. Non-response and unresolved acquisition

Not every elicitation attempt resolves a Gap.

A Subject may:

- skip the question
- say they do not remember
- say they are unsure
- provide an unrelated answer
- provide insufficient information

When the Subject provides an actual response, even if the response does not resolve the Gap, that response should normally be preserved as a Source.

For example:

```json
{
  "id": "source_004",
  "type": "elicitation_response",
  "origin": "subject",
  "elicitation_id": "elicitation_003",
  "content": "I don't remember what criterion I used."
}
```

The Elicitation Step may then record:

```json
{
  "id": "elicitation_003",
  "triggered_by_gap": "gap_005",
  "question": "What criterion did you use to choose that option?",
  "response_source": "source_004",
  "result": "answered_but_unresolved",
  "resolved_gaps": [],
  "new_gaps_detected": []
}
```

The corresponding Gap state becomes:

```json
{
  "gap_id": "gap_005",
  "source_state": "not_observed",
  "elicitation_state": "elicited_but_unresolved",
  "elicitation_id": "elicitation_003"
}
```

By contrast, `response_source: null` should generally be reserved for cases where no response Source was created, such as a skipped or unanswered question.

This is different from `not_elicited`, because acquisition was attempted.

---

## 11. Explicit denial is information

If the Subject explicitly states that the relevant reasoning did not exist, this should not automatically be treated as Missingness.

For example:

> "I didn't have a specific rule."

or:

> "I wasn't consciously comparing alternatives."

is itself acquired information.

The response should be stored as a Source.

In this case, the relevant Gap is generally considered:

```text
elicitation_state: elicited_and_resolved
```

because the question was answered and the uncertainty about whether such reasoning was present has been resolved.

The resolved content is:

> absence of the relevant reasoning

rather than a missing response.

Depending on the application, a Reasoning Unit may represent:

- absence of an explicit criterion
- lack of conscious deliberation
- no recalled rationale

The important distinction is:

```text
Subject explicitly stated that no such reasoning existed
≠
system never asked
≠
Subject could not answer
```

---

## 12. Inference without elicitation

CRA allows a system to infer a Reasoning Unit even when the corresponding Gap was never directly elicited.

Example:

```text
Gap:
decision criterion

Source state:
not_observed

Elicitation state:
not_elicited

System:
infers a possible decision rule from other Sources
```

This may produce:

```json
{
  "id": "unit_004",
  "type": "decision_rule",
  "related_gap_ids": [
    "gap_003"
  ],
  "derivation": {
    "type": "inferred"
  },
  "verification": {
    "status": "unconfirmed"
  }
}
```

This does **not** mean that the Gap was resolved through elicitation.

The dataset should retain both facts:

```text
the Unit exists
+
the Subject was never asked
```

Therefore:

```text
Gap state
≠
Reasoning Unit existence
```

---

## 13. Verification is separate from Elicitation

A Subject response can be a Source without constituting Verification of a later Reasoning Unit.

For example:

```text
Subject response
      ↓
Source
      ↓
system extracts interpretation
      ↓
Reasoning Unit
```

The Reasoning Unit may initially be:

- Derivation: `extracted`
- Verification: `unconfirmed`

If the Subject later reviews and confirms the generated Unit:

- Verification: `confirmed`

This is a separate event from the original elicitation.

Therefore:

```text
Subject provided Source
≠
Subject verified generated Reasoning Unit
```

---

## 14. Gap state transitions

A simplified Gap lifecycle may look like:

```text
Gap detected
    ↓
Source state
(not_observed / observed_but_insufficient)
    ↓
┌─────────────────────────────┐
│                             │
▼                             ▼
not_elicited             elicitation attempted
                              │
                     ┌────────┴────────┐
                     ▼                 ▼
             elicited_and_      elicited_but_
                resolved          unresolved
```

However, implementations should not assume every Gap follows exactly one path.

For example:

```text
Gap detected
→ source_state: not_observed
→ elicitation_state: not_elicited
→ Reasoning Unit inferred by system
→ later Subject review
→ Unit confirmed
```

The Gap history and Unit history remain distinct.

---

## 15. Stopping

Adaptive acquisition requires a stopping decision.

Possible stopping reasons include:

- sufficient information acquired
- maximum elicitation steps reached
- expected information gain is low
- Subject unable to continue
- cost threshold reached
- Event importance does not justify further acquisition

Example:

```json
{
  "stopping": {
    "reason": "max_elicitation_steps_reached",
    "max_elicitation_steps": 2,
    "completed_elicitation_steps": 2,
    "remaining_not_elicited_gaps": [
      "gap_003"
    ]
  }
}
```

Stopping is part of Elicitation History because it explains why known Gaps may remain unresolved or unelicited.

Without a stopping record, an analyst may incorrectly interpret remaining Gaps as system failures or as evidence that the underlying reasoning did not exist.

---

## 16. Example complete Elicitation History

A simplified complete example:

```json
{
  "elicitation_history": {
    "gaps": [
      {
        "id": "gap_001",
        "type": "missing_reason",
        "target": "reason_for_action",
        "detected_at": "initial"
      },
      {
        "id": "gap_002",
        "type": "missing_context",
        "target": "situation_recognition",
        "detected_at": "initial"
      },
      {
        "id": "gap_003",
        "type": "missing_decision_criterion",
        "target": "decision_criterion",
        "detected_at": "initial"
      },
      {
        "id": "gap_004",
        "type": "missing_interpretation",
        "target": "interpretation_of_situation",
        "detected_at": "elicitation_001"
      }
    ],

    "elicitation_steps": [
      {
        "id": "elicitation_001",
        "sequence": 1,
        "triggered_by_gap": "gap_001",
        "question": "Why did you decide not to raise the price increase this time?",
        "response_source": "source_002",
        "result": "answered",
        "resolved_gaps": [
          "gap_001",
          "gap_002"
        ],
        "new_gaps_detected": [
          "gap_004"
        ]
      },
      {
        "id": "elicitation_002",
        "sequence": 2,
        "triggered_by_gap": "gap_004",
        "question": "What made you think this was not a good timing to raise the price increase?",
        "response_source": "source_003",
        "result": "answered",
        "resolved_gaps": [
          "gap_004"
        ],
        "new_gaps_detected": []
      }
    ],

    "final_gap_states": [
      {
        "gap_id": "gap_001",
        "source_state": "not_observed",
        "elicitation_state": "elicited_and_resolved",
        "resolved_by": "elicitation_001"
      },
      {
        "gap_id": "gap_002",
        "source_state": "not_observed",
        "elicitation_state": "elicited_and_resolved",
        "resolved_by": "elicitation_001",
        "note": "Resolved incidentally by a response targeting another Gap."
      },
      {
        "gap_id": "gap_003",
        "source_state": "not_observed",
        "elicitation_state": "not_elicited"
      },
      {
        "gap_id": "gap_004",
        "source_state": "observed_but_insufficient",
        "elicitation_state": "elicited_and_resolved",
        "resolved_by": "elicitation_002"
      }
    ],

    "stopping": {
      "reason": "max_elicitation_steps_reached",
      "max_elicitation_steps": 2,
      "completed_elicitation_steps": 2,
      "remaining_not_elicited_gaps": [
        "gap_003"
      ]
    }
  }
}
```

In this example, `gap_004` is `observed_but_insufficient` because `source_002` contains information about the tense situation, but does not yet contain the Subject's explicit interpretation of that situation.

---

## 17. Recommended implementation properties

An implementation should ideally make it possible to reconstruct:

- which Sources were available before each question
- which Gap triggered the question
- the exact question shown
- the response or non-response
- which Source was created from the response
- which Gaps were resolved
- which Gaps remained
- which new Gaps appeared
- why acquisition stopped

This does not require a particular database architecture.

Possible implementations include:

- append-only event log
- relational tables
- document records
- graph structures
- hybrid storage

The important requirement is that the acquisition path remains recoverable.

---

## 18. What Elicitation History is not

Elicitation History is not:

- a transcript alone
- a chat log alone
- a list of questions alone
- a Reasoning Trace
- a model execution trace

A conversation log records:

> what was said.

An LLM trace records:

> what the AI system executed.

A Reasoning Trace records:

> what reasoning-related information was represented.

Elicitation History records:

> why additional information was requested, what changed as a result, and why acquisition stopped.

These records may reference each other, but they represent different layers.

---

## 19. Design boundary

This specification defines **what acquisition provenance should remain distinguishable**.

It does not define:

- how Gaps are detected
- how questions are generated
- how question quality is scored
- how stopping thresholds are calculated
- how many elicitation steps are optimal
- which LLM or model should be used

Those decisions belong to implementation-specific systems.

---

## 20. Current Specification Status

This document describes an implementation-facing conceptual model for Elicitation History.

It is not currently intended as a finalized interoperability standard.

Future versions may formalize:

- Gap lifecycle enums
- Source state enums
- Elicitation state enums
- Elicitation result enums
- timestamp requirements
- question / response identifiers
- cross-record references
- versioning rules
- event-sourcing conventions

while preserving the conceptual distinctions defined here.

---

## Related Resources

- [README](../README.md)
- [Complete Reasoning Trace Example](../examples/complete-reasoning-trace.json)
- [Data Model](./data-model.md)
- [Derivation, Verification, and Confidence](./derivation-and-verification.md)
- [JSON Schema](../schema/reasoning-trace.schema.json)
- Preprint: [10.5281/zenodo.23215881](https://doi.org/10.5281/zenodo.23215881)
