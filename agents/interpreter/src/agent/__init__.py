"""Agent package public API.

Typical usage:

    from agent import Agent

    agent = Agent(model="gpt-4o-mini")
    messages = [
        {"role": "system", "content": "You are helpful."},
        {"role": "user", "content": "Hello!"}
    ]
    print(agent.chat(messages))

The legacy helper functions remain importable:

    from agent import calculate_token_count, summarize_context
"""
from .agent import (
    Agent,
)

__all__ = [
    "Agent",
]
