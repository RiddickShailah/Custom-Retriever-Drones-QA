# Bug Report: US Dev Custom Retriever Service Startup Failure

## Title

US Dev Custom Retriever service fails to install due to missing `ArangoPlatformLink`

## Environment

| Field | Value |
|---|---|
| Environment | US Dev |
| Retriever version | `v0.0.17-7cc96b2` |
| Database | tester-owned database |
| GenAI project | `drones` |
| Data collection | `drones` |
| Tool collection | `Tools` |
| Service | `arangodb-graphrag-retriever` |

## Data Load Evidence

| Metric | Value |
|---|---:|
| Markdown files found | 345 |
| Documents prepared | 345 |
| Documents inserted/upserted | 345 |
| Final collection count | 345 |
| Total characters loaded | 1,741,527 |
| Average characters per document | 5,047.9 |

## Steps to Reproduce

1. Log into US Dev.
2. Use or create a tester-owned database.
3. Create or use GenAI project `drones`.
4. Create or use collection `drones`.
5. Create or use collection `Tools`.
6. Load the Drones markdown files into the `drones` collection.
7. Verify the collection count.
8. Start the retriever service with:

```json
{
  "service_name": "arangodb-graphrag-retriever",
  "env": {
    "db_name": "tester_owned_database",
    "genai_project_name": "drones",
    "chat_api_provider": "openai",
    "embedding_api_provider": "openai",
    "chat_api_url": "https://api.openai.com/v1",
    "embedding_api_url": "https://api.openai.com/v1",
    "chat_model": "gpt-4o",
    "embedding_model": "text-embedding-3-small",
    "embedding_dim": "512"
  }
}
```

Sensitive fields such as API keys and passwords were omitted from this report.

## Expected Result

The platform should install/start the `arangodb-graphrag-retriever` service and return a service ID similar to:

```text
arangodb-graphrag-retriever-xxxxx
```

The notebook should then continue to health-check the retriever and execute Custom Retriever tests.

## Actual Result

The service startup request failed with:

```text
500 Internal Server Error
Unable to run action: Install...
could not get information about ArangoPlatformLink arangodb-graphrag-retriever...
resource not found in the US Dev namespace
```

## Impact

The following test categories were blocked:

- Validation tests
- Direct custom retrieval tests
- Multi-tool merge tests
- Cache behavior tests
- Streaming response tests

## Analysis

The failure occurred after:

- successful authentication,
- successful collection creation/use,
- successful markdown discovery,
- successful document preparation,
- successful document insertion,
- successful collection count verification,
- correction of the GenAI project name from `default_project` to `drones`.

Because the data path succeeded, the error appears to be a service installation or platform configuration issue rather than a data or notebook issue.

## Suggested Owner

US Dev platform owner, retriever deployment owner, or service infrastructure owner.

## Suggested Fix Areas

Investigate whether:

1. `arangodb-graphrag-retriever` version `v0.0.17-7cc96b2` is registered correctly in US Dev.
2. The expected `ArangoPlatformLink` exists in the US Dev namespace.
3. The service installer is referencing the correct retriever resource name.
4. A partially failed service installation left stale metadata.
5. Testers should reuse an existing retriever service ID instead of creating a new service instance.

## Status

Blocked pending platform/service remediation.
