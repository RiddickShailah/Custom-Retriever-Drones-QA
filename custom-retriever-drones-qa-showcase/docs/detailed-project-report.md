# Detailed Project Report: Custom Retriever Drones QA Testing

## 1. Executive Summary

This project investigated Custom Retriever testing in the US Dev environment using a Drones markdown dataset. The assigned retriever version was `v0.0.17-7cc96b2`.

The project successfully completed the setup and data-ingestion portions of the workflow:

- Authenticated into US Dev.
- Created or used a tester-owned database.
- Created or used the required ArangoDB collections.
- Loaded markdown files from the Drones dataset.
- Prepared structured documents for retrieval testing.
- Inserted/upserted all documents into ArangoDB.
- Verified the final collection count.
- Designed custom retriever tool definitions and a full QA test matrix.

Full custom retriever query testing was blocked by a backend service installation failure. The `arangodb-graphrag-retriever` service failed to start with a `500 Internal Server Error` referencing a missing `ArangoPlatformLink` resource. This was documented as a platform-level blocker rather than a notebook or dataset issue.

## 2. Objective

The original testing goal was to validate the latest Custom Retriever version in US Dev by:

1. Logging into US Dev.
2. Creating a database under the tester's name.
3. Choosing a notebook server.
4. Creating a notebook folder.
5. Uploading the Drones data.
6. Following shared reference notebooks.
7. Starting the Custom Retriever service.
8. Running query tests.
9. Recording all results, including the retriever version.
10. Reporting bugs and blockers.

## 3. Environment Metadata

| Field | Value |
|---|---|
| Environment | US Dev |
| Retriever version assigned | `v0.0.17-7cc96b2` |
| Database observed in execution | tester-owned database |
| Initial GenAI project attempted | `default_project` |
| Corrected GenAI project | `drones` |
| Primary data collection | `drones` |
| Tool collection | `Tools` |
| Dataset format | Markdown |
| Main service | `arangodb-graphrag-retriever` |
| Query mode | `query_type: 4` |
| Notebook folder | `shailah_custom_retriever_test` |

## 4. Reference Notebooks

Two reference notebooks informed the final testing workflow.

### 4.1 `custom_query.ipynb`

This notebook presented a QA-style flow for Custom Query testing:

- Authenticate.
- Start the retriever service.
- Create `custom_retriever` documents in `Tools`.
- Run validation tests.
- Run direct custom retriever tests.
- Run multi-tool tests.
- Run cache tests.
- Run streaming tests.
- Produce a QA summary table.
- Clean up test tools and stop the service.

### 4.2 `CustomRetreiver_Sample_Test.ipynb`

This notebook showed how Custom Retriever requests are structured:

```json
{
  "query": "example question",
  "query_type": 4,
  "custom_tools": ["tool_id"],
  "include_metadata": true,
  "use_cache": false,
  "auto_create_indexes": true
}
```

It also confirmed the service name:

```text
arangodb-graphrag-retriever
```

## 5. Dataset Details

The Drones dataset consisted of markdown files from news and analysis sources. Example source groups included:

- BBC
- Bloomberg
- El Radar
- South China Morning Post
- Sequoia
- Spiegel

Topic areas included:

- Military drones
- Counter-drone systems
- Drone delivery
- Drone manufacturing
- Drone investment
- AI-enabled defense systems
- Ukraine/Russia drone warfare
- Drone supply chains
- Low-altitude economy
- Autonomous systems

## 6. Quantitative Data

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
| Full batches | 13 |
| Final partial batch | 20 |
| Collections required | 2 |
| Custom retriever tools designed | 2 |
| Planned validation tests | 3 |
| Planned direct retriever tests | 3 |
| Planned multi-tool tests | 1 |
| Planned cache tests | 2 |
| Planned streaming tests | 1 |
| Total planned QA scenarios | 10 |

## 7. Implementation Summary

The testing script was designed to run as either a single notebook cell or a standalone Python script.

Major components:

1. Configuration and metadata capture.
2. Secure credential loading using environment variables or prompts.
3. Authentication against the ArangoDB deployment.
4. REST API helper functions.
5. AQL execution helper.
6. Collection creation helpers.
7. Markdown discovery and extraction.
8. Document preparation.
9. Batched document upserts.
10. Retriever service startup.
11. Health check.
12. Custom retriever tool creation.
13. QA test execution.
14. Result summarization.
15. Optional cleanup.

## 8. Custom Retriever Tool Design

### 8.1 `drones_lexical_search`

The primary retrieval tool searched markdown article content using lexical matching.

```json
{
  "tool_id": "drones_lexical_search",
  "tool_type": "custom_retriever",
  "description": "Search Drones markdown dataset documents using lexical text search.",
  "config": {
    "collection": "drones",
    "search_modes": [
      {
        "type": "lexical",
        "field": "content",
        "weight": 1.0
      }
    ],
    "top_k": 10,
    "show_citations": true
  }
}
```

### 8.2 `drones_no_citations`

The secondary tool tested citation suppression behavior.

```json
{
  "tool_id": "drones_no_citations",
  "tool_type": "custom_retriever",
  "description": "Search Drones markdown dataset documents with citations disabled.",
  "config": {
    "collection": "drones",
    "search_modes": [
      {
        "type": "lexical",
        "field": "content",
        "weight": 1.0
      }
    ],
    "top_k": 5,
    "show_citations": false
  }
}
```

## 9. Planned QA Matrix

| ID | Scenario | Purpose |
|---|---|---|
| VAL-01 | Missing `custom_tools` | Confirm invalid request handling |
| VAL-02 | Empty `custom_tools` | Confirm empty tool list does not crash |
| VAL-03 | Nonexistent tool ID | Confirm clear failed-tool behavior |
| DIR-01 | Basic Drones lexical search | Confirm retrieval over Drones content |
| DIR-02 | Specific Drones use-case query | Confirm targeted domain retrieval |
| DIR-03 | Citations disabled | Confirm `show_citations: false` behavior |
| MRG-01 | Two-tool merge | Confirm multi-tool execution metadata |
| FT-01 | First cached query | Confirm first call is cache miss |
| FT-02 | Repeated cached query | Confirm repeated call becomes cache hit |
| STR-01 | Streaming response | Confirm streaming delta chunks and final metadata |

## 10. Findings

### Finding 1: Data ingestion succeeded

The dataset was discovered, converted into structured documents, and inserted successfully.

Evidence:

```text
Markdown files found: 345
Documents prepared: 345
Documents inserted/upserted: 345
Collection count: 345
```

### Finding 2: Initial project name was incorrect

The first service startup attempt used:

```text
default_project
```

The platform returned:

```text
Project default_project not found in the metadata store under the tester-owned database.
Create the project before installing services.
```

Resolution:

```text
Changed project name to drones.
```

### Finding 3: Correct project name exposed a backend service bug

After switching to:

```text
genai_project_name: drones
```

the service startup progressed further but failed with:

```text
500 Internal Server Error
Unable to run action: Install...
could not get information about ArangoPlatformLink arangodb-graphrag-retriever...
resource not found in the US Dev namespace
```

This indicates a US Dev platform configuration or deployment problem.

### Finding 4: `Tools` collection must exist before tool insertion

An AQL query failed with `404` when attempting to remove tool documents from `Tools` before confirming the collection existed.

Resolution:

Added collection setup:

```python
create_collection_if_missing("Tools")
create_collection_if_missing("drones")
```

## 11. Bug and Blocker Summary

| Issue | Severity | Status | Notes |
|---|---|---|---|
| `default_project` missing | Medium | Resolved | Fixed by using project `drones` |
| Retriever service startup 500 | High | Blocked | Requires platform/service owner investigation |
| `Tools` collection missing | Low | Resolved | Fixed by creating collection before AQL usage |
| Duplicate collection warnings | Low | Expected | Occurred because notebook was rerun |

## 12. Root Cause Analysis

The project had both setup-level and platform-level issues.

The setup-level issues were addressable in the notebook:

- Wrong project name.
- Missing `Tools` collection.
- Duplicate collection warnings during reruns.

The platform-level issue was not addressable from the notebook:

- The retriever service installation process could not locate the expected `ArangoPlatformLink` resource.

The service startup error occurred after successful authentication and data insertion, so it was not caused by the dataset itself.

## 13. Impact

The backend service startup failure blocked all query-based Custom Retriever validation.

Blocked areas:

- Retrieval quality testing
- Citation behavior testing
- Multi-tool execution testing
- Cache behavior testing
- Streaming behavior testing
- Final QA pass/fail table completion

The project still produced useful QA evidence because it identified a reproducible environment blocker.

## 14. Skills Demonstrated

### Python and notebook development

- Built a reusable notebook workflow.
- Consolidated many cells into one runnable script.
- Used environment variables and secure prompts.
- Parsed markdown files recursively.
- Batched large document inserts.

### API and backend debugging

- Used REST endpoints for authentication, collection creation, service startup, and AQL execution.
- Diagnosed HTTP `400`, `404`, and `500` failures.
- Added error logging to print payloads and response bodies safely.
- Redacted sensitive fields from debug output.

### ArangoDB skills

- Created collections.
- Inserted/upserted documents.
- Ran AQL through the cursor API.
- Designed custom retriever tools using the `Tools` collection.
- Connected retriever configuration to database, project, collection, and search fields.

### QA testing skills

- Designed a structured QA matrix.
- Separated setup validation from product testing.
- Tracked expected versus actual behavior.
- Converted runtime errors into actionable bug reports.
- Documented quantitative evidence.

### Communication and reporting

- Summarized technical failures clearly.
- Created advisor-ready bug reports.
- Documented blocked status without overstating completed testing.
- Preserved security by excluding credentials and secrets.

## 15. Recommended Escalation

The following message can be sent to an advisor or platform owner:

```text
I am blocked while testing Custom Retriever v0.0.17-7cc96b2 in US Dev.

Completed successfully:
- Database used: tester-owned database
- GenAI project: drones
- Collection: drones
- Tools collection exists
- Markdown files found: 345
- Documents prepared: 345
- Documents inserted/upserted: 345
- Collection count verified: 345
- Total characters loaded: 1,741,527

Blocking issue:
Starting arangodb-graphrag-retriever through POST /gen-ai/v1/service fails with:

500 Internal Server Error
Unable to run action: Install...
could not get information about ArangoPlatformLink arangodb-graphrag-retriever...
resource not found in the US Dev namespace

Impact:
This blocks all Custom Retriever query tests, including validation, direct retrieval, multi-tool, cache, and streaming tests.

This appears to be a US Dev service installation/platform configuration issue rather than a notebook or data issue.
```

## 16. Final Status

| Category | Status |
|---|---|
| Setup | Complete |
| Data loading | Complete |
| Quantitative validation | Complete |
| Custom tool design | Complete |
| Service startup | Blocked |
| Query tests | Blocked |
| Bug report | Complete |
| Portfolio documentation | Complete |

## 17. Conclusion

This project successfully transformed an open-ended testing request into a structured QA workflow. The Drones markdown corpus was loaded and validated quantitatively, and a Custom Retriever test plan was prepared using the provided reference notebooks.

The primary outcome was the discovery of a backend US Dev blocker preventing the `arangodb-graphrag-retriever` service from starting. This blocker prevented full query execution but provided meaningful QA value by identifying a reproducible platform issue with clear evidence and escalation steps.
