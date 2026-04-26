# scripts/clean_corpus.py
# ========================
# Cleans and standardizes raw collected comments.
# Input:  data/raw/*.jsonl
# Output: data/cleaned/corpus.jsonl
#
# Cleaning steps applied:
#   1. Remove duplicates (exact text match)
#   2. Remove comments shorter than MIN_LENGTH characters
#   3. Strip URLs, HTML tags, excessive whitespace
#   4. Normalize encoding (UTF-8)
#   5. Add a unique ID if missing
#
# HOW TO USE:
#   python scripts/clean_corpus.py --in data/raw/comments.jsonl --out data/cleaned/corpus.jsonl
