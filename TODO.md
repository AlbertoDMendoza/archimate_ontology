# TODO

Outstanding issues identified during ontology review (2026-02-22).

---

## Medium Priority

### `archimate_derivation_rules.ttl`
- **CrossDomainRestrictions misplaced**: The `CrossDomainRestrictions` shape is a SHACL validation
  constraint (`sh:NodeShape`), not a derivation rule. Move it to `archimate_validation_metamodel.ttl`.

- **Strategy→Core restriction too broad**: The cross-domain rule blocks all relationships from
  Strategy to Core except `association`. Per spec (Section 7.2, Figure 51), serving and other
  relationships from Strategy elements to Core are valid patterns (e.g., Capability serving a
  BusinessProcess). Soften or add explicit exceptions.

- **`structuralStrength`/`dependencyStrength` values never assigned**: The strength properties are
  declared and referenced in `BIND(IF(?strength1 <= ?strength2, ...))` comparisons across DR2–DR8,
  but no actual values are ever asserted on relationship type instances. At runtime the comparisons
  will bind to unbound variables and silently produce wrong results. Assign numeric strength values
  to each relationship property (e.g., `archimate:composition deriv:structuralStrength 1`) or
  rewrite the rules to avoid numeric comparison.

- **PDR rules not validated post-derivation**: Potential derivation rules (PDR1–PDR12) fire and
  assert new relationships without checking whether the derived result satisfies metamodel
  constraints. A derived relationship that violates Layer 2 patterns will silently enter the graph.
  Run `archimate_validation_metamodel.ttl` shapes against the materialized graph after derivation,
  or add `FILTER` guards inside each PDR rule.

### `archimate_validation_core.ttl` — RDF4J / Transactional SHACL
- **RDF4J 4.3.x sets `sh:conforms false` for ANY validation result regardless of severity**:
  Info and Warning results are treated identically to Violation — all block the transaction and
  return HTTP 500. This is intentional GraphDB behavior ("we don't want to ingest invalid data").
  No severity-based filtering is available via configuration.

  *Current strategy*: Only `sh:Violation`-level shapes are loaded into the SHACL shapes graph.
  `DeepSpecializationCheck` (`sh:Info`) is loaded but immediately deactivated via `sh:deactivated true`
  in the shapes graph — it is batch/reporting use only.

  *Note*: No other widely-deployed triplestore implements transactional SHACL, so cross-engine
  severity comparison is not applicable for our write-blocking use case.

### `archimate_validation_relationships.ttl`
- **Plateau composition includes `archimate:Relationship`**: The Plateau composition/aggregation
  shape lists `archimate:Relationship` as a valid target. `archimate:Relationship` is an abstract
  metaclass not meant to be instantiated. Verify against `relationships.xml` source and remove
  if not spec-mandated.

- **Audit period placement around line 101**: Multiple shapes have a period (`.`) at a point where
  a semicolon (`;`) would be expected to continue chaining `sh:property` blocks. Spot-check all
  NodeShape definitions for truncated property chains — a misplaced period silently ends the shape
  early, leaving subsequent constraints unchecked.

- **No inverse composition/aggregation validation**: Nothing prevents element Y from composing
  element X when X already composes Y, except the circular-composition SPARQL in
  `archimate_validation_core.ttl`. Add explicit `sh:not` or SPARQL constraints to disallow
  bidirectional composition/aggregation pairs.

### `archimate_validation_metamodel.ttl`
- **`RealizationDirection` shape has no active constraint**: The shape is declared but contains
  neither `sh:property` nor `sh:sparql`, making it informational only. Either add the intended
  constraint or remove the shape to avoid false confidence during validation runs.

---

## Low Priority

### `archimate_derivation_rules.ttl`
- **`structuralStrength`/`dependencyStrength` domain error**: Both helper properties declare
  `rdfs:domain` using a property IRI (`archimate:structuralRelationship`) rather than a class.
  Technically ill-formed OWL. Remove the `rdfs:domain` declarations or replace with an
  appropriate class (e.g., `owl:ObjectProperty`).

- **`DerivationDepthLimit` won't trigger**: The shape requires 6 distinct `deriv:derivedFrom`
  values on a single statement. Each derivation rule adds at most 2–3 sources, so this
  threshold is unreachable in practice. Rethink the depth detection approach.

- **`ContradictionResolution` misleading name**: Labeled "Cleanup Rules" and described as
  removing contradictory relationships, but the CONSTRUCT only adds a `deriv:contradictionFlag`
  annotation — nothing is removed. Rename or update the description to reflect actual behavior.

### `archimate_validation_profiles.ttl`
- **`email` property uses wrong datatype**: `archimate-prof:email` is declared as `xsd:anyURI`.
  Plain email addresses are not valid IRIs. Change to `xsd:string` with an appropriate
  `sh:pattern` constraint, or document that `mailto:` URI format is required.

### `archimate_skos.ttl`
- **External vocabulary references lack prefix declarations**: Lines 787–792 reference
  `goodrelations:BusinessFunction`, `dcat:DataService`, and `org:Role` via `skos:relatedMatch`,
  but none of those prefixes are declared at the top of the file. Add `@prefix` declarations for
  each or replace with full IRIs to keep the file self-contained.

### `archimate_profile_examples.ttl`
- **Commented-out profile examples should be resolved**: Lines 82–119 contain commented-out
  profile class definitions. Either activate them (add `owl:imports` and uncomment) or remove
  them. Dead code creates confusion about what is intentional.

### `archimate.ttl`
- **`junctionType` OWL range non-standard**: `rdfs:range [ owl:oneOf ( "and" "or" ) ]` uses a
  blank node with string literals, which is not standard OWL DL. The constraint is already
  enforced by `sh:in` in `JunctionTypeValidation`. Remove the `rdfs:range` restriction and
  rely solely on SHACL.

- **Label casing inconsistency (line 149)**: `"Architecture View"` and `"Architecture Viewpoint"`
  follow Title Case correctly, but verify all `rdfs:label` values in the file use consistent
  Title Case rather than mixing with sentence case.

---

## Informational

### `archimate_derivation_rules.ttl`
- **`ComplexChainDerivation` is redundant**: A structural→structural→dependency chain is already
  derivable by chaining DR2 then DR3. The rule produces correct results but fires redundantly
  before the `FILTER NOT EXISTS` guard eliminates duplicates.

### `archimate_validation_metamodel.ttl`
- **No Level 2 behavioral constraints for `ImplementationEvent`**: `ImplementationEvent` has
  similar restrictions to other event elements (no triggering/flow into Motivation, etc.) but
  these are not explicitly modeled at Level 2. Level 3 covers composition/aggregation only.

---

## Pending Features

- **Viewpoints**: Add common ArchiMate viewpoint definitions (Organization, Application Usage,
  Business Process Cooperation, etc.) and define allowed elements/relationships per viewpoint.

- **Examples**: Create example models demonstrating element instantiation, RDF-Star
  relationships, profiles, and derivations.

- **Profiles**: Add domain-specific example profiles beyond the current Person/Organization stubs.

- **SKOS full framework**: Extend `archimate_skos.ttl` to include the full framework structure
  (currently definitions only).
