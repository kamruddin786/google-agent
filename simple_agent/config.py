"""
Centralized configuration for the agent application.

Change the MODEL_NAME here to switch the LLM model used by all agents.
This avoids having to update multiple files when changing models.

Ollama model examples:
  - "ollama_chat/llama3.1:latest"
  - "ollama_chat/ministral-3:8b"
  - "ollama_chat/llama3.2:1b"
  - "ollama_chat/mistral-nemo:12b"
  - "ollama_chat/qwen2.5:14b"
"""

from google.adk.models.lite_llm import LiteLlm

# ── Change the model name here to switch all agents at once ──
MODEL_NAME = "ollama_chat/ministral-3:8b"

MODEL = LiteLlm(model=MODEL_NAME)
