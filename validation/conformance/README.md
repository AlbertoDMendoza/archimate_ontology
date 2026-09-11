# Validation Conformance

Fixtures that pin the profile pattern's machine-checkable guarantees. The derivation layer has an
oracle in `derivation/conformance/` (what must be *inferred*); this directory is its validation-side
counterpart (what must *fail*, and what must conform).

Validation has a nastier failure mode than derivation: when shape targeting breaks — subclass axioms
missing from the data graph, implicit class targets going inert on a different engine, a rule harness
change — the result is *fewer violations*, which looks identical to a clean model. The only way to
detect that is a fixture that must fail. Everything here is **test data — never load any of it into a
working repository.**

## Files

| path | role |
|---|---|
| `fixture-profile-shapes.ttl` | **frozen** test TBox + shapes: `fix:Alpha` (profile of BusinessActor, open attribute `alphaCode`) and `fix:Beta` (sub-profile, fixed attribute `betaKind` = `"beta"`). Load into the shapes graph AND the data graph. |
| `fixture-profile-data.ttl` | probe instances + the `betaKind` materialization rule (standalone `sh:SPARQLRule`). Data graph only — rules stay out of the shapes graph. |
| `fixture-profile-materialized.ttl` | oracle: the exact triples the rule must produce. |
| `fixture-profile-expected.ttl` | oracle: the exact violations the SHACL report must contain, matched on (focusNode, resultPath, sourceConstraintComponent). |
| `fixture-pattern-bad.ttl` | deliberately malformed profile *definitions*, one meta-shape violation each. Data graph for a meta-validation run. |
| `fixture-pattern-expected.ttl` | oracle: the exact meta-shape violations, matched on (focusNode, sourceShape). |
| `../../tools/profile_conformance.py` | runner: executes all four oracles below, exit 1 on any mismatch. Requires `pyshacl`. |

The fixture TBox is deliberately independent of the `myModel:` examples — those are documented as
free-to-change samples, and a conformance oracle must not break when documentation evolves. **Do not
edit the fixture files without regenerating the expected files beside them.**

## The four oracles

```
python3 tools/profile_conformance.py
```

1. **Rule oracle** — running `fix:BetaKindRule` must produce exactly the triples in
   `fixture-profile-materialized.ttl`. Guards the rule and the repository's execution model
   (standalone self-selecting SPARQL rules); an extra triple means the rule fires outside its scope
   (`fix:probe-alpha-only` is the scoping probe).
2. **Instance oracle** — after rules, validation must report exactly the violations in
   `fixture-profile-expected.ttl`. Each probe guards one mechanism:

   | probe | must | guards |
   |---|---|---|
   | `fix:probe-conforming` | conform | rule-before-validation ordering (skipped rules surface as an extra `sh:hasValue` violation here) |
   | `fix:probe-deviant` | fail `sh:hasValue` | fixed-value immutability — the instance cannot override the profile-pinned value |
   | `fix:probe-excess` | fail `sh:maxCount` | the cardinality cap — pinned value plus extras is not conformance |
   | `fix:probe-missing-inherited` | fail `sh:minCount` on `alphaCode` (declared on `fix:Alpha`, node typed only `fix:Beta`) | attribute inheritance via subclass targeting — the canary for silent under-validation |
   | `fix:probe-alpha-only` | conform, untouched by the rule | rule scoping |

3. **Meta oracle** — validating `fixture-pattern-bad.ttl` against
   `validation/archimate_validation_profile_pattern.ttl` must report exactly the violations in
   `fixture-pattern-expected.ttl`, one per malformed class (marker/subclass mismatch,
   self-specialization, missing `owl:Class`, nested class not naming its ArchiMate primitive,
   uncapped fixed attribute, fixed value outside its datatype, fixed value contradicting an
   ancestor's, two `archimate:profileOrder` values, an `archimate:profileAspect` pointer at a
   class with no marker).
   Note the last one is reported with the named property shape `avpat:ProfileOrderValue` as
   `sh:sourceShape`, since SHACL core results cite the property shape, not the node shape. `fixbad:FixedParent` is well-formed by
   construction — a violation on it means a meta-shape broadened.
4. **Examples check** — the shipped example profiles (`ontology/archimate_profile_examples.ttl` +
   `validation/archimate_validation_profile_examples.ttl`) must conform to the meta-shapes.

## Reading a failure

| outcome | meaning |
|---|---|
| violation expected **and** reported | mechanism confirmed |
| expected, **not** reported | a shape went inert: subclass axioms missing from the data graph, implicit class targets not firing on this engine, or a constraint narrowed |
| reported, **not** expected | a constraint broadened, the rule harness was skipped, or a rule fired outside its scope |
