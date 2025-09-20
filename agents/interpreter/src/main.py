from openai import OpenAI, Stream
from openai.types.chat import ChatCompletionChunk

openai_api_base = "http://localhost:8000/v1"

def stream_response(stream: Stream[ChatCompletionChunk]) -> str:
  print("Client: Start streaming chat completion...")
  printed_reasoning_content = False
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


def main():
  client = OpenAI(
    api_key="",
    base_url=openai_api_base
  )

  models = client.models.list()
  model = models.data[0].id

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

    stream = client.chat.completions.create(model=model, messages=messages, stream=True)
    response = stream_response(stream)
    messages.append({"role": "assistant", "content": response})

    print(f"\n{messages}")

  

if __name__ == "__main__":
  main()