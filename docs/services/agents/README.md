# Agents Service

Language: Python

## Overview

The Agents service hosts multiple AI agents using vLLM for local inference. Each agent focuses on a specific task area (instruction following, browsing/scraping, data pipeline, summarization/analysis). The service communicates with the Manager for scheduling and reporting.

## Agent types (initial set)

- Instruction interpreter agent
- Browsing and scraping agent
- Data pipeline agent (clean, normalize, store)
- Summarization and analysis agent

## Architecture (high level)

- Inference Runtime: vLLM for local model serving (model choice TBD)
- Tooling Integrations: browser/scraper, data transforms, storage adapters
- Agent Router: dispatch per-agent type based on requested capability
- Manager Client: report status, progress, and results
- Storage: intermediate artifacts and outputs (backend TBD)

## Interfaces (TBD)

- Agents ↔ Manager: TBD (REST vs gRPC vs MQ)
- Agents ↔ Storage: TBD (local FS, SQLite/Postgres, object storage)

## Model loading and GPU considerations (TBD)

- Model selection and size vs VRAM (RTX 4060)
- Lazy loading, caching, quantization options
- Per-agent memory budgeting and concurrency limits

## Data formats and persistence (TBD)

- Input/output schemas for each agent
- Storage of structured data (tables), logs, and artifacts

## Configuration (TBD)

- Environment variables for model paths, device selection, concurrency
- Feature flags for tools (browser/scraper, pipeline)

## Runbook (TBD)

- Start the service
- Health checks
- Logs and troubleshooting

## Open questions to resolve (answer here when decided)

1. What APIs do agents expose to the manager?
2. How are models loaded, pinned, and scheduled relative to GPU memory constraints?
3. What data formats and persistence layers are used for intermediate/outputs?
4. What scraping approach and anti-bot strategies are used (if any)?
5. How are failures and retries handled per agent type?

## ADRs and references

- Global ADRs: `docs/adr/`
- Agents ADRs: `docs/services/agents/adr/` (to be added)

## Try it (placeholder)

You can run the OpenAI-compatible vLLM server that serves the local Phi-3 model in two ways:

1. Bake models into the image (current Dockerfile)

- Build the image from the repo root (context includes `agents/models`):

  - make from `agents/` folder: `make build-model-image`
  - or directly from repo root: `docker build -f agents/Dockerfile -t pa-agents-vllm .`

- Run the server (GPU optional):

  - With GPU: `docker run --rm -p 8000:8000 --gpus all --gpu-memory-utilization 0.5 pa-agents-vllm`
  - CPU only: `docker run --rm -p 8000:8000 pa-agents-vllm`

- Test:

  - `curl http://localhost:8000/v1/models`

2. Volume-mount models (avoids a large image)

- Keep models on host and mount into the container:

  - With GPU (standard HF model):

    ```bash
    docker run --rm -p 8000:8000 --gpus all \
      -v C:/Users/krzys/.cache/huggingface:/root/.cache/huggingface \
      pa-agents-vllm \
      --model microsoft/Phi-3.1-mini-128k-instruct \
      --gpu-memory-utilization 0.9 \
      --host 0.0.0.0 --port 8000
    ```

  - With GPU (GGUF model):
    ```bash
    docker run --rm -p 8000:8000 --gpus all -v "C:\Users\krzys\.cache\huggingface\hub\models--dphn--Dolphin3.0-Llama3.1-8B-GGUF\snapshots\be0be5e42b14c7b0052705d146a79a9e9ee8e6eb":/models pa-agents-vllm --model /models/Dolphin3.0-Llama3.1-8B-Q5_0.gguf --gpu-memory-utilization 0.85 --host 0.0.0.0 --port 8000 --max_num_batched_tokens 1024 --max_num_seqs 1 --max_model_len 10240
    ```

- Test the API:
  - List models: `curl http://localhost:8000/v1/models`
  - Chat completion:
    ```bash
    curl -X POST "http://localhost:8000/v1/chat/completions"
      -H "Content-Type: application/json"
      -d '{
        "model": "/models/Phi-3.1-mini-128k-instruct-Q8_0.gguf",
        "messages": [{"role": "user", "content": "What is the capital of France?"}]
      }'
    ```

Notes

- For GGUF models, use the exact model ID returned by `/v1/models` in chat requests
- The default CMD in the image points to `/models/phi-3-mini-128k-instruct`. If you mount a different path or model name, override `--model` accordingly.
- If the server fails to start due to GPU memory, try `--gpu-memory-utilization 0.5` or lower, or run without `--gpus` for CPU.
- API is OpenAI-compatible; supports standard endpoints like `/v1/models` and `/v1/chat/completions`.
