# core/retriever.py
# ==================
# Loads a FAISS vector index for one agent and performs semantic search.
# This is the RAG (Retrieval-Augmented Generation) component.
#
# HOW RAG WORKS HERE:
#   When an agent responds, it first searches its own corpus for the
#   most similar comments to the stimulus. These are injected into the
#   prompt, grounding the agent's response in authentic community language.
#
# Students: you don't need to modify this file.
# To build the indexes, run: python scripts/build_vectorstore.py
