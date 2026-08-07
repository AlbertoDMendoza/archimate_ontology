# Derivation

ArchiMate 3.2 Appendix B derivation as portable RDF: the normative relationship tables, a generator,
and SPARQL rules that consume what it produces. Everything needed to use this is in this repository.

## Files

| path | role |
|---|---|
| `relationships.xml` | the Appendix B tables, **case-significant**: `UPPERCASE` = direct, `lowercase` = derived. Source of truth. |
| `../tools/relationships2axioms.py` | generator; reads the tables, writes everything marked generated below. |
| `archimate_derivation_axioms.ttl` | *generated.* **Load this.** Relationship letters, categories, and the permitted matrix in both forms. |
| `archimate_derivation_strengths.ttl` | the B.2.2 / B.3.3 strength orderings as integers. Load this — the weakest-link rules compare them. |
| `archimate_derivation_provenance.ttl` | terms recording where a derived relationship came from. Load if you want that recorded. |
| `archimate_derivation_rules.ttl` | DR1–DR8 and PDR1–PDR12 as SPARQL CONSTRUCT rules. |
| `conformance/fixture-direct.ttl` | *generated.* The direct relationships as type-level instance data. **Test data — never load into a working repository.** |
| `conformance/fixture-derived.ttl` | *generated.* The derived relationships, same shape. Test data. |

Regenerate with:

```
python3 tools/relationships2axioms.py derivation/relationships.xml derivation/conformance
```

## Load order

1. `ontology/archimate.ttl`
2. `derivation/archimate_derivation_axioms.ttl` — **required.** Supplies the categories and the
   permitted matrix the rules match against.
3. `derivation/archimate_derivation_strengths.ttl` — **required.** Without it the weakest-link
   premises never bind and DR2/PDR7 derive nothing, with no error.
4. `derivation/archimate_derivation_provenance.ttl` — optional; needed only to record provenance.
5. `derivation/archimate_derivation_rules.ttl`
6. your model data

## Permitted, and permitted *directly*

The tables distinguish two things a flat matrix cannot, and both are generated:

| predicate | meaning |
|---|---|
| `archi:permits<Relation>` | permitted, whether directly or by derivation — 10,610 triples |
| `archi:permitsDirect<Relation>` | permitted **directly**: assertable per the metamodel — 5,822 triples |

Every `permitsDirect` triple is also a `permits` triple. A pair that is permitted but *not*
permitted-direct is one Appendix B sanctions only as the conclusion of a derivation, so the two
predicates answer different questions:

```sparql
# May a modeller draw this?
ASK { archi:ApplicationComponent archi:permitsDirectRealization archi:ApplicationProcess }

# May it exist at all, including as a derived relationship?
ASK { archi:ApplicationComponent archi:permitsRealization archi:ApplicationProcess }
```

`archi:permittedBy` maps a relation to the predicate carrying its permissions, so one generic query can
look up permission for whatever relation it is handling.

## Valid and potential derivations

Appendix B separates the two and so do the rules. **DR1–DR8** are valid: the specification permits
asserting what they produce. **PDR1–PDR12** are potential — B.3 says a potential derivation "might be
relevant but may also be wrong… it is up to the modeler to decide". Asserting a PDR result without a
modeller's judgement asserts something the specification does not sanction.

`archimate:confidence` records which a given derived relationship was: `"valid"` or `"potential"`.

## Restrictions as positive premises

Several of the specification's rules read "R holds *unless* X". The cased tables let that be expressed
without negation, because they state **positively** which `(sourceType, relation, targetType)` triples
are permitted — so requiring the permission is enough:

```sparql
?a ?rel ?b .
?a a ?sourceType . ?b a ?targetType .
?rel archi:permittedBy ?p .
?sourceType ?p ?targetType .      # the restriction, as a lookup
```

## Using the fixtures as a conformance oracle

Load `archimate_derivation_axioms.ttl` plus `conformance/fixture-direct.ttl`, run the rules, and diff
the inferred relationships against `conformance/fixture-derived.ttl`:

| outcome | meaning |
|---|---|
| inferred **and** in `fixture-derived` | rule confirmed against the specification |
| in `fixture-derived`, **not** inferred | missing or incorrect rule |
| inferred, **permitted nowhere** | a restriction the rules fail to enforce |

Counts from the current tables: 61 concepts, 10,610 permitted triples, of which 5,822 are direct and
4,788 derived. A private downstream fork with its own consuming application keeps the same derived
half (also 4,788) but a larger direct half — the two only disagree there, and only because of
`Junction` (below).

## Junction is deliberately not in this table

A private downstream fork of this ontology, with its own consuming application, carries 61 `Junction`
rows in its equivalent table, all `ACFGINORSTV` — every relationship type, all direct. This table
carries none, on purpose, not as a sync gap.

`Junction` has no relationship semantics of its own: it merges or splits relationships of *some other
type*, decided per diagram, not per concept pair, so no fixed per-pair case can represent it in a
static permission table. That fork picks `ACFGINORSTV` anyway because its consuming application has to
let people draw a junction with any relationship type — that is a statement about what a modeller may
draw, not about which relationships two *concept types* permit between them, which is the only
question this table exists to answer. A specification rendering is more faithful leaving it out.

This is why `Junction`'s absence here does **not** need "adding back": doing so would answer a
question this table doesn't ask. The real gap it leaves — deriving *through* a junction, e.g. a chain
`A → Junction → B` — needs a rule that treats the junction as transparent and takes the relationship
type from its real neighbours, not a permission row. `<#JunctionTransparency>` in
`archimate_derivation_rules.ttl` is exactly that rule, so this repository derives across a junction on
its own, with nothing engine-specific required. `<#JunctionRelationshipHomogeneity>`
(`validation/archimate_validation_metamodel.ttl`) stays active alongside it: the rule's same-type
requirement is structural (one shared variable spans both hops), so it cannot itself flag a modeller
*asserting* mismatched types through a junction — the shape catches exactly that case, which the rule
cannot.
