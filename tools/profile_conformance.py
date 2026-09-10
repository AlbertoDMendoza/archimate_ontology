#!/usr/bin/env python3
"""Profile-pattern conformance oracle.

Runs the fixtures in validation/conformance/ and diffs the outcomes against
their expected-output files (see validation/conformance/README.md):

  1. Rule oracle       — fix:BetaKindRule must materialize exactly the triples
                         in fixture-profile-materialized.ttl.
  2. Instance oracle   — validating the fixture data against the fixture
                         shapes must report exactly the violations in
                         fixture-profile-expected.ttl, matched on
                         (focusNode, resultPath, sourceConstraintComponent).
  3. Meta oracle       — validating fixture-pattern-bad.ttl against the
                         profile-pattern meta-shapes must report exactly the
                         violations in fixture-pattern-expected.ttl, matched
                         on (focusNode, sourceShape).
  4. Examples check    — the shipped example profiles must conform to the
                         meta-shapes.

Exit status 0 when every oracle passes, 1 otherwise.
Requires: rdflib, pyshacl (pip install pyshacl).
"""

import sys
from pathlib import Path

import rdflib
from rdflib.namespace import RDF, SH
from pyshacl import validate

ROOT = Path(__file__).resolve().parent.parent
CONF = ROOT / "validation" / "conformance"

FAILURES = []


def check(name: str, expected: set, actual: set) -> None:
    missing = expected - actual
    extra = actual - expected
    if not missing and not extra:
        print(f"PASS  {name}")
        return
    print(f"FAIL  {name}")
    for row in sorted(missing, key=str):
        print(f"      missing: {row}")
    for row in sorted(extra, key=str):
        print(f"      extra:   {row}")
    FAILURES.append(name)


def load(*paths: Path) -> rdflib.Graph:
    g = rdflib.Graph()
    for p in paths:
        g.parse(p, format="turtle")
    return g


def run_rules(data: rdflib.Graph) -> rdflib.Graph:
    """Execute every standalone sh:SPARQLRule in the graph (the repository's
    execution model — rules are self-selecting CONSTRUCTs, not attached to
    node shapes) and add the derived triples. Returns only the derived
    triples."""
    prefix_lines = []
    for decl in data.objects(None, SH.declare):
        prefix = data.value(decl, SH.prefix)
        namespace = data.value(decl, SH.namespace)
        prefix_lines.append(f"PREFIX {prefix}: <{namespace}>")
    header = "\n".join(prefix_lines)
    derived = rdflib.Graph()
    for rule in data.subjects(RDF.type, SH.SPARQLRule):
        query = str(data.value(rule, SH.construct))
        for triple in data.query(f"{header}\n{query}"):
            derived.add(triple)
    for triple in derived:
        data.add(triple)
    return derived


def violations(data: rdflib.Graph, shapes: rdflib.Graph) -> rdflib.Graph:
    _, report, _ = validate(data, shacl_graph=shapes, inference="none")
    return report


def result_keys(graph: rdflib.Graph, fields) -> set:
    keys = set()
    for result in graph.subjects(RDF.type, SH.ValidationResult):
        keys.add(tuple(graph.value(result, f) for f in fields))
    return keys


def main() -> int:
    # --- 1 & 2: instance-level fixture ---------------------------------
    shapes = load(CONF / "fixture-profile-shapes.ttl")
    data = load(
        CONF / "fixture-profile-shapes.ttl",  # subclass axioms, in data too
        CONF / "fixture-profile-data.ttl",
    )

    derived = run_rules(data)
    expected_triples = set(load(CONF / "fixture-profile-materialized.ttl"))
    check("rule oracle (materialized triples)", expected_triples, set(derived))

    report = violations(data, shapes)
    fields = (SH.focusNode, SH.resultPath, SH.sourceConstraintComponent)
    expected = result_keys(load(CONF / "fixture-profile-expected.ttl"), fields)
    check("instance oracle (fixture violations)", expected, result_keys(report, fields))

    # --- 3: meta-shapes against the malformed TBox ---------------------
    meta = load(ROOT / "validation" / "archimate_validation_profile_pattern.ttl")
    bad = load(CONF / "fixture-pattern-bad.ttl")
    report = violations(bad, meta)
    fields = (SH.focusNode, SH.sourceShape)
    expected = result_keys(load(CONF / "fixture-pattern-expected.ttl"), fields)
    check("meta oracle (malformed definitions)", expected, result_keys(report, fields))

    # --- 4: meta-shapes against the shipped examples -------------------
    examples = load(
        ROOT / "ontology" / "archimate_profile_examples.ttl",
        ROOT / "validation" / "archimate_validation_profile_examples.ttl",
    )
    report = violations(examples, meta)
    check("examples conform to meta-shapes", set(), result_keys(report, fields))

    print()
    if FAILURES:
        print(f"{len(FAILURES)} oracle(s) failed")
        return 1
    print("all conformance oracles passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
