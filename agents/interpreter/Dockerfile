# Agents - vLLM OpenAI-compatible server
# Base image: official vLLM server exposing the OpenAI-compatible API
# Docs: https://github.com/vllm-project/vllm

FROM vllm/vllm-openai:latest

# Default model can be overridden at runtime with: docker run ... <image> --model <other>
# Using Microsoft Phi-3 Mini 128k Instruct as requested.

# When building from the repo root (context is one level up), copy models from agents/models

EXPOSE 8000

# Optional: set a default Hugging Face cache path inside the container
# ENV HF_HOME=/root/.cache/huggingface

# Start the vLLM OpenAI server with the requested model and bind to all interfaces.
# The base image defines the entrypoint, so we only provide default args via CMD.
CMD ["--model","microsoft/Phi-3-mini-128k-instruct","--host","0.0.0.0","--port","8000", "--gpu-memory-utilization", "0.5"]
