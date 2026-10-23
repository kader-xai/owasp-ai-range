"""Record real local-model workflow cases; never assume an attack must succeed.

No model download and no external tool calls. Default output is JSON Lines on
stdout. --output creates a new evidence file and refuses to overwrite one.
"""

import argparse
import http.cookiejar
import json
from datetime import datetime, timezone
from urllib.parse import urlsplit
import urllib.request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8088")
    parser.add_argument(
        "--labs", nargs="+", choices=[f"LLM{i:02d}" for i in range(1, 11)]
    )
    parser.add_argument(
        "--samples",
        nargs="+",
        choices=["baseline", "example"],
        default=["baseline", "example"],
    )
    parser.add_argument(
        "--output", help="New JSONL file; existing files are not overwritten"
    )
    args = parser.parse_args()
    parsed = urlsplit(args.base_url)
    if (
        parsed.scheme != "http"
        or parsed.hostname not in ("127.0.0.1", "localhost", "::1")
        or parsed.username
        or parsed.password
        or parsed.path not in ("", "/")
        or parsed.query
        or parsed.fragment
    ):
        parser.error("Only a local HTTP range origin is supported")
    base = args.base_url.rstrip("/")
    client = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar())
    )

    def api(path, data=None):
        request = urllib.request.Request(
            base + "/api/" + path,
            None if data is None else json.dumps(data).encode(),
            {} if data is None else {"Content-Type": "application/json"},
        )
        with client.open(request, timeout=120) as response:
            return json.load(response)

    definitions = api("workflows")
    selected = [
        d for d in definitions if not args.labs or d["id"].split(":")[0] in args.labs
    ]
    output = open(args.output, "x", encoding="utf-8") if args.output else None
    errors = 0
    try:
        for definition in selected:
            lab = definition["id"]
            for sample in args.samples:
                # Fresh initial state for each variant, especially cumulative quota.
                # Fixture content is identical; workspace-private fields may differ.
                for mode in ("vulnerable", "defended"):
                    record = {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "lab": lab,
                        "sample": sample,
                        "mode": mode,
                        "claim_boundary": "Single real-model case; not a benchmark or guaranteed attack success.",
                    }
                    try:
                        api("support/start", {})
                        payload = {"lab": lab, "mode": mode, "backend": "ollama"}
                        if lab == "LLM02:2025":
                            payload.update(definition["request_examples"][sample])
                            record["fixture"] = definition["request_examples"][sample]
                        else:
                            fixture = definition[sample]
                            payload["revision"] = api(
                                "workflows/attachment", {"content": fixture}
                            )["revision"]
                            record["fixture"] = fixture
                        record["result"] = api("workflows/run", payload)
                    except Exception as error:
                        errors += 1
                        record["error"] = str(error)
                    line = json.dumps(record, ensure_ascii=False)
                    print(line, flush=True)
                    if output:
                        output.write(line + "\n")
                        output.flush()
    finally:
        if output:
            output.close()
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()
