"""Bounded lexical candidate lookup, never evidence admission.

This independent, source-only recovery experiment shares no old archive code,
model weights, private memory, network transport or authority assertions.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import re

from .receipts import AdmissionStatus, RetrievalReceipt

MAX_DOCUMENTS = 512
MAX_TEXT_CHARS = 16384
MAX_QUERY_CHARS = 4096
MAX_RESULTS = 32


def _exact_text(value: str, field: str, limit: int) -> str:
    if type(value) is not str or not value:
        raise ValueError(field + " must be a nonempty exact str")
    if len(value) > limit:
        raise ValueError(field + " too long")
    return value


def _tokens(text: str) -> frozenset[str]:
    return frozenset(re.findall(r"[^\W_]+", text.casefold()))


@dataclass(frozen=True, slots=True)
class CandidateDocument:
    ref: str
    text: str

    def __post_init__(self) -> None:
        _exact_text(self.ref, "ref", 512)
        _exact_text(self.text, "text", MAX_TEXT_CHARS)


def search_untrusted_candidates(
    query: str, *, source_id: str, source_version: str,
    documents: tuple[CandidateDocument, ...], max_results: int = 5,
) -> RetrievalReceipt:
    """Rank local lexical overlaps without granting provenance or authority.

    The returned receipt is always RETRIEVED_ONLY. Other Rezon components must
    perform their normal independent evidence admission before any promotion.
    """
    query = _exact_text(query, "query", MAX_QUERY_CHARS)
    source_id = _exact_text(source_id, "source_id", 512)
    source_version = _exact_text(source_version, "source_version", 512)
    if type(documents) is not tuple or len(documents) > MAX_DOCUMENTS:
        raise ValueError("documents must be a bounded exact tuple")
    if type(max_results) is not int or not 1 <= max_results <= MAX_RESULTS:
        raise ValueError("max_results outside supported bound")
    references: set[str] = set()
    ranked: list[tuple[int, str, str]] = []
    terms = _tokens(query)
    for doc in documents:
        if type(doc) is not CandidateDocument:
            raise ValueError("documents must be exact CandidateDocument instances")
        # Frozen dataclass construction is not a validation boundary:
        # object.__setattr__ can replace fields after __post_init__.
        ref = _exact_text(doc.ref, "ref", 512)
        content = _exact_text(doc.text, "text", MAX_TEXT_CHARS)
        if ref in references:
            raise ValueError("duplicate document reference")
        references.add(ref)
        score = len(terms & _tokens(content))
        if score:
            ranked.append((score, ref, sha256(content.encode('utf-8')).hexdigest()))
    ranked.sort(key=lambda pair: (-pair[0], pair[1]))
    hits = tuple(ref for _score, ref, _digest in ranked[:max_results])
    selected_bindings = tuple((ref, digest) for _score, ref, digest in ranked[:max_results])
    binding = json.dumps(
        [query, source_id, source_version, selected_bindings], ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    retrieval_id = "lexical-candidate:" + sha256(binding).hexdigest()
    return RetrievalReceipt(
        retrieval_id=retrieval_id, query=query, source_id=source_id,
        source_version=source_version, method="untrusted_lexical_candidates",
        returned_refs=hits, admission_status=AdmissionStatus.RETRIEVED_ONLY,
    )
