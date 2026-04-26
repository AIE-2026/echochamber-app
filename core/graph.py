# core/graph.py
# ==============
# LangGraph orchestration for the agentic debate (Tab 3).
#
# HOW THE DEBATE WORKS:
#   This is NOT a fixed round-robin. After each message, a "router" LLM call
#   decides who speaks next based on the thread content. Agents address each
#   other directly by @handle, agree or disagree with previous messages.
#
#   Flow:
#     START → [router] → [agent_X] → [router] → [agent_Y] → ... → END
#
#   The router picks the next agent based on who was just challenged,
#   who hasn't spoken recently, or who has the strongest reaction to give.
#
# Students: you don't need to modify this file.
