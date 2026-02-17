# Archimate Ontology (OWL + SHACL)
An OWL/RDF formalization of the ArchiMate® 3.2 Specification, including executable validation using SHACL.

This repository provides:
* OWL ontology of ArchiMate enterprise architecture language
* SKOS file with ArchiMate vocabulary, published as HTML
* SHACL constraints that enforce the ArchiMate metamodel
* Support for custom profiles and specializations
* Derivation rules

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
  2026-02-10
  
### Author
  Alberto D. Mendoza  
  https://albertodmendoza.net

## Repo Structure
<pre>
ontology/ 
├── archimate.ttl                     # Main ontology file (purl.org/archimate/owl)
├── archimate_skos.ttl                # Vocabulary (purl.org/archimate/skos)
├── archimate.html                    # Human-readable vocabulary (purl.org/archimate#)
└── archimate_profile_examples.ttl    # Profile examples

validation/
├── archimate_validation_core.ttl            # Level 1: graph integrity, concept requirements
├── archimate_validation_metamodel.ttl       # Level 2: metamodel pattern rules
├── archimate_validation_strategy.ttl        # Level 3: Strategy layer relationship matrix
├── archimate_validation_business.ttl        # Level 3: Business layer relationship matrix
├── archimate_validation_profiles.ttl        # Profile-specific SHACL shapes
└── archimate_derivation_rules.ttl           # DR1-DR8, PDR1-PDR12 derivation rules
</pre>

## Specification 
This Ontology is a rendition of The Open Group® ArchiMate® 3.2 Specification. See the full specification at https://pubs.opengroup.org/architecture/archimate3-doc/. 
The model tries to remain faithful to the ArchiMate 3.2 specification. No semantic reinterpretation is introduced at the base ontology level.

### Disclaimer
ArchiMate is a registered trademark of The Open Group.
This project is an independent formalization and is not an official Open Group publication.
