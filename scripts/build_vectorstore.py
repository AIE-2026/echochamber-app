# scripts/build_vectorstore.py
# =============================
# Builds a FAISS vector index for each agent from data/bubbles/.
# Each agent gets its own index in assets/vectorstores/<slug>/
#
# HOW TO USE:
#   python scripts/build_vectorstore.py

from pathlib import Path
import pickle
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer

BUBBLES_DIR = Path("data/bubbles")
VECTOR_DIR = Path("assets/vectorstores")
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

VECTOR_DIR.mkdir(parents=True, exist_ok=True)

model = SentenceTransformer(MODEL_NAME)

for bubble_path in sorted(BUBBLES_DIR.glob("*.jsonl")):
    slug = bubble_path.stem
    df = pd.read_json(bubble_path, lines=True)

    df = df[df["text"].fillna("").str.strip() != ""].copy()
    if df.empty:
        print(f"{slug}: skipped, no texts")
        continue

    texts = df["text"].tolist()

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True
    ).astype("float32")

    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)

    out_dir = VECTOR_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    faiss.write_index(index, str(out_dir / "index.faiss"))

    with open(out_dir / "index.pkl", "wb") as f:
        pickle.dump(df.to_dict(orient="records"), f)

    print(f"{slug}: {len(texts)} texte -> {out_dir}")

print("Gata. Vectorstore-urile au fost create.")