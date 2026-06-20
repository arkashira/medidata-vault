# TECH_SPEC.md  

**Project:** `medidata-vault`  
**Owner:** Axentx – Data Integrity Team  
**Status:** Ready for implementation (shippable)  

---  

## 1. Overview  

`medidata-vault` provides **immutable, version‑controlled storage** for medical datasets together with a **tamper‑evident audit trail**. It is intended for use cases such as:

* Clinical trial data capture  
* Electronic health record (EHR) snapshots  
* Regulatory submissions that require full provenance  

The library is delivered as a **pure‑Python package** that can be embedded in any data‑processing pipeline (ETL, ML training, analytics). It stores data **off‑heap** in a configurable backend (filesystem, S3, or Azure Blob) while keeping lightweight metadata in a relational store (SQLite/PostgreSQL).  

---  

## 2. Architecture  

```
+-------------------+        +-------------------+        +-------------------+
|   Client App      |  API   |   medidata-vault  |  DB    |   Metadata Store |
| (Python, Java,   |<------>|   Core Library    |<------>| (SQLite / PG)    |
|  R, etc.)         |        |   (Python)        |        |                   |
+-------------------+        +-------------------+        +-------------------+
                                   |
                                   |  Blob Storage (FS / S3 / Azure)
                                   v
                           +-------------------+
                           |   Data Store      |
                           | (immutable files) |
                           +-------------------+
```

* **Client Layer** – thin wrapper exposing a clean, language‑agnostic API (`DataVersioning` class).  
* **Core Library** – implements versioning logic, hash‑based immutability, and audit‑trail generation.  
* **Metadata Store** – relational DB holding version records, lineage, and audit entries.  
* **Data Store** – immutable binary blobs (JSON, CSV, Parquet, DICOM, etc.) stored in a configurable backend.  

All components are **stateless** except the metadata DB; scaling is achieved by adding read‑replicas of the DB and additional blob storage nodes.  

---  

## 3. Key Components  

| Component | Responsibility | Public Interface |
|-----------|----------------|------------------|
| `DataVersioning` | Main façade for clients. Handles version creation, retrieval, and audit queries. | `add_version(data: bytes, meta: dict) -> VersionID`<br>`get_version(version_id: VersionID) -> bytes`<br>`list_versions(filter: dict) -> List[VersionMeta]`<br>`get_audit_trail(version_id: VersionID) -> List[AuditEntry]` |
| `VersionStore` | Persists immutable blobs to the configured backend. | `store_blob(blob: bytes) -> BlobRef`<br>`retrieve_blob(ref: BlobRef) -> bytes` |
| `MetadataRepository` | CRUD for version rows and audit rows. Abstracts SQLite/PostgreSQL. | `insert_version(meta: VersionMeta) -> None`<br>`fetch_version(id: VersionID) -> VersionMeta`<br>`insert_audit(entry: AuditEntry) -> None` |
| `Hasher` | Computes cryptographic hash (SHA‑256) of each blob for integrity & deduplication. | `hash(blob: bytes) -> str` |
| `AuditLogger` | Writes immutable audit entries (who, when, operation, hash). | `log(action: str, user: str, version_id: VersionID, details: dict) -> None` |
| `Config` | Central configuration (backend URLs, DB DSN, retention policies). | `load_from_env()`, `validate()` |

---  

## 4. Data Model  

### 4.1. Version Table  

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID (PK) | Unique version identifier |
| `blob_ref` | TEXT | Pointer to blob in Data Store (e.g., `s3://bucket/sha256`) |
| `hash` | CHAR(64) | SHA‑256 of the blob (hex) |
| `created_at` | TIMESTAMP | UTC timestamp of version creation |
| `created_by` | TEXT | User or service identifier |
| `metadata` | JSONB | Arbitrary key/value pairs supplied by client |
| `parent_id` | UUID (FK) | Optional link to previous version (for lineage) |

### 4.2. Audit Table  

| Column | Type | Description |
|--------|------|-------------|
| `id` | BIGSERIAL (PK) | Auto‑increment |
| `version_id` | UUID (FK) | Version this entry relates to |
| `action` | TEXT | `CREATE`, `READ`, `UPDATE`, `DELETE` |
| `actor` | TEXT | User/service performing the action |
| `timestamp` | TIMESTAMP | UTC |
| `details` | JSONB | Free‑form context (e.g., IP, client version) |
| `hash_snapshot` | CHAR(64) | Hash of the version at time of action (for tamper evidence) |

---  

## 5. API Specification  

All public methods raise `VaultError` (sub‑classed for `VersionNotFound`, `IntegrityError`, `PermissionError`).  

### 5.1. `add_version`  

```python
def add_version(self,
                data: bytes,
                meta: Optional[Dict[str, Any]] = None,
                user: str = "system") -> UUID:
    """
    Store a new immutable version.
    Steps:
      1. Compute SHA‑256 hash.
      2. Store blob (deduplication if hash already exists).
      3. Insert row in Version table.
      4. Write audit entry (action='CREATE').
    Returns the generated version UUID.
    """
```

### 5.2. `get_version`  

```python
def get_version(self,
                version_id: UUID,
                user: str = "system") -> bytes:
    """
    Retrieve the raw blob for a given version.
    Emits an audit entry (action='READ').
    Validates stored hash against computed hash; raises IntegrityError on mismatch.
    """
```

### 5.3. `list_versions`  

```python
def list_versions(self,
                  filter: Optional[Dict[str, Any]] = None,
                  limit: int = 100,
                  offset: int = 0) -> List[VersionMeta]:
    """
    Query versions by metadata fields, creator, date range, etc.
    No audit entry is generated (read‑only query).
    """
```

### 5.4. `get_audit_trail`  

```python
def get_audit_trail(self,
                    version_id: UUID,
                    limit: int = 1000,
                    offset: int = 0) -> List[AuditEntry]:
    """
    Return chronological audit entries for a version.
    """
```

---  

## 6. Technology Stack  

| Layer | Choice | Rationale |
|-------|--------|-----------|
| Language | **Python ≥3.10** | Strong ecosystem, easy integration with data pipelines |
| Hashing | `hashlib.sha256` (built‑in) | No external dependency, FIPS‑approved |
| Blob Backend | **Pluggable** (local FS, AWS S3, Azure Blob) via `fsspec` | Uniform API, future‑proof |
| Metadata DB | **SQLite** (dev / single‑node) **or** PostgreSQL (prod) | ACID, JSONB support, easy migration |
| ORM / DB Access | **SQLAlchemy 2.x** | Declarative models, async support |
| Config | **pydantic-settings** | Validation, env‑var loading |
| Logging | **structlog** + standard `logging` | Structured logs for observability |
| Testing | **pytest**, **hypothesis** (property‑based) | High coverage, fuzzing of hash/duplication |
| CI/CD | GitHub Actions (lint, test, build wheel) | Consistent pipeline |
| Packaging | **PEP‑517** (`pyproject.toml`), wheel distribution | Standard Python packaging |
| Documentation | **mkdocs** + **mkdocstrings** | Auto‑generated API docs |

---  

## 7. Dependencies  

| Dependency | Version | Scope |
|------------|---------|-------|
| python | >=3.10,<4.0 | runtime |
| sqlalchemy | >=2.0 | runtime |
| fsspec | >=2023.6.0 | runtime |
| s3fs | >=2023.6.0 | optional (S3 backend) |
| azure-storage-blob | >=12.19.0 | optional (Azure backend) |
| pydantic-settings | >=2.0 | runtime |
| structlog | >=24.0 | runtime |
| pytest | >=8.0 | dev |
| hypothesis | >=6.100 | dev |
| mkdocs | >=1.5 | docs |
| mkdocstrings | >=0.24 | docs |

All dependencies are Apache‑2.0 or MIT licensed, compatible with the project's mixed‑license data assets.

---  

## 8. Deployment & Operations  

### 8.1. Packaging  

* Build a wheel (`python -m build`) and publish to the internal PyPI (`axentx-pypi`).  
* Provide a Dockerfile for containerized usage (e.g., in Airflow or Kubeflow).  

### 8.2. Runtime Configuration  

| Variable | Example | Description |
|----------|---------|-------------|
| `VAULT_DB_DSN` | `postgresql://user:pwd@db:5432/vault` | DB connection string |
| `VAULT_BLOB_URL` | `s3://medidata-vault` | Root URL for blob backend |
| `VAULT_RETENTION_DAYS` | `3650` | Optional auto‑purge of audit entries (regulatory‑compliant default: keep forever) |
| `VAULT_LOG_LEVEL` | `INFO` | Logging verbosity |
| `VAULT_ALLOWED_USERS` | `user1,user2` | Comma‑separated list for simple ACL (future RBAC extension) |

Configuration is loaded via `Config.load_from_env()` at library import time; missing required vars raise `ConfigError`.

### 8.3. Scaling  

* **Stateless workers** – multiple instances of the library can run concurrently; DB row‑level locks guarantee uniqueness of version IDs.  
* **Blob deduplication** – identical hashes map to the same object; storage cost grows linearly with unique data only.  
* **Read replicas** – PostgreSQL read‑replicas can serve `get_version` and `list_versions` without impacting write throughput.  

### 8.4. Monitoring  

* Emit structured logs (`structlog`) with fields: `event`, `version_id`, `user`, `duration_ms`.  
* Export Prometheus metrics via `prometheus_client` (optional):  
  * `vault_version_created_total`  
  * `vault_version_read_total`  
  * `vault_audit_entries_total`  
  * `vault_blob_storage_bytes`  

### 8.5. Security  

* All blob URLs are signed (S3 pre‑signed URLs or Azure SAS) when accessed directly; the library never exposes raw credentials.  
* Hash verification on every read guarantees **tamper evidence**.  
* Optional **encryption‑at‑rest** is delegated to the storage backend (e.g., S3 SSE‑KMS).  

---  

## 9. Testing Strategy  

1. **Unit Tests** – cover each component (hashing, DB CRUD, blob store).  
2. **Integration Tests** – spin up a PostgreSQL container and a MinIO S3 mock; run full end‑to‑end scenarios.  
3. **Property‑Based Tests** – using `hypothesis` to generate random payloads, ensuring:  
   * `add_version` → `get_version` returns identical bytes.  
   * Duplicate payloads result in a single blob (deduplication).  
4. **Performance Benchmarks** – simple `pytest-benchmark` suite to verify <10 ms latency for reads on local FS.  

All tests run in CI on Python 3.10, 3.11, and 3.12. Coverage target: **≥ 90 %**.

---  

## 10. Future Enhancements  

| Feature | Priority | Notes |
|---------|----------|-------|
| Role‑Based Access Control (RBAC) | High | Integrate with Axentx IAM service. |
| Immutable Ledger (Merkle tree) | Medium | Provide cryptographic proof of entire dataset history. |
| Data Lifecycle Policies | Medium | Automatic archival to Glacier/Cold storage after N years. |
| Streaming Ingestion API | Low | Support for chunked uploads of large files (>5 GB). |
| Multi‑tenant isolation | Low | Separate schemas per tenant for SaaS offering. |

---  

## 11. Glossary  

* **VersionID** – UUID that uniquely identifies a stored data version.  
* **BlobRef** – Backend‑specific URI pointing to the immutable data object.  
* **AuditEntry** – Immutable record of an operation performed on a version.  

---  

*Prepared by:* Senior Product/Engineering Lead, Axentx – Data Integrity Team  
*Date:* 2026‑06‑20  

---
