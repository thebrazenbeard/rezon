# Source recovery: untrusted lexical retrieval candidates

The local historical `VERA_RETRIEVAL_ADAPTER_V0.2.2_VALIDATED.zip` includes retrieval-index and embedding-provider concepts. Its private archive is **not** imported into Rezon. The current `rezon` repository instead exposes a strict retrieval **admission** boundary: a relevance result is not evidence and cannot grant source authority.

`rezon.candidate_retrieval.search_untrusted_candidates()` adds a small, standard-library-only exact/lexical fallback. Callers supply bounded in-memory `CandidateDocument(ref, text)` objects plus an explicit source ID/version and query. The function produces a deterministic `RetrievalReceipt` with `admission_status=RETRIEVED_ONLY`; no authority, currentness or verification references are populated. Only overlapping lexical tokens qualify. Ties order by reference. There is no vector search, weight loading, network call, filesystem access, hidden corpus, privacy override, or private-memory import.

Receipt IDs include cryptographic digests of the **selected documents' text**, not only their references. This prevents ordinary false stability when a result's content changes under an unchanged label. It does **not** authenticate the person who supplied the text or establish a trusted source version.

## Bounded behavior and tests

Document collections must be exact tuples of at most 512 exact `CandidateDocument` values; texts are at most 16,384 characters, queries 4,096 characters, and result limits 1–32. Duplicate references, strange subclasses, oversized inputs, and invalid result caps fail closed. The function never creates a canonical Episode evidence proposition.

```bash
python -m pytest -q tests/test_untrusted_candidate_retrieval.py tests/test_retrieval_execution.py
```

On Lappy Windows Python 3.12, fourteen focused and existing retrieval tests passed. The new receipt-content-binding regression was first observed **failing**, then passed after digest binding was added.

> **Hostile challenge:** A lexical-overlap rank is neither semantic correctness nor factual authority. If the source-version string is fabricated, this function cannot detect that. Even exact content digests are substitution checks, not signatures or evaluator custody. Production evidence requires the existing Rezon admission policy and separately qualified source/currentness bindings.

The scanner and selection algorithm are an originally authored, minimal candidate layer inspired by a historical capability gap. The archived adapter, embedding models, generated/private indices and other historical files remain outside GitHub. This source PR does not qualify historical model weights or a live retrieval service.
