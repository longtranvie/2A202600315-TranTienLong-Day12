"""
Mock LLM - no real API key needed.
Simulates an LLM response for testing deployment concepts.
"""
import time
import random


MOCK_RESPONSES = {
    "default": [
        "This is a mock AI agent response. In production, this would come from OpenAI/Anthropic.",
        "Agent is running well! (mock response) Ask another question.",
        "I am an AI agent deployed on the cloud. Your question was received.",
    ],
    "docker": ["A container packages an app so it runs anywhere. Build once, run anywhere!"],
    "deploy": ["Deployment is the process of bringing code from your machine to a server."],
    "health": ["Agent is operating normally. All systems operational."],
    "hello": ["Hello! I'm a production AI agent. How can I help you today?"],
}


def ask(question: str, delay: float = 0.1) -> str:
    """Mock LLM call with simulated latency."""
    time.sleep(delay + random.uniform(0, 0.05))

    question_lower = question.lower()
    for keyword, responses in MOCK_RESPONSES.items():
        if keyword in question_lower:
            return random.choice(responses)

    return random.choice(MOCK_RESPONSES["default"])


def ask_stream(question: str):
    """Mock streaming response - yield each word."""
    response = ask(question)
    for word in response.split():
        time.sleep(0.05)
        yield word + " "
