"""Adapter validation; no network or model download in unit tests."""

import io
import json
import unittest
from unittest.mock import patch
from range_core.embeddings import embed, cosine


class EmbeddingTests(unittest.TestCase):
    def response(self, vectors):
        return io.BytesIO(json.dumps({"embeddings": vectors}).encode())

    def test_real_request_contract(self):
        with patch(
            "urllib.request.urlopen", return_value=self.response([[1, 0], [0, 1]])
        ) as request:
            vectors, metadata = embed(["query", "record"])
        payload = json.loads(request.call_args.args[0].data)
        self.assertEqual(payload["input"], ["query", "record"])
        self.assertFalse(payload["truncate"])
        self.assertTrue(request.call_args.args[0].full_url.endswith("/api/embed"))
        self.assertEqual(metadata["dimension"], 2)
        self.assertEqual(cosine(*vectors), 0)

    def test_input_bounds(self):
        for texts in ([], ["a"] * 9, ["a" * 8001], [None]):
            with self.assertRaises(ValueError):
                embed(texts)

    def test_invalid_vectors(self):
        for vectors in ([], [[1]], [[1], [1, 2]], [[float("nan")], [0]], [[True], [0]]):
            with patch("urllib.request.urlopen", return_value=self.response(vectors)):
                with self.assertRaises(ValueError):
                    embed(["query", "record"])

    def test_zero_vector_has_zero_similarity(self):
        self.assertEqual(cosine([0, 0], [1, 1]), 0)
