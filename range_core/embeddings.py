"""Ollama embeddings with bounded input and response validation."""

import json
import math
import os
import urllib.request


def embed(texts):
    if not 1 <= len(texts) <= 8 or any(
        not isinstance(t, str) or len(t) > 8000 for t in texts
    ):
        raise ValueError("Embedding input exceeds lab bounds")
    model = os.environ.get("OLLAMA_EMBED_MODEL", "nomic-embed-text:latest")
    payload = {"model": model, "input": texts, "truncate": False}
    url = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
    request = urllib.request.Request(
        url + "/api/embed",
        json.dumps(payload).encode(),
        {"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        result = json.load(response)
    vectors = result.get("embeddings")
    if not isinstance(vectors, list) or len(vectors) != len(texts):
        raise ValueError("Invalid embedding count")
    dimension = len(vectors[0]) if isinstance(vectors[0], list) else 0
    if not 1 <= dimension <= 4096 or any(
        not isinstance(v, list)
        or len(v) != dimension
        or any(type(n) not in (int, float) or not math.isfinite(n) for n in v)
        for v in vectors
    ):
        raise ValueError("Invalid embedding vectors")
    return vectors, {
        "embedding_model": model,
        "dimension": dimension,
        "prompt_eval_count": result.get("prompt_eval_count"),
    }


def cosine(left, right):
    denominator = math.sqrt(sum(x * x for x in left) * sum(x * x for x in right))
    return sum(x * y for x, y in zip(left, right)) / denominator if denominator else 0.0
