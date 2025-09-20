## Agents Makefile
## Builds the vLLM OpenAI-compatible server image that serves the local model in ../models

.PHONY: help build-model-image

# Configurable variables
IMAGE_NAME ?= pa-agents-vllm
DOCKER ?= docker
# Use the Dockerfile in this folder, but build context needs repo root (one level up)
DOCKERFILE ?= $(CURDIR)/Dockerfile
CONTEXT ?= $(CURDIR)/..
# Additional build args can be passed like: make build-model-image BUILD_ARGS="--build-arg FOO=bar"
BUILD_ARGS ?=

help:
	@echo "Available targets:"
	@echo "  build-model-image  Build the Docker image '$(IMAGE_NAME)' using $(DOCKERFILE) with context $(CONTEXT)"

# Build the Docker image that includes ../models into /models in the container
build-model-image:
	$(DOCKER) build -f $(DOCKERFILE) -t $(IMAGE_NAME) $(BUILD_ARGS) $(CONTEXT)

