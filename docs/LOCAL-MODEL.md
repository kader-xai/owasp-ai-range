# Local-model demonstration

## Small default
Qwen2.5:1.5b, Q4_K_M quantization, approximately 986 MB model download.
Model size is not total RAM use: runtime and context require additional memory.
Start with this small model on CPU; native Ollama can use Apple Metal on supported
Macs. The development Mac is Apple Silicon with 48 GiB RAM. No paid API required.
Sources: https://ollama.com/library/qwen2.5:1.5b and https://docs.ollama.com/gpu

There is no additional guardrail service in this range. This model still has its
own training and may reject instructions. We do not label it uncensored or claim
zero guardrails. Harmless task redirection is sufficient to teach the failure.

## Native setup
Install Python 3.12+ and Ollama, then run from the repository:

```sh
bash scripts/start-local.sh
```

Open http://127.0.0.1:8088, choose **Real local model · Ollama**, and check readiness.
To use an already running service manually:

```sh
ollama pull qwen2.5:1.5b
OLLAMA_MODEL=qwen2.5:1.5b python3 app.py
```

## All-in-Docker, CPU mode
Install and start Docker, then:

```sh
docker compose -f compose.local-model.yaml up --build -d
docker compose -f compose.local-model.yaml logs -f model-setup
```

The model-setup service downloads the model before the app starts. Subsequent runs
reuse a named volume. Ollama has no published port; only the app is exposed on
localhost. This configuration uses CPU and can be slower than native Metal on Mac.
Linux GPU setup needs platform-specific devices/toolkit configuration; see
https://docs.ollama.com/docker rather than assuming GPU access.
Stop without removing downloaded models:

```sh
docker compose -f compose.local-model.yaml down
```

Alternatively `docker compose up --build -d` runs just the app against host Ollama.
The host.docker.internal setting targets Docker Desktop; Linux needs explicit
host-gateway configuration. Both Compose files default to the same small model.

## Real experiment
With Ollama running and the model downloaded:

```sh
python3 scripts/test-local-model.py
```

Six runs compare baseline and two benign injected documents in both modes. The
output contains timestamp, model, inputs, answers, and traces. Export browser
attempts too. This is not an attack-success-rate benchmark. Marker presence is a
narrow challenge condition; review whether it replaced or merely contaminated
the answer. Marker absence does not prove security.

Defended mode removes the document entirely for the policy-only task. It is an
application boundary, not a claim that prompting or model alignment solves injection.

## Scope and troubleshooting
- If port 8088 is occupied, stop the other range instance or set PORT to another port.
- If Ollama is unavailable, start `ollama serve`; use Check model connection.
- If inference fails, inspect Ollama logs and model availability with `ollama list`.
- First inference may be slower while loading weights. No external tools execute.
- This text-only model cannot read images. A genuine vision-model/image lab is a
  separate planned scenario, not silently simulated OCR.
- Agent frameworks are not needed for LLM01. Add an isolated local tool adapter
  when implementing excessive agency; never connect real customer accounts here.
- Local use only. Do not expose either service to the public Internet.
