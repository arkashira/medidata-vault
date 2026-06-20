# REQUIREMENTS.md  

## 1. Overview  
**Project Name:** medidata‑vault  
**Purpose:** Provide a lightweight, language‑agnostic library for immutable data versioning and a tamper‑evident audit trail. The library must be easy to embed in existing Python services that handle sensitive medical data, ensuring every change is recorded, queryable, and compliant with common regulatory standards (e.g., HIPAA, GDPR).  

---

## 2. Functional Requirements  

| ID | Description | Priority |
|----|-------------|----------|
| **FR‑1** | **Create a `DataVersioning` class** that can be instantiated with a storage backend (in‑memory, file‑system, or relational DB). | Must |
| **FR‑2** | **Add a new version** via `add_version(data: Any, metadata: dict = None) → version_id`. The method must: <br>• Serialize the supplied data (JSON‑compatible or binary). <br>• Compute a cryptographic hash (SHA‑256) of the serialized payload. <br>• Store the payload, hash, timestamp, and supplied metadata as an immutable record. | Must |
| **FR‑3** | **Retrieve a specific version** via `get_version(version_id: str) → (data, metadata)`. Must raise a clear error if the version does not exist. | Must |
| **FR‑4** | **List all versions** via `list_versions() → List[dict]` returning version_id, timestamp, and metadata (no payload). | Should |
| **FR‑5** | **Generate an audit trail** via `get_audit_trail() → List[dict]` ordered chronologically, each entry containing: <br>• version_id <br>• operation type (`CREATE`, `UPDATE`, `DELETE`) <br>• actor (optional, from metadata) <br>• timestamp <br>• hash of the payload <br>• hash of the previous version (chain linking). | Must |
| **FR‑6** | **Support immutable deletion** via `tombstone_version(version_id: str, actor: str, reason: str)`. The method must not physically remove data but mark it as deleted and add a deletion entry to the audit trail. | Should |
| **FR‑7** | **Verify integrity** via `verify_chain(start_version_id: str = None) → bool`. The function walks the hash chain and returns `True` only if every stored hash matches the recomputed hash and the previous‑hash links are consistent. | Must |
| **FR‑8** | **Export / import** functionality: <br>• `export(to_path: str, format: Literal['json','csv'])` – dumps the full version history (metadata + hashes, not payload) for external audit. <br>• `import(from_path: str, format: ...)` – restores the audit trail into a new instance, rejecting any record that fails integrity checks. | Should |
| **FR‑9** | **Pluggable storage backends** – the library must expose an abstract `StorageBackend` interface with concrete implementations for: <br>• In‑memory (default, for testing) <br>• Local file system (single‑file SQLite) <br>• PostgreSQL (via SQLAlchemy) | Must |
| **FR‑10** | **Thread‑safe operation** – all public methods must be safe to call from multiple threads/processes when using a concurrent‑capable backend (e.g., PostgreSQL). | Must |
| **FR‑11** | **Unit test suite** – 100 % coverage of public API, including edge cases (duplicate version, missing version, integrity failure). Tests must be runnable with `pytest`. | Must |
| **FR‑12** | **Documentation** – auto‑generated API reference (via Sphinx or MkDocs) and a concise README with usage examples for each backend. | Must |

---

## 3. Non‑Functional Requirements  

| ID | Requirement | Target |
|----|-------------|--------|
| **NFR‑1** | **Performance** – Adding a version must complete in ≤ 15 ms for payloads ≤ 1 MiB (in‑memory backend) and ≤ 50 ms for the same payload size on SQLite. |
| **NFR‑2** | **Scalability** – The system must support at least 10 million version records without degradation of read latency (≤ 30 ms for `get_version`). |
| **NFR‑3** | **Security** – All stored hashes must use SHA‑256. Sensitive metadata (e.g., `actor`) may be optionally encrypted using a user‑provided key (AES‑256‑GCM). |
| **NFR‑4** | **Reliability** – No data loss on graceful shutdown; on crash recovery, the backend must guarantee ACID properties (SQLite/PostgreSQL). |
| **NFR‑5** | **Compliance** – Audit trail must be immutable and tamper‑evident, satisfying HIPAA audit‑log requirements (record‑level integrity, chronological ordering). |
| **NFR‑6** | **Portability** – Library must be pure Python 3.9+ with no compiled extensions, enabling deployment in serverless environments (AWS Lambda, GCP Cloud Functions). |
| **NFR‑7** | **Observability** – Emit structured logs (JSON) for each operation at INFO level, and DEBUG‑level logs for hash calculations. |
| **NFR‑8** | **License** – Distributed under Apache‑2.0 to align with the company’s open‑source policy. |
| **NFR‑9** | **Maintainability** – Code style must follow PEP‑8, with type hints for all public functions. CI pipeline must enforce linting (flake8) and static analysis (mypy). |

---

## 4. Constraints  

1. **Dependency Policy** – Only third‑party packages with permissive licenses (Apache‑2.0, MIT, BSD) may be added. Core dependencies are limited to `sqlalchemy`, `pydantic`, and `cryptography`.  
2. **Storage Size** – Payloads are stored as BLOBs; the library must not impose a hard size limit, but documentation should warn about SQLite file‑size limits (~140 TiB).  
3. **Runtime Environment** – Must run on Linux, macOS, and Windows without OS‑specific code.  
4. **Version Identifier** – Must be a UUID‑v4 string; generated internally and never reused.  

---

## 5. Assumptions  

| ID | Assumption |
|----|------------|
| **A‑1** | Consumers will handle data serialization for non‑JSON‑compatible objects before calling `add_version`. |
| **A‑2** | The calling application is responsible for providing an “actor” identifier (e.g., user ID) via metadata when required. |
| **A‑3** | Network latency is negligible for local backends; remote backends (PostgreSQL) are assumed to be reachable with < 100 ms round‑trip. |
| **A‑4** | Regulatory compliance (HIPAA/GDPR) is addressed at the application layer; `medidata‑vault` only guarantees immutable audit logging and cryptographic integrity. |
| **A‑5** | The library will be used primarily in Python services; cross‑language bindings are out of scope for the initial release. |

---

## 6. Acceptance Criteria  

- All **Must** functional requirements are implemented and pass the automated test suite.  
- Performance benchmarks meet **NFR‑1** on the reference hardware (Intel i7, 16 GB RAM).  
- Documentation builds without errors and includes a “Getting Started” guide for each storage backend.  
- CI pipeline (GitHub Actions) runs linting, type checking, unit tests, and a security scan (bandit) on every PR.  

---  

*Prepared by:* Senior Product/Engineering Lead, Axentx  
*Date:* 2026‑06‑20
