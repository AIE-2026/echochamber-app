# core/retriever.py
# =================
# Semantic retrieval over a FAISS vector store.
#
# Acest fișier NU folosește un LLM generativ.
# El face doar partea de retrieval:
#
#   interogare text → embedding interogare → căutare FAISS → top-k fragmente
#
# LLM-ul apare abia în C6, în core/agent.py, unde aceste fragmente vor fi
# introduse într-un prompt pentru a genera răspunsul agentului.

# Exemplu python -m core.retriever --agent anti_sistem --query "CCR a decis anularea alegerilor după suspiciuni privind influențe externe." --k 5
from pathlib import Path
import argparse
import pickle

import faiss
from sentence_transformers import SentenceTransformer


# Modelul de embeddings folosit și în C5 la construirea indexului.
# Este important ca același model să fie folosit și la căutare.
# Dacă indexul a fost construit cu MiniLM, și interogarea trebuie transformată
# în embedding tot cu MiniLM.
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


# Folderul unde sunt salvate vectorstore-urile create în C5.
# Structura așteptată este:
#
# assets/vectorstores/
#   anti_sistem/
#     index.faiss
#     index.pkl
#   conspirationist/
#     index.faiss
#     index.pkl
#   pro_european/
#     index.faiss
#     index.pkl
VECTORSTORE_DIR = Path("assets/vectorstores")


class Retriever:
    """
    Retriever pentru o singură bulă / un singur agent.

    Exemplu:
        retriever = Retriever("anti_sistem")
        chunks = retriever.search("CCR a decis anularea alegerilor", k=5)

    Ce încarcă:
        index.faiss = indexul numeric FAISS, adică vectorii textelor
        index.pkl   = metadatele, adică textele originale + informații asociate

    Ce face:
        primește o interogare nouă,
        o transformă în embedding,
        caută în FAISS cele mai apropiate texte,
        returnează fragmentele găsite împreună cu scorurile.
    """

    def __init__(self, agent_slug: str):
        """
        Inițializează retriever-ul pentru un agent.

        agent_slug este numele folderului din assets/vectorstores/.
        Exemplu:
            agent_slug = "anti_sistem"

        Atunci retriever-ul caută aici:
            assets/vectorstores/anti_sistem/index.faiss
            assets/vectorstores/anti_sistem/index.pkl
        """

        self.agent_slug = agent_slug
        self.path = VECTORSTORE_DIR / agent_slug

        index_path = self.path / "index.faiss"
        metadata_path = self.path / "index.pkl"

        # Verificăm dacă există indexul FAISS.
        # Fără acest fișier nu avem vectorii în care să căutăm.
        if not index_path.exists():
            raise FileNotFoundError(f"Missing FAISS index: {index_path}")

        # Verificăm dacă există metadatele.
        # Fără acest fișier FAISS poate returna poziții numerice,
        # dar noi nu putem recupera textul original.
        if not metadata_path.exists():
            raise FileNotFoundError(f"Missing metadata file: {metadata_path}")

        # Încărcăm indexul FAISS.
        # Acesta conține vectorii embedding ai textelor din bula selectată.
        self.index = faiss.read_index(str(index_path))

        # Încărcăm metadatele.
        # metadata[i] corespunde vectorului i din FAISS.
        # Dacă FAISS returnează poziția 12, textul este în metadata[12].
        with open(metadata_path, "rb") as f:
            self.metadata = pickle.load(f)

        # Încărcăm modelul de embeddings.
        # Acesta transformă interogarea nouă într-un vector numeric.
        self.model = SentenceTransformer(MODEL_NAME)

    def search(self, query: str, k: int = 5) -> list[dict]:
        """
        Caută cele mai apropiate k fragmente față de interogare.

        Parametri:
            query:
                textul nou introdus de utilizator;
                exemplu: "CCR a decis anularea alegerilor..."

            k:
                câte fragmente vrem să recuperăm;
                exemplu: k=5 returnează cele mai apropiate 5 texte.

        Returnează:
            o listă de dicționare.
            Fiecare dicționar conține:
                - textul original
                - metadatele lui
                - score = scorul de similaritate
                - position = poziția în indexul FAISS
        """

        # 1. Transformăm interogarea în embedding.
        #
        # Dacă textele din corpus au fost transformate în vectori,
        # și interogarea trebuie transformată în același tip de vector.
        #
        # normalize_embeddings=True înseamnă că vectorul are lungime 1.
        # Pentru că folosim IndexFlatIP, scorul devine echivalent cu
        # similaritatea cosinus.
        query_vector = self.model.encode(
            [query],
            normalize_embeddings=True,
            show_progress_bar=False
        ).astype("float32")

        # 2. Căutăm în FAISS cele mai apropiate k texte.
        #
        # scores = scorurile de similaritate
        # positions = pozițiile vectorilor găsiți în index
        #
        # Exemplu:
        # scores    = [[0.82, 0.75, 0.70]]
        # positions = [[12, 4, 31]]
        #
        # Înseamnă:
        # textul de la metadata[12] este cel mai apropiat,
        # textul de la metadata[4] este al doilea,
        # textul de la metadata[31] este al treilea.
        scores, positions = self.index.search(query_vector, k)

        results = []

        # 3. Transformăm pozițiile FAISS în texte citibile.
        #
        # FAISS nu returnează textul direct.
        # Returnează doar poziția vectorului.
        # Noi folosim poziția ca să luăm textul din metadata.
        for score, pos in zip(scores[0], positions[0]):
            if pos == -1:
                continue

            # Copiem metadatele textului găsit.
            # Folosim copy() ca să nu modificăm obiectul original din metadata.
            item = self.metadata[int(pos)].copy()

            # Adăugăm scorul de similaritate.
            item["score"] = float(score)

            # Adăugăm poziția în index.
            # Aceasta arată legătura dintre FAISS și metadata.
            item["position"] = int(pos)

            results.append(item)

        return results

    def format_for_prompt(self, chunks: list[dict]) -> str:
        """
        Transformă fragmentele recuperate într-un bloc de context.

        În C5 doar testăm retrieval-ul.
        În C6 acest context va fi introdus în promptul LLM-ului.

        Exemplu output:

        [Fragment 1 | score=0.812]
        text recuperat...

        [Fragment 2 | score=0.744]
        alt text recuperat...
        """

        if not chunks:
            return "(Nu au fost găsite fragmente relevante.)"

        lines = []

        for i, chunk in enumerate(chunks, start=1):
            lines.append(
                f'[Fragment {i} | score={chunk["score"]:.3f}]\n{chunk["text"]}'
            )

        return "\n\n".join(lines)


def main():
    """
    Funcție pentru testare direct din terminal.

    Exemplu comandă:

        python -m core.retriever --agent anti_sistem --query "CCR a decis anularea alegerilor..." --k 5

    Această parte este utilă în C5 pentru a verifica rapid dacă retriever-ul funcționează.
    """

    parser = argparse.ArgumentParser(
        description="Test semantic retrieval for one agent bubble."
    )

    # Agentul / bula în care căutăm.
    # Trebuie să existe folderul:
    # assets/vectorstores/<agent_slug>/
    parser.add_argument(
        "--agent",
        required=True,
        help="Agent slug, for example: anti_sistem"
    )

    # Interogarea semantică.
    # Este textul nou pe baza căruia căutăm fragmente similare.
    parser.add_argument(
        "--query",
        required=True,
        help="Text used as semantic search query"
    )

    # Numărul de rezultate returnate.
    # k=5 înseamnă top-5 fragmente.
    parser.add_argument(
        "--k",
        type=int,
        default=5,
        help="Number of retrieved fragments"
    )

    args = parser.parse_args()

    # Inițializăm retriever-ul pentru bula aleasă.
    retriever = Retriever(args.agent)

    # Rulăm căutarea semantică.
    chunks = retriever.search(args.query, k=args.k)

    # Afișăm informații generale.
    print("Agent:", args.agent)
    print("Interogare:", args.query)
    print("Vectori în index:", retriever.index.ntotal)
    print("Rezultate recuperate:", len(chunks))

    # Afișăm rezultatele într-o formă ușor de citit.
    for i, chunk in enumerate(chunks, start=1):
        print(f"\nRezultat {i}")
        print("Poziție:", chunk["position"])
        print("Scor:", round(chunk["score"], 3))

        # Aceste câmpuri apar doar dacă există în metadata.
        # Nu toate corpusurile au neapărat aceleași metadate.
        if "agent" in chunk:
            print("Agent text:", chunk["agent"])

        if "source_channel" in chunk:
            print("Sursă:", chunk["source_channel"])

        if "video_title" in chunk:
            print("Video:", chunk["video_title"])

        print("Text:", chunk["text"][:500])


if __name__ == "__main__":
    main()