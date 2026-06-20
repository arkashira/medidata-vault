# STORIES.md – medidata‑vault

## Table of Contents
1. [Epics Overview](#epics-overview)  
2. [MVP – Core Versioning & Audit Trail](#epic-1‑core-versioning--audit-trail)  
3. [Enterprise Enhancements](#epic-2‑enterprise‑features)  
4. [Observability & Ops](#epic-3‑observability--ops)  
5. [Glossary](#glossary)  

---

## Epics Overview

| Epic ID | Title | Description | MVP? |
|---------|-------|-------------|------|
| **E1** | **Core Versioning & Audit Trail** | Implement the fundamental data‑versioning engine, immutable audit logs, and a clean Python API. | ✅ |
| **E2** | **Enterprise Features** | Add role‑based access control, snapshot/branching, and compliance export (HIPAA, GDPR). | ❌ |
| **E3** | **Observability & Ops** | Provide monitoring, CLI tooling, and CI/CD integration for automated testing and deployment. | ❌ |

Stories are ordered within each epic from highest priority (MVP) to lower‑priority enhancements.

---

## Epic 1 – Core Versioning & Audit Trail

> **Goal:** Deliver a reliable, thread‑safe library that lets downstream applications version arbitrary data objects and retrieve a tamper‑evident audit trail.

| # | User Story | Acceptance Criteria |
|---|------------|----------------------|
| **E1‑S1** | **As a data engineer, I want to create a `DataVersioning` instance, so that I can start tracking versions for a specific dataset.** | - `DataVersioning(dataset_id: str)` can be instantiated.<br>- Constructor raises a clear error if `dataset_id` is empty or already in use.<br>- Instance exposes `dataset_id` as a read‑only property. |
| **E1‑S2** | **As a developer, I want to add a new version with a payload and metadata, so that the system records the change.** | - Method `add_version(payload: Any, metadata: dict = None) -> str` returns a UUID version identifier.<br>- Payload is deep‑copied and stored immutably.<br>- Metadata (e.g., `author`, `timestamp`, `comment`) is optional but, if supplied, is persisted with the version.<br>- Adding a version increments an internal monotonic version counter. |
| **E1‑S3** | **As a data analyst, I want to retrieve a specific version by its identifier, so that I can reproduce historic results.** | - Method `get_version(version_id: str) -> Tuple[Any, dict]` returns the stored payload and its metadata.<br>- Raises `VersionNotFoundError` for unknown IDs.<br>- Returned payload is a deep copy (no mutation of stored data). |
| **E1‑S4** | **As a compliance officer, I need an immutable audit trail of all version operations, so that I can prove data lineage.** | - Method `get_audit_trail() -> List[dict]` returns a chronologically ordered list of audit entries.<br>- Each entry contains: `version_id`, `action` (`add`/`retrieve`), `timestamp`, `actor` (if provided), and a cryptographic hash of the payload.<br>- The audit trail is stored in a write‑once append‑only structure; attempts to modify past entries raise `AuditTrailTamperError`. |
| **E1‑S5** | **As a tester, I want deterministic version identifiers for given inputs in a test environment, so that snapshots are reproducible.** | - When an optional `seed` argument is supplied to `add_version`, the generated UUID is deterministic (e.g., UUID5 with namespace `dataset_id`).<br>- Unit tests can assert exact version IDs. |
| **E1‑S6** | **As a DevOps engineer, I want the library to be thread‑safe, so that concurrent writes do not corrupt state.** | - All public methods are protected by a re‑entrant lock.<br>- Stress test with 100 concurrent `add_version` calls completes without data loss or race conditions. |
| **E1‑S7** | **As a CI pipeline, I need a simple way to run the test suite, so that code quality is enforced on every commit.** | - `pytest` discovers all tests under `tests/` with a single command `pytest -q`.<br>- Test suite includes at least: successful creation, version addition, retrieval, audit trail integrity, and thread‑safety tests.<br>- CI badge in README updates on each push. |
| **E1‑S8** | **As a package consumer, I want clear documentation and type hints, so that I can integrate the library with minimal friction.** | - All public functions/classes are annotated with PEP‑484 type hints.<br>- README includes a quick‑start code snippet and a link to generated API docs (e.g., via `mkdocs` or `pdoc`).<br>- `setup.cfg`/`pyproject.toml` declares `python_requires >=3.9`. |

### MVP Definition (Epic 1)

The MVP consists of stories **E1‑S1** through **E1‑S8**. Completion of these stories yields a publishable `medidata-vault` package that passes all tests, is thread‑safe, and provides immutable versioning with an audit trail.

---

## Epic 2 – Enterprise Features

| # | User Story | Acceptance Criteria |
|---|------------|----------------------|
| **E2‑S1** | As a security admin, I want role‑based access control (RBAC) on version operations, so that only authorized users can modify data. | - `add_version` and `get_version` accept an `actor` argument.<br>- Configurable ACL (read/write) per `dataset_id` stored in a JSON/YAML policy file.<br>- Unauthorized actions raise `PermissionDeniedError`. |
| **E2‑S2** | As a data steward, I want to create named snapshots (branches) of a dataset, so that I can experiment without affecting the main line. | - API `create_snapshot(name: str, base_version: str) -> Snapshot`.<br>- Snapshots support independent `add_version` calls while preserving lineage to the base version.<br>- `list_snapshots()` returns all snapshot names and their head version IDs. |
| **E2‑S3** | As a compliance auditor, I need to export the full audit trail in CSV and JSON formats, so that it can be ingested by external reporting tools. | - Method `export_audit(format: Literal["csv","json"], path: Path) -> None` writes a well‑formed file.<br>- Export includes all fields from the internal audit entries and is UTF‑8 encoded. |
| **E2‑S4** | As a legal officer, I want automatic retention policies (e.g., purge after 7 years), so that we stay compliant with data‑retention regulations. | - Configurable `retention_days` per dataset.<br>- Background job `purge_expired_versions()` removes versions older than the threshold and appends a `purge` entry to the audit trail.<br>- Purge operation is immutable and logged. |
| **E2‑S5** | As a data scientist, I want to query versions by metadata (e.g., author or date range), so that I can locate relevant data quickly. | - Method `query_versions(**filters) -> List[VersionInfo]` supports filtering on `author`, `timestamp`, and custom metadata keys.<br>- Returns ordered list of matching version IDs. |

### Release Gate for Epic 2
Epic 2 is slated for **Phase 2** (post‑MVP) once the core library demonstrates stability in production pilots.

---

## Epic 3 – Observability & Ops

| # | User Story | Acceptance Criteria |
|---|------------|----------------------|
| **E3‑S1** | As a site reliability engineer, I want structured logs for every operation, so that incidents can be traced. | - Library uses `structlog` to emit JSON logs for `add_version`, `get_version`, and audit‑trail writes.<br>- Log entries include `dataset_id`, `version_id`, `action`, `actor`, and `request_id` (correlation ID). |
| **E3‑S2** | As a developer, I want a CLI (`medidata-vault-cli`) to inspect datasets, so that I can debug without writing code. | - Commands: `list-datasets`, `list-versions <dataset>`, `show-version <dataset> <version>`, `audit <dataset>`.<br>- CLI respects the same RBAC rules as the library. |
| **E3‑S3** | As a CI/CD engineer, I want a Dockerfile that builds the library with all dependencies, so that deployments are reproducible. | - Multi‑stage Dockerfile produces a minimal `python:slim` image with the package installed via `pip install .`.<br>- Image size < 120 MB.<br>- `docker run --rm <image> pytest` executes the test suite inside the container. |
| **E3‑S4** | As a product manager, I want usage metrics (e.g., number of versions added per day) exported to Prometheus, so that we can monitor adoption. | - Optional `metrics` module exposing counters via `prometheus_client`.<br>- Metrics: `versions_total`, `audit_entries_total`, `active_datasets`. |
| **E3‑S5** | As a security auditor, I need the ability to verify the cryptographic hash chain of the audit log, so that tampering can be detected. | - Method `verify_audit_integrity() -> bool` recomputes hashes and returns `True` only if the chain is intact.<br>- Failure logs a warning with the mismatched entry. |

### Observability Roadmap
Epic 3 will be delivered after Enterprise Features, enabling robust production monitoring and operational tooling.

---

## Glossary

| Term | Definition |
|------|------------|
| **Dataset** | Logical collection of versioned data identified by a unique `dataset_id`. |
| **Version ID** | UUID (or deterministic UUID5 when seeded) that uniquely identifies a stored payload. |
| **Audit Trail** | Append‑only log of all actions performed on a dataset, including cryptographic hashes for integrity. |
| **Snapshot / Branch** | Named pointer to a specific version that can diverge independently from the main line. |
| **Actor** | Identifier (e.g., user email, service account) supplied to operations for RBAC and audit purposes. |
| **Retention Policy** | Configurable rule that defines how long versions are kept before automatic purge. |

--- 

*Prepared by the senior product/engineering lead, 2026‑06‑20.*
