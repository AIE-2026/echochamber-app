# core/agent.py
# ==============
# The Agent class. Each agent:
#   1. Reads its persona from roles.yaml (via config.py)
#   2. Retrieves similar comments from its corpus (RAG via retriever.py)
#   3. Calls the LLM with its system prompt + retrieved context + stimulus
#
# Students: you don't need to modify this file.
# Your work is in assets/roles/roles.yaml — that's where you define the persona.
