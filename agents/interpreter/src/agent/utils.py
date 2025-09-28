import tiktoken
from openai.types.model import Model

def get_safe_encoding(model: Model) -> tiktoken.Encoding:
  # Handle both string model names and Model objects
  if isinstance(model, Model):
    model_name = model.id
  else:
    model_name = model
    
  try:
    encoding = tiktoken.encoding_for_model(model_name)
  except KeyError:
    encoding = tiktoken.get_encoding("cl100k_base")
  return encoding