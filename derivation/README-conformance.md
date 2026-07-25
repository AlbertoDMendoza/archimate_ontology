# Derivation conformance (branch: `derivation-pie-conformance`)

Integration branch combining the two independent efforts that each stalled on their own:

- **`derivation-redo`** contributed the **case-significant Appendix B tables**
  (`relationships.xml`, 3,720 cased entries) where `UPPERCASE = direct` and `lowercase = derived`.
  That distinction is the ground truth everything here depends on.
- The **rule-engine effort** contributed the idea of running ArchiMate derivation as engine-native
  forward-chaining rules, which stalled because the specification's *restriction* rules have the
  shape "R holds **unless** X is absent" and forward chaining has no negation.

Combining them dissolves that blocker: the tables state **positively** which
`(sourceType, targetType, relation)` triples are permitted, so requiring that permission as an extra
positive premise achieves what negation would, inside forward chaining.

## What's here

| path | purpose |
|---|---|
| `relationships.xml` | the cased Appendix B tables (from `derivation-redo`) |
| `../tools/relationships2axioms.py` | generator — the step that never existed before |
| `archimate_derivation_axioms.ttl` | **regenerated**: strength ordering, relationship categories, permission lookup, permitted matrix, and per-pair detail that now **preserves the direct/derived split** |
| `conformance/fixture-direct.ttl` | the direct relationships as type-level instance data — input to a conformance run |
| `conformance/fixture-derived.ttl` | the derived relationships — what a correct ruleset must reproduce |

## Why the axioms file was regenerated rather than edited

The previous version had two faults that made it inert:

1. It declared `@prefix archi: <https://purl.org/archimate/owl#>` — the ontology **document** IRI —
   while every term and model predicate lives at `<https://purl.org/archimate#>`. Nothing it asserted
   could bind to a real relationship.
2. It was transcribed from the **all-lowercase** table, discarding direct-vs-derived. That is still
   usable as a permitted-set guard but useless as a conformance oracle.

## How to use it as a conformance oracle

Load `archimate_derivation_axioms.ttl` plus `conformance/fixture-direct.ttl` into a reasoning store,
run the derivation rules, then diff the inferred relationships against
`conformance/fixture-derived.ttl`:

- inferred **and** in `fixture-derived` → rule confirmed against the specification
- in `fixture-derived`, **not** inferred → a missing or incorrect derivation rule
- inferred, **permitted nowhere** → a restriction case

## Note on the engine

The GraphDB `.pie` ruleset that consumes these axioms is deliberately **not** in this repository: it
is engine-specific, and this repository stays standards-based (Turtle + a vendor-neutral generator).
The portable rules are the source of truth; an engine ruleset is a compilation target.
