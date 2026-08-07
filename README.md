# Archimate Ontology (OWL + SHACL)
An OWL/RDF formalization of the ArchiMate® 3.2 Specification, including executable validation using SHACL.

This repository provides:
* OWL ontology of ArchiMate enterprise architecture language
* SKOS file with ArchiMate vocabulary, published as HTML
* SHACL constraints that enforce the ArchiMate metamodel
* Support for custom profiles and specializations
* Appendix B derivation rules, and the relationship matrix as queryable RDF —
  distinguishing what may be asserted directly from what only a derivation may produce

The goal of this project is to provide a semantically rigorous, standards-faithful representation of ArchiMate suitable for:
* Enterprise architecture modeling on RDF graphs
* Semantic querying and reasoning
* Automated model validation and conformance checking
* Knowledge graph integration with enterprise systems
* Tool-independent architecture repositories
* Advanced impact and dependency analysis
* Architecture governance automation
* Ontology alignment and research
* Controlled language extensions and profiling
* Foundations for enterprise digital twins and AI-assisted architecture

This repository models the language itself, not a specific tool implementation.

### Namespace - Permanent URL
  https://purl.org/archimate#
  
### Last Updated Date
  2026-08-07
  
### Author
  Alberto D. Mendoza  
  https://albertodmendoza.net

## Repo Structure
<pre>
ontology/
├── archimate.ttl                        # Main ontology file (purl.org/archimate/owl)
├── archimate_skos.ttl                   # Vocabulary (purl.org/archimate/skos)
├── archimate_skos.html                  # Human-readable vocabulary docs
├── archimate_profile.ttl                # archimate:profileSpecialization (class-level profile marker)
└── archimate_profile_examples.ttl       # Profile examples

validation/
├── archimate_validation_core.ttl              # Level 1: graph integrity, concept requirements
├── archimate_validation_metamodel.ttl         # Level 2: metamodel pattern rules
├── archimate_validation_relationships.ttl     # Level 3: relationship matrix for all layers (Appendix B)
└── archimate_validation_profile_examples.ttl  # Profile-specific SHACL shapes (example)

derivation/                              # see derivation/README.md
├── relationships.xml                    # Appendix B Relationships matrix, CASE-SIGNIFICANT: UPPERCASE = direct, lowercase = derived. Source of truth.
├── archimate_derivation_axioms.ttl      # generated: categories + permits / permitsDirect matrices
├── archimate_derivation_strengths.ttl   # relationship strength orderings
├── archimate_derivation_provenance.ttl  # terms recording where a derived relationship came from
└── conformance/                         # generated test fixtures — never load into a working repository

tools/
└── relationships2axioms.py           # generates the axioms and fixtures from relationships.xml

archimate.html                        # Human-readable vocabulary (purl.org/archimate#)
</pre>

## Specification 
This Ontology is a rendition of The Open Group® ArchiMate® 3.2 Specification. See the full specification at https://pubs.opengroup.org/architecture/archimate3-doc/. The model tries to remain faithful to the ArchiMate® 3.2 specification. No semantic reinterpretation is introduced at the base ontology level.

## License
© Alberto D. Mendoza | Licensed under Apache 2.0 | 
ArchiMate® is a registered trademark of The Open Group.
This ontology is an independent formalization and is not an official Open Group publication.

 
