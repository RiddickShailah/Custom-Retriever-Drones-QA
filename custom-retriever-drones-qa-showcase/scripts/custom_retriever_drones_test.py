"""Custom Retriever Drones QA workflow.

This sanitized script mirrors the notebook workflow used during US Dev testing.
It authenticates with an ArangoDB deployment, loads markdown files into a
`drones` collection, creates Custom Retriever tool definitions, and attempts to
start the retriever service before running QA scenarios.

Credentials are read from environment variables or prompted interactively.
Do not commit credentials, API keys, tokens, or private deployment URLs.
"""

from __future__ import annotations

import json
import os
import time
import uuid
import zipfile
from getpass import getpass
from pathlib import Path
from pprint import pprint
from typing import Any

import requests

requests.packages.urllib3.disable_warnings()


RETRIEVER_VERSION = "v0.0.17-7cc96b2"
COLLECTION_NAME = "drones"
TOOLS_COLLECTION = "Tools"
PROJECT_NAME = os.environ.get("GENAI_PROJECT_NAME", "drones")
BATCH_SIZE = 25


class ArangoQaClient:
    def __init__(self) -> None:
        self.server_url = self._read_config("ARANGO_DEPLOYMENT_ENDPOINT", "US Dev endpoint").rstrip("/")
        self.db_name = self._read_config("DB_NAME", "Database name")
        self.username = self._read_config("ARANGO_USERNAME", "Arango username")
        self.password = self._read_secret("ARANGO_PASSWORD", "Arango password")
        self.openai_api_key = self._read_secret("OPENAI_API_KEY", "OpenAI API key")
        self.jwt_token: str | None = None
        self.service_id_full: str | None = None
        self.retriever_service_id: str | None = None

    @staticmethod
    def _read_config(env_key: str, prompt: str) -> str:
        value = os.environ.get(env_key)
        if value:
            return value
        return input(f"{prompt}: ").strip()

    @staticmethod
    def _read_secret(env_key: str, prompt: str) -> str:
        value = os.environ.get(env_key)
        if value:
            return value
        return getpass(f"{prompt}: ")

    def print_metadata(self) -> None:
        print("========== TEST METADATA ==========")
        print("Environment: US Dev")
        print("Retriever version:", RETRIEVER_VERSION)
        print("Database:", self.db_name)
        print("Project:", PROJECT_NAME)
        print("Dataset: Drones markdown files")
        print("Collection:", COLLECTION_NAME)
        print("===================================")

    def authenticate(self) -> None:
        response = requests.post(
            f"{self.server_url}/_open/auth",
            json={"username": self.username, "password": self.password},
            timeout=60,
            verify=False,
        )

        self._raise_with_debug(response, "AUTH")
        self.jwt_token = response.json()["jwt"]
        print("Authenticated successfully.")

    def headers(self) -> dict[str, str]:
        if not self.jwt_token:
            raise RuntimeError("JWT token is missing. Authenticate first.")
        return {
            "Authorization": f"Bearer {self.jwt_token}",
            "Content-Type": "application/json",
        }

    def api(
        self,
        suffix: str,
        payload: dict[str, Any] | None = None,
        method: str = "POST",
        timeout: int = 180,
    ) -> dict[str, Any]:
        response = requests.request(
            method,
            f"{self.server_url}{suffix}",
            json=payload,
            headers=self.headers(),
            timeout=timeout,
            verify=False,
        )

        self._raise_with_debug(response, "API", payload)
        return response.json() if response.text else {}

    @staticmethod
    def _redact_payload(payload: dict[str, Any] | None) -> dict[str, Any]:
        safe_payload = json.loads(json.dumps(payload or {}))

        def redact(value: Any) -> Any:
            if isinstance(value, dict):
                return {
                    key: "[REDACTED]" if "key" in key.lower() or "password" in key.lower() else redact(item)
                    for key, item in value.items()
                }
            if isinstance(value, list):
                return [redact(item) for item in value]
            return value

        return redact(safe_payload)

    def _raise_with_debug(
        self,
        response: requests.Response,
        label: str,
        payload: dict[str, Any] | None = None,
    ) -> None:
        if response.ok:
            return

        print(f"\n{label} ERROR")
        print("Status:", response.status_code)
        print("URL:", response.url)
        if payload is not None:
            print("Payload:")
            pprint(self._redact_payload(payload))
        print("Response text:")
        print(response.text[:4000])
        print()
        response.raise_for_status()

    def aql(self, query: str, bind_vars: dict[str, Any] | None = None) -> dict[str, Any]:
        body: dict[str, Any] = {"query": query}
        if bind_vars:
            body["bindVars"] = bind_vars
        return self.api(f"/_db/{self.db_name}/_api/cursor", body, timeout=300)

    def create_collection_if_missing(self, name: str) -> None:
        try:
            self.api(f"/_db/{self.db_name}/_api/collection", {"name": name}, timeout=60)
            print(f"Created collection: {name}")
        except requests.HTTPError as exc:
            if exc.response is not None and exc.response.status_code == 409:
                print(f"Collection already exists: {name}")
                return
            raise

    def start_service(self) -> None:
        startup_env = {
            "db_name": self.db_name,
            "genai_project_name": PROJECT_NAME,
            "chat_api_provider": "openai",
            "embedding_api_provider": "openai",
            "chat_api_url": "https://api.openai.com/v1",
            "embedding_api_url": "https://api.openai.com/v1",
            "chat_model": "gpt-4o",
            "embedding_model": "text-embedding-3-small",
            "embedding_dim": "512",
            "chat_api_key": self.openai_api_key,
            "embedding_api_key": self.openai_api_key,
        }

        response = self.api(
            "/gen-ai/v1/service",
            {"service_name": "arangodb-graphrag-retriever", "env": startup_env},
            timeout=300,
        )

        self.service_id_full = response["serviceInfo"]["serviceId"]
        self.retriever_service_id = self.service_id_full.split("-")[-1]
        print("Full service ID:", self.service_id_full)
        print("Retriever path ID:", self.retriever_service_id)
        pprint(response)

    def stop_service(self) -> None:
        if not self.service_id_full:
            print("No service ID captured; skipping service stop.")
            return

        response = self.api(
            f"/gen-ai/v1/service/{self.service_id_full}",
            {"service_id": self.service_id_full},
            method="DELETE",
            timeout=300,
        )
        print("Stopped retriever service:")
        pprint(response)

    def retriever_path(self) -> str:
        if not self.retriever_service_id:
            raise RuntimeError("Retriever service ID is missing.")
        return f"/graphrag/retriever/{self.retriever_service_id}"

    def health_check(self) -> dict[str, Any]:
        return self.api(f"{self.retriever_path()}/v1/health", method="GET", timeout=60)

    def wait_for_health(self) -> None:
        print("Waiting for retriever service health check...")
        for attempt in range(60):
            try:
                health = self.health_check()
                print(health)
                if str(health.get("status", "")).upper() == "OK":
                    print(f"Retriever healthy after {attempt * 2}s")
                    return
            except Exception as exc:
                print("Waiting for health check:", exc)
            time.sleep(2)
        raise TimeoutError("Retriever service did not become healthy.")

    def query_unary(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.api(f"{self.retriever_path()}/v1/graphrag-query", payload, timeout=300)

    def query_stream(self, payload: dict[str, Any]):
        url = f"{self.server_url}{self.retriever_path()}/v1/graphrag-query-stream"
        stream_headers = {**self.headers(), "Accept": "application/x-ndjson"}

        with requests.post(
            url,
            json=payload,
            headers=stream_headers,
            stream=True,
            timeout=(10, 300),
            verify=False,
        ) as response:
            self._raise_with_debug(response, "STREAM", payload)
            for line in response.iter_lines(decode_unicode=True):
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue


def find_markdown_files(data_dir: Path) -> list[Path]:
    zip_candidates = [
        data_dir / "single_newspieces.zip",
        data_dir / "single_newpieces.zip",
        Path("single_newspieces.zip"),
        Path("single_newpieces.zip"),
    ]

    extract_dir = data_dir / "single_newspieces"
    extract_dir.mkdir(parents=True, exist_ok=True)

    for candidate in zip_candidates:
        if candidate.exists():
            print(f"Found zip file: {candidate}")
            with zipfile.ZipFile(candidate, "r") as archive:
                archive.extractall(extract_dir)
            print(f"Extracted zip to: {extract_dir}")
            break
    else:
        print("No zip file found. Looking for uploaded .md files directly.")

    search_dirs = [extract_dir, data_dir, Path(".")]
    seen: set[Path] = set()
    markdown_files: list[Path] = []

    for search_dir in search_dirs:
        if not search_dir.exists():
            continue
        for path in search_dir.rglob("*.md"):
            resolved = path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            markdown_files.append(path)

    print("Markdown files found:", len(markdown_files))
    if markdown_files:
        print("First 5 markdown files:")
        for path in markdown_files[:5]:
            print("-", path)

    return markdown_files


def prepare_documents(markdown_files: list[Path]) -> list[dict[str, Any]]:
    documents: list[dict[str, Any]] = []

    for index, path in enumerate(markdown_files):
        content = path.read_text(errors="ignore").strip()
        if not content:
            continue
        documents.append(
            {
                "_key": f"drone_md_{index}",
                "file_name": path.name,
                "path": str(path),
                "content": content,
                "dataset": "drones",
                "source_format": "markdown",
                "retriever_test_version": RETRIEVER_VERSION,
            }
        )

    print("Documents prepared:", len(documents))
    total_chars = sum(len(document["content"]) for document in documents)
    print("Total characters:", total_chars)
    print("Average characters per document:", round(total_chars / max(len(documents), 1), 2))
    return documents


def insert_documents(client: ArangoQaClient, documents: list[dict[str, Any]]) -> int:
    if not documents:
        raise ValueError("No documents to insert.")

    for start in range(0, len(documents), BATCH_SIZE):
        batch = documents[start : start + BATCH_SIZE]
        client.aql(
            """
            FOR doc IN @docs
                UPSERT { _key: doc._key }
                INSERT doc
                UPDATE doc
                IN @@collection
            """,
            {"@collection": COLLECTION_NAME, "docs": batch},
        )
        print(f"Inserted/upserted batch {start // BATCH_SIZE + 1}: {len(batch)} documents")

    count_result = client.aql(
        """
        RETURN LENGTH(
            FOR doc IN @@collection
                RETURN 1
        )
        """,
        {"@collection": COLLECTION_NAME},
    )

    collection_count = count_result["result"][0]
    print("Collection count:", collection_count)
    return collection_count


def create_custom_tools(client: ArangoQaClient) -> list[dict[str, Any]]:
    tools = [
        {
            "tool_id": "drones_lexical_search",
            "tool_type": "custom_retriever",
            "description": "Search Drones markdown dataset documents using lexical text search.",
            "config": {
                "collection": COLLECTION_NAME,
                "search_modes": [{"type": "lexical", "field": "content", "weight": 1.0}],
                "top_k": 10,
                "show_citations": True,
            },
        },
        {
            "tool_id": "drones_no_citations",
            "tool_type": "custom_retriever",
            "description": "Search Drones markdown dataset documents with citations disabled.",
            "config": {
                "collection": COLLECTION_NAME,
                "search_modes": [{"type": "lexical", "field": "content", "weight": 1.0}],
                "top_k": 5,
                "show_citations": False,
            },
        },
    ]

    for tool in tools:
        client.aql(
            "FOR t IN Tools FILTER t.tool_id == @tool_id REMOVE t IN Tools",
            {"tool_id": tool["tool_id"]},
        )
        client.aql("INSERT @tool INTO Tools", {"tool": tool})
        print("Created tool:", tool["tool_id"])

    return tools


def add_result(results: list[dict[str, str]], test_id: str, scenario: str, status: str, notes: str) -> None:
    results.append({"ID": test_id, "Scenario": scenario, "Status": status, "Notes": notes})


def run_qa_tests(client: ArangoQaClient) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []

    test_cases = [
        (
            "DIR-01",
            "Basic Drones lexical search",
            {
                "query": "What drone-related topics are discussed in the dataset?",
                "query_type": 4,
                "custom_tools": ["drones_lexical_search"],
                "include_metadata": True,
                "use_cache": False,
                "auto_create_indexes": True,
            },
        ),
        (
            "DIR-02",
            "Specific Drones use-case query",
            {
                "query": "Find information about drones used for photography, video, mapping, delivery, military use, or inspection.",
                "query_type": 4,
                "custom_tools": ["drones_lexical_search"],
                "include_metadata": True,
                "use_cache": False,
                "auto_create_indexes": True,
            },
        ),
        (
            "DIR-03",
            "Citations disabled",
            {
                "query": "Summarize the key drone use cases in the dataset.",
                "query_type": 4,
                "custom_tools": ["drones_no_citations"],
                "include_metadata": True,
                "use_cache": False,
                "auto_create_indexes": True,
            },
        ),
    ]

    for test_id, scenario, payload in test_cases:
        print(f"\nRunning {test_id}: {scenario}")
        response = client.query_unary(payload)
        metadata = str(response.get("metadata", ""))
        status = "PASS" if payload["custom_tools"][0] in metadata else "REVIEW"
        if test_id == "DIR-03":
            text = str(response.get("result", ""))
            status = "FAIL" if "[CITE:" in text or "[[" in text else "PASS"
        add_result(results, test_id, scenario, status, metadata[:300])

    unique_query = f"Drones cache test query {uuid.uuid4().hex[:8]}"
    cache_payload = {
        "query": unique_query,
        "query_type": 4,
        "custom_tools": ["drones_lexical_search"],
        "include_metadata": True,
        "use_cache": True,
        "auto_create_indexes": True,
    }

    first = client.query_unary(cache_payload)
    first_meta = str(first.get("metadata", ""))
    first_cached = '"cached": true' in first_meta or '"cached":true' in first_meta
    add_result(results, "FT-01", "Cache miss first call", "FAIL" if first_cached else "PASS", first_meta[:300])

    time.sleep(2)
    second = client.query_unary(cache_payload)
    second_meta = str(second.get("metadata", ""))
    second_cached = '"cached": true' in second_meta or '"cached":true' in second_meta
    add_result(results, "FT-02", "Cache hit second call", "PASS" if second_cached else "REVIEW", second_meta[:300])

    return results


def main() -> None:
    client = ArangoQaClient()
    client.print_metadata()
    client.authenticate()

    client.create_collection_if_missing(COLLECTION_NAME)
    client.create_collection_if_missing(TOOLS_COLLECTION)

    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    markdown_files = find_markdown_files(data_dir)
    documents = prepare_documents(markdown_files)
    collection_count = insert_documents(client, documents)

    try:
        client.start_service()
        client.wait_for_health()
    except requests.HTTPError:
        print("\nService startup failed. Data ingestion completed before this failure.")
        print("Report this as a service/platform blocker if the error mentions ArangoPlatformLink.")
        raise

    create_custom_tools(client)
    qa_results = run_qa_tests(client)

    print("\n========== QA SUMMARY ==========")
    pprint(qa_results)

    print("\n========== FINAL TEST METADATA ==========")
    print("Environment: US Dev")
    print("Retriever version tested:", RETRIEVER_VERSION)
    print("Database:", client.db_name)
    print("Project:", PROJECT_NAME)
    print("Markdown files found:", len(markdown_files))
    print("Documents inserted/upserted:", len(documents))
    print("Collection:", COLLECTION_NAME)
    print("Collection count:", collection_count)
    print("Service ID:", client.service_id_full)


if __name__ == "__main__":
    main()
