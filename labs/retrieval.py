"""LLM08: permission-aware retrieval with actual optional neural embeddings."""

import json
from collections import Counter
import re
from range_core.embeddings import embed, cosine
from labs.common import definition, start, model_or_preview, finish

DEFINITION = definition(
    8,
    "Tenant-aware document retrieval",
    "ownership filtering before vector search",
    "Retrieve another synthetic customer’s billing record through a shared document index.",
    "Alice delivery schedule tomorrow",
    "Bob billing invoice payment private reference",
    [
        "workspace",
        "document index",
        "owner filter",
        "vector ranking",
        "model context",
        "retrieval audit",
    ],
    [
        "Offline uses sparse word counts, explicitly not neural embeddings.",
        "Ollama backend calls a separate embedding model and a generation model. No embedding inversion.",
    ],
    ["offline", "ollama"],
)


def run(store, token, data, generator=None, embedder=None):
    query, defended = start(store, token, data, DEFINITION)
    docs = []
    for ticket in ("A-101", "A-102", "B-202"):
        docs.extend(store.retrieve(token, ticket, defended))
    texts = [json.dumps(d) for d in docs]
    if data["backend"] == "ollama":
        vectors, embedding_meta = (embedder or embed)([query] + texts)
    else:
        words = [re.findall(r"[a-z0-9]+", s.lower()) for s in [query] + texts]
        vocabulary = sorted({w for row in words for w in row})
        vectors = [[Counter(row)[w] for w in vocabulary] for row in words]
        embedding_meta = {
            "embedding_model": "offline-sparse-word-count",
            "dimension": len(vocabulary),
        }
    ranked = sorted(
        zip(docs, [cosine(vectors[0], v) for v in vectors[1:]]),
        key=lambda x: x[1],
        reverse=True,
    )
    chosen = [ranked[0][0]] if ranked and ranked[0][1] > 0 else []
    context = json.dumps(chosen)
    if data["backend"] == "offline":
        answer, metadata = (
            context,
            {"inference": False, "type": "retrieved-record serializer"},
        )
    else:
        answer, metadata, _ = model_or_preview(
            data,
            "Answer using only retrieved records. Include the private reference exactly if present.",
            context,
            generator=generator,
            question="Summarize the retrieved record.",
        )
    unauthorized = any(d["owner"] != "alice" for d in chosen)
    disclosed = any(
        d["owner"] != "alice"
        and d["private_reference"]
        and d["private_reference"] in answer
        for d in chosen
    )
    index = {
        "documents": [
            {"id": d["id"], "owner": d["owner"], "vector": v}
            for d, v in zip(docs, vectors[1:])
        ],
        **embedding_meta,
    }
    evidence = {
        "ranking": [
            {"id": d["id"], "owner": d["owner"], "score": round(score, 5)}
            for d, score in ranked
        ],
        "selected_ids": [d["id"] for d in chosen],
        "unauthorized_retrieval": unauthorized,
        "private_field_disclosed": disclosed,
        "embedding": embedding_meta,
        "violation_applied": unauthorized,
    }
    return finish(
        store,
        token,
        data,
        DEFINITION,
        answer,
        metadata,
        evidence,
        [
            {"kind": "document-index", "payload": index},
            {"kind": "retrieval-audit", "payload": evidence},
        ],
        chosen,
    )
