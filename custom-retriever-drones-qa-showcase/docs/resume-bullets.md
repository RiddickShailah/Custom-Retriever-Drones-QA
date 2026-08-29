# Resume Bullet Options

## Primary Resume Entry

**Custom Retriever Drones QA: ArangoDB + GenAI Service Testing**  
Summer 2026  
Python · REST APIs · ArangoDB · AQL · GenAI Services · QA Automation · Jupyter

- Built a reproducible QA workflow to evaluate ArangoDB Custom Retriever behavior in US Dev using a Drones markdown corpus and the deployed retriever version `v0.0.17-7cc96b2`.
- Automated dataset ingestion for 345 markdown documents totaling 1.74M characters, transforming raw article files into structured ArangoDB documents with retriever-version metadata.
- Designed Custom Retriever tool definitions for lexical search and citation-disabled retrieval over a `drones` collection using `query_type: 4` and `custom_tools` payloads.
- Created a 10-scenario QA matrix covering invalid tool input, direct retrieval, multi-tool execution, cache behavior, citation suppression, and streaming response validation.
- Diagnosed US Dev service startup failures across HTTP 400, 404, and 500 responses, identifying a backend blocker where `arangodb-graphrag-retriever` could not install due to a missing `ArangoPlatformLink`.
- Produced an escalation-ready bug report with reproducible steps, request context, quantitative ingestion evidence, expected/actual behavior, and platform remediation recommendations.

## Shorter Resume Version

**Custom Retriever Drones QA: ArangoDB + GenAI Testing**  
Summer 2026  
Python · REST APIs · ArangoDB · AQL · Jupyter · QA Automation

- Built a notebook-based QA workflow for ArangoDB Custom Retriever testing in US Dev, loading 345 drone-related markdown files into ArangoDB and preparing `query_type: 4` retriever tool configurations.
- Designed validation, direct retrieval, multi-tool, cache, citation, and streaming test scenarios for retriever version `v0.0.17-7cc96b2`.
- Debugged service startup failures and documented a platform-level blocker involving a missing `ArangoPlatformLink` for `arangodb-graphrag-retriever`.

## Impact-Focused Version

**Custom Retriever Drones QA: ArangoDB Platform Testing**  
Summer 2026  
Python · REST · ArangoDB · AQL · GenAI Services · QA

- Converted an open-ended retriever testing assignment into a reproducible QA pipeline that ingested 345 markdown documents, generated Custom Retriever tool definitions, and produced a structured 10-case test matrix.
- Isolated setup issues from platform failures by validating authentication, collection creation, document upserts, and GenAI project configuration before identifying the final US Dev service-installation blocker.
- Authored a detailed bug report for a `500 Internal Server Error` caused by a missing `ArangoPlatformLink`, giving platform owners clear reproduction steps and remediation targets.

## Technical Version

**Custom Retriever Drones QA Automation**  
Summer 2026  
Python · Requests · ArangoDB · AQL · REST APIs · Jupyter

- Implemented a Python notebook workflow that authenticated with ArangoDB, created required collections, recursively parsed markdown files, and batch-upserted 345 documents into a Drones retrieval collection.
- Configured Custom Retriever tool documents in ArangoDB's `Tools` collection for lexical retrieval and no-citation retrieval over markdown content.
- Added robust HTTP diagnostics with safe payload redaction to debug `400 Bad Request`, `404 Not Found`, and `500 Internal Server Error` failures during retriever service setup.
- Built a QA plan for Custom Retriever endpoint behavior, including invalid input handling, direct retrieval, multi-tool merge, cache validation, and streaming response checks.

## Interview Talking Points

- The project was valuable even though full retrieval testing was blocked because the blocker itself was a legitimate QA finding.
- Data ingestion was validated separately from service startup, which helped prove the issue was not caused by malformed markdown files.
- The initial `default_project` failure was a configuration issue; after switching to `drones`, the platform advanced to a deeper backend failure.
- The final blocker pointed to a missing platform resource rather than a Python or notebook bug.
- The project demonstrated the ability to debug across application, data, API, and infrastructure boundaries.
