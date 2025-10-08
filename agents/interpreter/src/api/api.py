from time import sleep
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import logging
import json

from agent import Agent
from .models import ChatRequest, MessageResponse, ChatResponse

# Create a router instance
router = APIRouter(prefix="/v1", tags=["chat"])

# Initialize logger
logger = logging.getLogger(__name__)

# You can initialize the agent here or inject it as a dependency
agent = Agent(
    base_url="http://localhost:8000/v1",
    api_key="",
)

@router.post("/chat")
def chat(chat_request: ChatRequest):
    """
    Chat endpoint that processes messages and returns responses
    """
    try:
        response = agent.chat(chat_request.messages, stream=chat_request.stream)

        # Handle non-streaming response (MessageResponse object)
        if isinstance(response, MessageResponse):
            return ChatResponse(message=response)
        
        # Handle streaming response
        if hasattr(response, '__iter__') and not isinstance(response, MessageResponse):
            def event_generator():
                total_tokens = 0
                for chunk in response:
                    if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                        delta = chunk.choices[0].delta
                        if hasattr(delta, 'content') and delta.content:
                            # Format as server-sent events
                            yield f"data: {json.dumps({'content': delta.content})}\n\n"
                    
                    # Check for usage information in the final chunk
                    if hasattr(chunk, 'usage') and chunk.usage:
                        total_tokens = chunk.usage.total_tokens
                
                # Send token usage as final event before DONE
                if total_tokens > 0:
                    yield f"{json.dumps({'tokens_used': total_tokens})}\n\n"
                yield f"{json.dumps({'content': '[DONE]'})}\n\n"

            return StreamingResponse(
                event_generator(), 
                media_type="text/plain"
            )

    except Exception as e:
        logger.error(f"Error during chat: {e}")
        raise HTTPException(status_code=500, detail=f"Chat processing error: {str(e)}")

@router.get("/health")
def health_check():
    """
    Health check endpoint
    """
    sleep(11)
    return {"status": "healthy", "model": agent.model.id}

# You can add more routes here
@router.get("/model-info")
def get_model_info():
    """
    Get information about the current model configuration
    """
    return {
        "model_id": agent.model.id,
        "auto_summarize": agent.auto_summarize,
        "summarize_threshold_tokens": agent.summarize_threshold_tokens,
        "max_tokens": agent.max_tokens
    }
