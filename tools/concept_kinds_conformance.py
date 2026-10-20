#!/usr/bin/env python3
"""Concept-kinds conformance oracle.

Runs validation/conformance/fixture-concept-kinds-data.ttl and diffs the
outcomes against fixture-concept-kinds-expected.ttl (see
validation/conformance/README.md):

  1. Entailment oracle — after RDFS entailment over the ontology plus the
                         fixture, the nodes typed both as an Element and as a
                         Relationship or RelationshipConnector must be exactly
                         the expected focus nodes. A junction or a
                         relationship that takes part in a relationship must
                         not become an element.
  2. Validation oracle — validating the entailed graph against the Level 1
                         core shapes must report exactly the expected
                         violations, matched on (focusNode, sourceShape).

Exit status 0 when every oracle passes, 1 otherwise.
Requires: rdflib, pyshacl (pip install pyshacl).
"""

import sys
from pathlib import Path

import rdflib
from rdflib.namespace import RDF, RDFS, SH
from pyshacl import validate

ROOT = Path(__file__).resolve().parent.parent
CONF = ROOT / "validation" / "conformance"
ARCHIMATE = rdflib.Namespace("https://purl.org/archimate#")

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


def load_dataset(*paths: Path) -> rdflib.Dataset:
    """The data graph as a dataset: some core shapes query with GRAPH, which
    needs one. Everything goes into the default graph."""
    ds = rdflib.Dataset(default_union=True)
    for p in paths:
        ds.default_context.parse(p, format="turtle")
    return ds


def rdfs_entail(g: rdflib.Graph) -> None:
    """Add the RDFS entailments that matter here, in place, to a fixpoint:
    rdfs5/rdfs11 (transitive subPropertyOf/subClassOf), rdfs7 (subproperty),
    rdfs2 (domain), rdfs3 (range), rdfs9 (subclass)."""
    while True:
        before = len(g)
        for a, b in list(g.subject_objects(RDFS.subPropertyOf)):
            for c in list(g.objects(b, RDFS.subPropertyOf)):
                g.add((a, RDFS.subPropertyOf, c))
        for a, b in list(g.subject_objects(RDFS.subClassOf)):
            for c in list(g.objects(b, RDFS.subClassOf)):
                g.add((a, RDFS.subClassOf, c))
        for p, q in list(g.subject_objects(RDFS.subPropertyOf)):
            for s, o in list(g.subject_objects(p)):
                g.add((s, q, o))
        for p, c in list(g.subject_objects(RDFS.domain)):
            for s, _ in list(g.subject_objects(p)):
                g.add((s, RDF.type, c))
        for p, c in list(g.subject_objects(RDFS.range)):
            for _, o in list(g.subject_objects(p)):
                if not isinstance(o, rdflib.Literal):
                    g.add((o, RDF.type, c))
        for c, d in list(g.subject_objects(RDFS.subClassOf)):
            for s in list(g.subjects(RDF.type, c)):
                g.add((s, RDF.type, d))
        if len(g) == before:
            return


def result_keys(graph: rdflib.Graph, fields) -> set:
    keys = set()
    for result in graph.subjects(RDF.type, SH.ValidationResult):
        keys.add(tuple(graph.value(result, f) for f in fields))
    return keys


def main() -> int:
    data = load_dataset(ROOT / "ontology" / "archimate.ttl", CONF / "fixture-concept-kinds-data.ttl")
    rdfs_entail(data)
    expected_report = load(CONF / "fixture-concept-kinds-expected.ttl")
    fields = (SH.focusNode, SH.sourceShape)
    expected = result_keys(expected_report, fields)

    # --- 1: entailment ------------------------------------------------------
    elements = set(data.subjects(RDF.type, ARCHIMATE.Element))
    non_elements = set(data.subjects(RDF.type, ARCHIMATE.Relationship)) | set(
        data.subjects(RDF.type, ARCHIMATE.RelationshipConnector)
    )
    check(
        "entailment oracle (no relationship or junction becomes an element)",
        {focus for focus, _ in expected},
        elements & non_elements,
    )

    # --- 2: validation ------------------------------------------------------
    shapes = load(ROOT / "validation" / "archimate_validation_core.ttl")
    _, report, _ = validate(data, shacl_graph=shapes, inference="none")
    check("validation oracle (concept kinds disjoint)", expected, result_keys(report, fields))

    if FAILURES:
        print(f"\n{len(FAILURES)} oracle(s) failed")
        return 1
    print("\nall concept-kinds oracles passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
