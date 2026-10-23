import sqlite3
import unittest
from range_core.store import WorkspaceStore
from labs.registry import WORKFLOWS, execute
from labs import supply, poisoning, output, agency, prompt, retrieval, claims, budget


class DomainWorkflows(unittest.TestCase):
    def setUp(self):
        self.store = WorkspaceStore()
        self.token = self.store.create()

    def tearDown(self):
        self.store.close()

    def run_case(
        self, module, mode="vulnerable", sample="example", backend=None, generator=None
    ):
        d = module.DEFINITION
        revision = self.store.attachment(self.token, d[sample])
        data = {
            "lab": d["id"],
            "revision": revision,
            "mode": mode,
            "backend": backend or d["backends"][0],
        }
        return module.run(self.store, self.token, data, generator=generator)

    def test_all_registered(self):
        self.assertEqual(len(WORKFLOWS), 10)

    def test_supply_dependency_activation(self):
        self.assertTrue(self.run_case(supply)["attack_observed"])
        self.assertFalse(
            self.run_case(supply, "defended")["observation"]["activation_applied"]
        )
        self.assertTrue(
            self.run_case(supply, "defended", "baseline")["observation"][
                "activation_applied"
            ]
        )
        self.assertEqual(len(self.store.events(self.token, "LLM03:2025")), 3)

    def test_corpus_review_and_quarantine(self):
        self.assertTrue(self.run_case(poisoning)["observation"]["active"])
        self.assertFalse(self.run_case(poisoning, "defended")["observation"]["active"])
        self.assertEqual(
            self.store.events(self.token, "LLM04:2025")[0]["payload"]["status"],
            "quarantined",
        )

    def test_publication_encoding(self):
        weak = self.run_case(output)
        strong = self.run_case(output, "defended")
        self.assertIn("<h1>", weak["preview_html"])
        self.assertIn("&lt;h1&gt;", strong["preview_html"])
        self.assertTrue(weak["attack_observed"])
        self.assertFalse(strong["attack_observed"])

    def test_stripped_markup_is_not_reported_as_interpreted(self):
        revision = self.store.attachment(self.token, "<script>fictional</script>")
        result = output.run(
            self.store,
            self.token,
            {
                "lab": "LLM05:2025",
                "revision": revision,
                "mode": "vulnerable",
                "backend": "offline",
            },
        )
        self.assertEqual(result["preview_html"], "fictional")
        self.assertFalse(result["observation"]["formatting_interpreted"])

    def test_agent_plan_is_not_authorization(self):
        generate = lambda *a, **k: ('{"action":"send","text":"Synthetic send"}', {})
        self.assertTrue(
            self.run_case(agency, backend="ollama", generator=generate)[
                "attack_observed"
            ]
        )
        self.assertFalse(
            self.run_case(agency, "defended", backend="ollama", generator=generate)[
                "attack_observed"
            ]
        )
        outbox = [
            e for e in self.store.events(self.token) if e["kind"] == "local-outbox"
        ]
        self.assertEqual(len(outbox), 1)

    def test_preview_never_creates_agent_effect(self):
        self.run_case(agency)
        self.assertEqual(self.store.events(self.token), [])

    def test_private_label_not_submitted_when_defended(self):
        contexts = []

        def generate(system, *a, **k):
            contexts.append(system)
            return system, {}

        self.assertTrue(
            self.run_case(prompt, backend="ollama", generator=generate)[
                "attack_observed"
            ]
        )
        self.assertFalse(
            self.run_case(prompt, "defended", backend="ollama", generator=generate)[
                "attack_observed"
            ]
        )
        self.assertNotIn("ROUTE-", contexts[1])

    def test_sparse_retrieval_has_real_owner_boundary(self):
        self.assertTrue(
            self.run_case(retrieval)["observation"]["unauthorized_retrieval"]
        )
        self.assertFalse(
            self.run_case(retrieval, "defended")["observation"][
                "unauthorized_retrieval"
            ]
        )

    def test_neural_embedding_adapter_and_permissions(self):
        calls = []

        def embedder(texts):
            calls.append(texts)
            return [[1.0, 0.0]] + [
                [1.0, 0.0] if "B-202" in t else [0.0, 1.0] for t in texts[1:]
            ], {"embedding_model": "test-neural"}

        gen = lambda *a, **k: ("Unavailable", {})
        revision = self.store.attachment(self.token, "billing")
        for mode in ("vulnerable", "defended"):
            result = retrieval.run(
                self.store,
                self.token,
                {
                    "lab": "LLM08:2025",
                    "revision": revision,
                    "mode": mode,
                    "backend": "ollama",
                },
                gen,
                embedder,
            )
            self.assertEqual(
                result["observation"]["unauthorized_retrieval"], mode == "vulnerable"
            )
        self.assertNotIn("B-202", "".join(calls[1]))

    def test_claim_registry_and_publication(self):
        self.assertTrue(self.run_case(claims)["attack_observed"])
        self.assertFalse(self.run_case(claims, "defended")["observation"]["published"])
        self.assertTrue(
            self.run_case(claims, "defended", "baseline")["observation"]["published"]
        )

    def test_cumulative_quota(self):
        for _ in range(8):
            self.assertTrue(
                self.run_case(budget, "defended", "baseline")["observation"]["admitted"]
            )
        self.assertFalse(
            self.run_case(budget, "defended", "baseline")["observation"]["admitted"]
        )
        self.assertTrue(
            self.run_case(budget, "vulnerable", "baseline")["attack_observed"]
        )

    def test_large_plan_hard_caps(self):
        calls = []

        def generate(*a, **k):
            calls.append(k)
            return "Hello", {}

        r = self.run_case(budget, backend="ollama", generator=generate)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["tokens"], 200)
        self.assertEqual(r["observation"]["actual_model_calls"], 1)

    def test_events_and_attempt_roll_back_together(self):
        self.store.connection.execute(
            "CREATE TRIGGER fail_attempt2 BEFORE INSERT ON attempts BEGIN SELECT RAISE(ABORT,'test'); END"
        )
        with self.assertRaises(sqlite3.IntegrityError):
            self.run_case(supply)
        self.assertEqual(self.store.events(self.token), [])

    def test_event_isolation(self):
        self.run_case(supply)
        other = self.store.create()
        self.assertEqual(self.store.events(other), [])

    def test_unknown_workflow_rejected(self):
        with self.assertRaises(ValueError):
            execute("LLM99", self.store, self.token, {})

    def test_baselines_survive_defended_non_model_paths(self):
        for module in (supply, poisoning, output, retrieval, claims, budget):
            result = self.run_case(module, "defended", "baseline")
            self.assertFalse(result["attack_observed"], module.DEFINITION["id"])

    def test_wrong_value_with_real_source_is_unsupported(self):
        revision = self.store.attachment(self.token, '{"days":47,"source":"policy-v1"}')
        result = claims.run(
            self.store,
            self.token,
            {
                "lab": "LLM09:2025",
                "revision": revision,
                "mode": "defended",
                "backend": "offline",
            },
        )
        self.assertFalse(result["observation"]["published"])

    def test_invalid_inputs_do_not_create_effects(self):
        for module in (supply, budget):
            revision = self.store.attachment(self.token, '{"unexpected":true}')
            with self.assertRaises(ValueError):
                module.run(
                    self.store,
                    self.token,
                    {
                        "lab": module.DEFINITION["id"],
                        "revision": revision,
                        "mode": "vulnerable",
                        "backend": "offline",
                    },
                )
        self.assertEqual(self.store.events(self.token), [])
