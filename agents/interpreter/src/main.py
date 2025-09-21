from time import sleep
from openai import APIConnectionError, OpenAI, Stream
from openai.types.chat import ChatCompletionChunk
import tiktoken

openai_api_base = "http://localhost:8000/v1"

def stream_response(stream: Stream[ChatCompletionChunk]) -> str:
  print("Client: Start streaming chat completion...")
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


def summarize_context(messages: list[dict], client: OpenAI, model: str) -> str:
  print("\n\nSummarizing context...")
  response = client.chat.completions.create(
    model=model,
    messages=[
      {"role": "system", "content": "You are a helpful assistant that summarizes conversations."},
      {"role": "user", "content": f"Summarize the following conversation between a user and an AI assistant in a concise manner:\n\n{messages}"}
    ],
  )

  summary = response.choices[0].message.content

  messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "system", "content": summary }
  ]

  print(f"\n\nSummary: {summary}")
  print("Token usage:", response.usage.total_tokens)

  return messages


def get_safe_encoding(model: str):
  try:
    encoding = tiktoken.encoding_for_model(model)
  except KeyError:
    print("Model not found. Using cl100k_base encoding.")
    encoding = tiktoken.get_encoding("cl100k_base")
  return encoding


def calculate_token_count(messages: list[dict], model: str) -> int:
  encoding = get_safe_encoding(model)
  num_tokens = 0
  for message in messages:
    num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
    for key, value in message.items():
      num_tokens += len(encoding.encode(value))
      if key == "name":  # if there's a name, the role is omitted
        num_tokens += -1  # role is always required and always 1 token
  num_tokens += 2  # every reply is primed with <im_start>assistant
  return num_tokens


def main():
  client = OpenAI(
    api_key="",
    base_url=openai_api_base
  )
  
  models = client.models.list()
  model = models.data[0].id
  max_tokens = models.data[0].max_model_len or None

  print(f"Using model: {model} with max tokens: {max_tokens}")

  first_message = True
  messages = []

  while True:
    user_input = input("\nUser: ")
    if user_input.lower() in ["exit", "quit"]:
      break

    if first_message:
      first_message = False
      messages.append({"role": "system", "content": "You are a helpful assistant"})

    messages.append({"role": "user", "content": user_input})

    token_count = calculate_token_count(messages, model)
    print(f"\nToken count: {token_count}")

    if max_tokens is not None and token_count > max_tokens - 1024:
      messages = summarize_context(messages, client, model)
      token_count = calculate_token_count(messages, model)

    stream = client.chat.completions.create(model=model, messages=messages, stream=True)
    response = stream_response(stream)

    print(stream.usage.total_tokens)

    messages.append({"role": "assistant", "content": response})
    print(f"\n{messages}")


if __name__ == "__main__":
  while True:
    try:
      main()
    except APIConnectionError as e:
      print(f"Error: {e.request}. Retrying in 5 seconds...")
      sleep(5)
    except Exception as e:
      break