# scripts/build_vectorstore.py
# =============================
# Builds a FAISS vector index for each agent from data/bubbles/.
# Each agent gets its own index in assets/vectorstores/<slug>/
#
# HOW TO USE:
#   python scripts/build_vectorstore.py
#
# Prerequisites:
#   - data/bubbles/<slug>.jsonl exists for each agent defined in roles.yaml
#   - Each line in the JSONL has a "text" field
#
# Output:
#   assets/vectorstores/<slug>/index.faiss
#   assets/vectorstores/<slug>/index.pkl
