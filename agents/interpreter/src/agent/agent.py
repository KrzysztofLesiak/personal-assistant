"""Agent utilities and an `Agent` class for interacting with OpenAI compatible chat APIs.

This module originally exposed a set of free functions. They are still available for
backward compatibility, but typical usage should now go through `Agent` which wraps:

  * Streaming vs. non‑streaming chat completions
  * Optional automatic conversation summarisation when token usage grows
  * Token counting helpers (approximate, OpenAI-format heuristic)

Example:

    from agent import Agent

    agent = Agent(model="gpt-4o-mini")
    messages = [
        {"role": "system", "content": "You are helpful."},
        {"role": "user", "content": "Explain recursion in one sentence."}
    ]
    reply = agent.chat(messages)
    print("Agent reply:\n", reply)

    # Streaming
    agent.chat(messages, stream=True)

The summarisation logic replaces the running context with a concise system message
containing the summary once the total token estimate exceeds a threshold.
"""
import logging
from typing import Optional
from openai import OpenAI, Stream
from openai.types.chat import ChatCompletionChunk
from openai.types.model import Model

from agent.utils import get_safe_encoding
from api.models import MessageResponse

# Get logger - will use the colored formatter configured in main.py
logger = logging.getLogger(__name__)

openai_api_base = "http://localhost:8000/v1"
MODEL = "/models/Dolphin3.0-Llama3.1-8B-Q5_0.gguf"

class Agent:
  """High-level chat agent wrapper.

  Parameters
  ----------
  model: str
      Model name to use.
  base_url: str
      Base URL for OpenAI-compatible endpoint. Defaults to local server.
  api_key: Optional[str]
      API key (can be omitted for locally hosted inference servers).
  auto_summarize: bool
      If True, automatically summarize when token threshold exceeded.
  summarize_threshold_tokens: int
      Trigger summarization when estimated tokens in context exceed this.
  verbose: bool
      If True, prints diagnostic information (token counts, summary events).
  """

  def __init__(
    self,
    base_url: str = openai_api_base,
    api_key: Optional[str] = None,
    auto_summarize: bool = True,
    summarize_threshold_tokens: int = 4000,
    verbose: bool = True,
  ) -> None:
    self.client = OpenAI(base_url=base_url, api_key=api_key)
    self.model = self._get_model()
    self.auto_summarize = auto_summarize
    self.summarize_threshold_tokens = summarize_threshold_tokens
    self.verbose = verbose
    self.max_tokens = self.model.model_dump()["max_model_len"] or None

  def _get_model(self) -> Model:
    model = self.client.models.list().data[0]
    if model is None:
      raise ValueError("No model found from the client.")
    
    return model

  # ---------------------------- Utility methods ---------------------------
  def token_usage(self, messages: list[dict]) -> int:
    encoding = get_safe_encoding(self.model)
    num_tokens = 0
    for message in messages:
      num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
      for key, value in message.items():
        # We only expect string values here.
        if not isinstance(value, str):
          value = str(value)
        num_tokens += len(encoding.encode(value))
        if key == "name":  # if there's a name, the role is omitted
          num_tokens += -1  # role is always required and always 1 token
    num_tokens += 2  # every reply is primed with <im_start>assistant
    return num_tokens
  
  def _summarize_context(self, messages: list[dict], client: OpenAI, model: str) -> list[dict]:
    """Return a new messages list with a conversation summary as system context."""
    logger.info("Summarizing context...")
    response = client.chat.completions.create(
      model=model,
      messages=[
        {"role": "system", "content": "You are a helpful assistant that summarizes conversations."},
        {"role": "user", "content": f"Summarize the following conversation between a user and an AI assistant in a concise manner:\n\n{messages}"}
      ],
    )
    summary = response.choices[0].message.content
    new_messages = [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "system", "content": summary},
    ]
    logger.info(f"Summary: {summary}")
    if getattr(response, "usage", None):  # Some servers may omit usage
      logger.info(f"Token usage: {response.usage.total_tokens}")
    return new_messages 
  
  def _summarize(self, messages: list[dict]) -> list[dict]:
    if not self.auto_summarize:
      return messages
    tokens = self.token_usage(messages)
    if tokens < self.summarize_threshold_tokens:
      return messages
    if self.verbose:
      logger.info(f"[Agent] Context tokens {tokens} >= {self.summarize_threshold_tokens}; summarizing...")
    return self._summarize_context(messages, self.client, self.model.id)

  def _stream_response(self, stream: Stream[ChatCompletionChunk]) -> str:
    """Consume a streaming ChatCompletion and echo tokens to stdout.

    Returns the concatenated content string.
    """
    logger.info("Client: Start streaming chat completion...")
    printed_content = False
    content_parts: list[str] = []
    for chunk in stream:
      content = chunk.choices[0].delta.content or None
      if content is not None:
        if not printed_content:
          printed_content = True
          print(f"\nAgent (content):", end="", flush=True)
        content_parts.append(content)
        print(content, end="", flush=True)
    return "".join(content_parts)  

  # ---------------------------- Chat methods ------------------------------
  def chat(self, messages: list[dict], stream: bool = False, summarize: Optional[bool] = None) -> Stream[ChatCompletionChunk] | str:
    """Send chat completion request.

    If stream is True, tokens are printed progressively (stdout) and final text
    is returned.
    If summarize is explicitly provided it overrides auto_summarize for that call.
    """

    logger.info(f"[Agent] Chat called with {len(messages)} messages. Token estimate: {self.token_usage(messages)}")
    # messages = messages.insert(0, {"role": "system", "content": "You are a helpful assistant."})
    messages = [{"role": "system", "content": "You are a helpful assistant."}] + messages
    logger.debug(f"Messages: {messages}")

    if summarize is True or self.auto_summarize:
      messages = self._summarize(messages)

    if stream:
      completion_stream = self.client.chat.completions.create(
        model=self.model.id,
        messages=messages,
        stream=True,
        stream_options={"include_usage": True}
      )
      return completion_stream
    else:
      response = self.client.chat.completions.create(
        model=self.model.id,
        messages=messages,
      )
      text = response.choices[0].message.content or ""
      if self.verbose and getattr(response, "usage", None):
        logger.info(f"[Agent] Prompt tokens: {response.usage.prompt_tokens} | Completion tokens: {response.usage.completion_tokens} | Total: {response.usage.total_tokens}")
      
      logger.info(f"Agent (content): {text}")
      return MessageResponse(content=text, tokens_used=response.usage.total_tokens if getattr(response, "usage", None) else -1)