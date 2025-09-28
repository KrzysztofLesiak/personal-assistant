## Agents Makefile
## Builds the vLLM OpenAI-compatible server image that serves the local model in ../models

.PHONY: help build-model-image

# Configurable variables
IMAGE_NAME ?= pa-agents-vllm
# Use the Dockerfile in this folder, but build context needs repo root (one level up)
DOCKERFILE ?= $(CURDIR)/agents/interpreter/Dockerfile
CONTEXT ?= $(CURDIR)/agents/interpreter/
# Additional build args can be passed like: make build-model-image BUILD_ARGS="--build-arg FOO=bar"
BUILD_ARGS ?=

help:
	@echo "Available targets:"
	@echo "  build-model-image  Build the Docker image '$(IMAGE_NAME)'"
	@echo "  start-model        Run the Docker container with the model server. Configurable via environment variables:"
	@echo "                     MODEL - model filename in /models (default: Dolphin3.0-Llama3.1-8B-Q5_0.gguf)"
	@echo "                     PORT - port to expose the model server (default: 8000)"
	@echo "                     HOST - host to bind the model server (default: 0.0.0.0)"
	@echo "                     VOLUME_PATH - host path to the models directory"
	@echo "                     MAX_NUM_BATCHED_TOKENS - max tokens to batch (default: 1024)"
	@echo "                     MAX_NUM_SEQS - max sequences to process in parallel (default: 1)"
	@echo "                     MAX_MODEL_LEN - max model length (default: 8192)"
	@echo "                     GPU_MEMORY_UTILIZATION - fraction of GPU memory to use (default: 0.85)"
	@echo "  start-interpreter  Start the interpreter agent server on port 8181"

# Build the Docker image that includes ../models into /models in the container
build-model-image:
	docker build -f $(DOCKERFILE) -t $(IMAGE_NAME) $(BUILD_ARGS) $(CONTEXT)


VOLUME_PATH="C:\Users\krzys\.cache\huggingface\hub\models--dphn--Dolphin3.0-Llama3.1-8B-GGUF\snapshots\be0be5e42b14c7b0052705d146a79a9e9ee8e6eb"
MODEL=Dolphin3.0-Llama3.1-8B-Q5_0.gguf
HOST=0.0.0.0
PORT=8000
MAX_NUM_BATCHED_TOKENS=1024
MAX_NUM_SEQS=1
MAX_MODEL_LEN=8192
GPU_MEMORY_UTILIZATION=0.85
start-model:	
	docker run --rm \
		-p $(PORT):$(PORT) \
		--gpus all \
		-v $(VOLUME_PATH):/models \
		$(IMAGE_NAME) \
		--model /models/$(MODEL) \
		--gpu-memory-utilization $(GPU_MEMORY_UTILIZATION) \
		--host $(HOST) \
		--port $(PORT) \
		--max_num_batched_tokens $(MAX_NUM_BATCHED_TOKENS) \
		--max_num_seqs $(MAX_NUM_SEQS) \
		--max_model_len $(MAX_MODEL_LEN)


start-interpreter:
	cd .\agents\interpreter\ && \
	.\.venv\Scripts\Activate.ps1 && \
	uvicorn main:app --host 0.0.0.0 --port 8181 --reload --no-access-log

