# collector/filter_relevant.py
# =============================
# Filters raw collected comments to keep only those relevant to the topic.
# Uses a simple keyword list or an LLM call for classification.
# Input:  data/raw/comments.jsonl
# Output: data/raw/comments_filtered.jsonl
#
# HOW TO USE:
#   python collector/filter_relevant.py --in data/raw/comments.jsonl --out data/raw/filtered.jsonl
#
# TODO: implement filtering logic
