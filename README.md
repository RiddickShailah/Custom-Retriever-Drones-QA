# Custom Retriever Drones QA Showcase

Python | REST APIs | ArangoDB | GenAI Services | QA Testing | Notebook Automation

This project documents an end-to-end QA investigation of ArangoDB custom retriever testing in a US Dev environment using a markdown corpus of drone-related news articles. The work focused on preparing a reproducible notebook workflow, loading markdown data into ArangoDB, configuring Custom Retriever tools, and identifying platform blockers before full query validation could run.

> Note: This repository is a sanitized portfolio version of the project. It does not include credentials, API keys, Slack links, internal deployment secrets, or the original article dataset.

## Highlights

- Built a reusable Python workflow to authenticate with an ArangoDB deployment, create collections, ingest markdown files, and prepare custom retriever tool definitions.
- Processed a Drones markdown corpus observed at 345 files and 1,741,527 total characters, averaging 5,047.9 characters per document.
- Designed a QA matrix for Custom Retriever `query_type: 4` flows, including validation, direct retrieval, multi-tool, cache, and streaming scenarios.
- Diagnosed multiple environment and service-startup failures, separating notebook/data issues from backend platform blockers.
- Produced an escalation-ready bug report for a US Dev retriever service installation failure involving a missing `ArangoPlatformLink` resource.

## Project Context

The testing request was to validate the latest Custom Retriever version in US Dev:

```text
Retriever version: v0.0.17-7cc96b2
Environment: US Dev
Dataset: Drones markdown files
Database: tester-owned database
GenAI project: drones
Collection: drones
```

The intended flow was:

1. Log into US Dev.
2. Create a personal database.
3. Create a notebook folder.
4. Upload Drones markdown data.
5. Follow reference Custom Retriever notebooks.
6. Start the `arangodb-graphrag-retriever` service.
7. Create custom retriever tool definitions.
8. Run validation, retrieval, cache, multi-tool, and streaming tests.
9. Document results and blockers.

## Repository Structure

```text
custom-retriever-drones-qa-showcase/
  README.md
  requirements.txt
  data/
    README.md
  docs/
    detailed-project-report.md
    bug-report.md
    resume-bullets.md
    github-publishing.md
  scripts/
    custom_retriever_drones_test.py
```

## Quantitative Results

| Metric | Observed Value |
|---|---:|
| Markdown files found | 345 |
| Documents prepared | 345 |
| Documents inserted/upserted | 345 |
| Final collection count | 345 |
| Total characters loaded | 1,741,527 |
| Average characters per document | 5,047.9 |
| Insert batch size | 25 |
| Insert batches completed | 14 |
| Planned QA scenarios | 10 |
| Custom retriever tools designed | 2 |
| Blocking platform errors found | 1 |

## Key Finding

The data pipeline completed successfully, but full retriever query testing was blocked by a backend service startup failure:

```text
500 Internal Server Error
Unable to run action: Install...
could not get information about ArangoPlatformLink arangodb-graphrag-retriever...
resource not found in the US Dev namespace
```

This indicated a US Dev platform/service installation issue rather than a notebook or data ingestion problem.

## Running the Sanitized Script

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Set environment variables:

```bash
export ARANGO_DEPLOYMENT_ENDPOINT="https://example.endpoint"
export DB_NAME="your_database"
export GENAI_PROJECT_NAME="drones"
export ARANGO_USERNAME="your_username"
export ARANGO_PASSWORD="your_password"
export OPENAI_API_KEY="your_openai_api_key"
```

Place markdown files under:

```text
data/single_newspieces/
```

or place a zip at:

```text
data/single_newspieces.zip
```

Then run:

```bash
python scripts/custom_retriever_drones_test.py
```

## Skills Demonstrated

- Python automation
- REST API debugging
- ArangoDB collection and AQL workflows
- Notebook-based QA execution
- Custom retriever tool design
- GenAI service configuration
- Dataset ingestion and validation
- Quantitative QA reporting
- Bug reproduction and escalation

## Status

The ingestion and setup portions succeeded. Full retriever testing remained blocked until the US Dev retriever service installation issue was resolved.
