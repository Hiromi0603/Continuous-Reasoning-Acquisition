# Continuous Reasoning Acquisition

[English](./README.md) | [日本語](./README.ja.md)

**Capture not only what people did, but why they did it — as structured, traceable data.**

Continuous Reasoning Acquisition (CRA) is a reference architecture for adding a **reasoning-data layer** to AI applications, SaaS products, internal tools, and research systems.

It is designed for systems that already have access to events such as:

- user actions
- conversations
- work logs
- CRM records
- support interactions
- operational data
- self-reports

but do not capture the reasoning behind those events.

CRA takes an observed event, extracts what is already known, detects missing reasoning information, optionally asks targeted follow-up questions, and stores the result as a traceable Reasoning Trace.

```text
Event / Log / Conversation
        ↓
Initial Extraction
        ↓
Missing Reasoning Detection (Gap Detection)
        ↓
Targeted Follow-up (Adaptive Elicitation)
        ↓
Structured Reasoning Trace
        ↓
Longitudinal Reasoning Dataset
```

---

## What you can build with it

CRA can be used to add reasoning capture to systems such as:

- CRM / sales enablement tools
- AI coaching systems
- employee reflection tools
- expert knowledge capture systems
- decision-support applications
- customer support platforms
- training and education products
- Human-AI interaction systems
- AI evaluation / training data pipelines

Instead of storing only:

```json
{
  "action": "discount offered",
  "outcome": "deal closed"
}
```

a reasoning-aware system can retain:

```json
{
  "event": "pricing negotiation",
  "observation": "customer repeatedly asked about implementation risk",
  "interpretation": "price was not the primary objection",
  "reason": "reduce perceived implementation risk before discussing price",
  "action": "shared migration plan before offering discount",
  "outcome": "deal closed",
  "sources": ["conversation_102", "followup_18"],
  "derivation": {
    "interpretation": "inferred",
    "reason": "extracted"
  },
  "verification": {
    "interpretation": "unconfirmed",
    "reason": "confirmed"
  }
}
```

Here, **derivation** and **verification** represent independent dimensions.

For example, the interpretation above was inferred by the system and remains unconfirmed, while the reason was extracted from a source and later confirmed by the Subject.

The goal is not simply to generate an explanation with an LLM.

The goal is to create reasoning data whose origin, transformation, and confirmation state remain traceable.

---

## Why not just summarize logs with an LLM?

LLMs can already extract explanations from text.

The harder problem is deciding:

1. what reasoning information is already available,
2. what is still missing,
3. whether missing information should be inferred or asked,
4. what came directly from the Subject versus the system,
5. what was never elicited,
6. how each Reasoning Unit was generated,
7. what has or has not been verified.

These distinctions become increasingly important when reasoning data is accumulated across hundreds or thousands of events.

---

## Provenance and Elicitation History

CRA preserves distinctions between:

```text
what the Subject said
what the system extracted
what the system inferred
what was later confirmed
what was never asked
```

This matters because the absence of a Reasoning Unit does not have a single meaning.

```text
not observed
≠
not elicited
≠
elicitation attempted but unresolved
```

For example, a system may contain no recorded decision criterion because:

- the original event record did not contain one,
- Gap Detection did not select it for follow-up,
- the system asked about it but the Subject could not answer,
- or the information existed but was not represented in the final schema.

Without retaining Elicitation History, these states may become indistinguishable later.

An Elicitation History can therefore retain:

- detected gap
- question presented
- target information
- response / non-response
- updated information state
- remaining gap
- stopping reason

The simplified JSON example above is intended for introduction only.

A complete example including Sources, Grounding, Derivation, Verification, Missingness, and Elicitation History is available in:

[`/examples/complete-reasoning-trace.json`](./examples/complete-reasoning-trace.json)

---

## Why not just ...?

### ...log everything as JSON?

CRA records can be represented as JSON, relational tables, graph structures, or other storage formats.

The key issue is not the serialization format. It is **what the system preserves as data.**

Typical application logs may retain:

- question
- answer
- model output

but not necessarily:

- which reasoning gap triggered the question
- which gaps were intentionally not elicited
- which Source supports each Reasoning Unit
- whether a field was subject-stated, system-extracted, or system-inferred
- whether the resulting Unit was confirmed
- why elicitation stopped

If these distinctions are not captured during acquisition, some of them cannot be reliably reconstructed afterward.

### ...use W3C PROV?

CRA is compatible with general provenance concepts such as those defined by W3C PROV and can be mapped to them.

W3C PROV provides a general framework for representing entities, activities, agents, and derivation relationships.

CRA applies provenance concepts specifically to human reasoning data and defines domain-specific distinctions such as:

- subject-stated vs. system-extracted vs. system-inferred
- confirmed vs. unconfirmed
- not observed vs. not elicited vs. unresolved

The goal is not to replace W3C PROV, but to specify what provenance information matters when the object being captured is human reasoning.

### ...use LLM observability or tracing tools?

LLM observability tools answer questions such as:

- Which model was called?
- Which prompt was sent?
- What response was returned?
- How long did the call take?
- Which tool was invoked?

CRA addresses a different layer:

- What did the person observe?
- What did they interpret?
- What was inferred by the system?
- Which Source supports that inference?
- Was the person ever asked about it?
- Was the resulting Reasoning Unit confirmed?

LLM tracing records what the AI system did.

CRA records how reasoning-related information about the Subject was acquired, derived, and verified.

The two can therefore be complementary rather than alternatives.

---

## Core components

### Gap Detection

Determine what information is still missing for a given event.

Typical gaps include:

- missing reason
- missing context
- missing interpretation
- missing decision criterion
- ambiguity
- unsupported inference
- conflicting information

### Adaptive Elicitation

Generate targeted follow-up questions only when additional information is needed.

```text
Existing data
    ↓
Detect missing reason
    ↓
Ask: "What made you choose A instead of B?"
    ↓
Update event state
    ↓
Stop or detect next gap
```

### Reasoning Trace

Store the reasoning associated with one event as structured data rather than as a single generated summary.

### Provenance

See [Provenance and Elicitation History](#provenance-and-elicitation-history) above.

### Longitudinal identity

Keep Subject + Event + Time relationships so reasoning can later be analyzed across events.

---

## Architecture

A typical implementation can look like:

```text
Application / SaaS / Internal System
                │
                ▼
        Event Capture Layer
                │
                ▼
      Reasoning Acquisition Layer
        ├─ extraction
        ├─ gap detection
        ├─ follow-up generation
        └─ stopping
                │
                ▼
         Reasoning Data Layer
        ├─ Reasoning Units
        ├─ Sources
        ├─ Grounding
        ├─ Derivation
        ├─ Verification
        └─ Elicitation History
                │
                ▼
       Application-specific use
        ├─ coaching
        ├─ analytics
        ├─ knowledge transfer
        ├─ personalization
        └─ AI training/evaluation
```

CRA does not require a specific LLM, database, frontend, or reasoning taxonomy.

---

## Repository scope

This repository focuses on implementation-facing specifications for:

- Reasoning Trace structure
- Reasoning Unit structure
- Source / Grounding
- Derivation
- Verification
- Elicitation History
- Missingness
- example schemas
- sample records
- implementation patterns

It does not publish:

- production prompts
- proprietary Gap Detection logic
- application-specific optimization rules
- internal Lessonary implementation details

---

## Who this is for

This repository may be useful if you are building a system where:

> user behavior is recorded, but the reasoning behind that behavior is lost.

Typical users include:

- AI engineers
- ML engineers
- product engineers
- data architects
- research engineers
- product managers building AI-assisted workflows

---

## Collaboration

I am interested in working with teams that want to integrate reasoning acquisition into an existing product or build a reasoning dataset from real-world events.

Possible collaboration includes:

- architecture design
- product integration
- technical advisory
- PoC design
- reasoning data model design
- adaptive elicitation design
- joint research and empirical validation

If your system already captures what happened, but loses why the decision happened, I can help design and integrate a reasoning acquisition layer around your existing data and workflows.

Contact: research@crossai-labs.com

---

## Research background

The full methodological rationale, related work, limitations, and preliminary observations are described in the associated preprint: [10.5281/zenodo.23215881](https://doi.org/10.5281/zenodo.23215881).

For the theoretical background, see:

- Thought Engineering: A Structural Model of Human Cognition — [10.5281/zenodo.19450037](https://doi.org/10.5281/zenodo.19450037)

---

## Status

This work is currently presented as a methodological proposal with preliminary implementation observations.

The current work does not establish:

- cognitive validity of acquired Reasoning Traces
- superiority over existing elicitation methods
- optimal stopping conditions
- cross-person measurement validity
- effectiveness for downstream applications

These remain subjects for prospective research.

---

## Responsible use

CRA captures information about how people make decisions, which can be more sensitive than ordinary activity logs.

Implementations should define the purpose of acquisition, explain it to Subjects, obtain appropriate consent, and avoid using reasoning data as a fixed measure of individual ability or performance without careful design.

Making the distinction between subject-stated and system-inferred information visible to users is part of responsible use.

---

## Citation

If you use or build upon this work, please cite the corresponding Zenodo preprint.

Citation metadata is available in [`CITATION.cff`](./CITATION.cff).

---

## License

Documentation, specifications, and example records in this repository are released under the [Creative Commons Attribution 4.0 International License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/). See [`LICENSE`](./LICENSE).

The publication of this conceptual method and data model does not imply that all implementation-specific systems, algorithms, prompts, or application code are included in this repository.
