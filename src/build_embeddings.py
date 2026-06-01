import os
import json
import numpy as np
from tqdm import tqdm
from sentence_transformers import SentenceTransformer

from load_candidates import load_candidates
from build_candidate_text import build_candidate_text


OUTPUT_DIR = "outputs"
EMBEDDINGS_PATH = "outputs/candidate_embeddings.npy"
IDS_PATH = "outputs/candidate_ids.json"


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Loading model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    print("Loading candidates...")
    candidates = load_candidates(limit=5000)

    candidate_ids = []
    candidate_texts = []

    for candidate in candidates:
        candidate_ids.append(candidate["candidate_id"])
        candidate_texts.append(build_candidate_text(candidate))

    print("Generating embeddings...")

    embeddings = model.encode(
        candidate_texts,
        batch_size=64,
        show_progress_bar=True,
        normalize_embeddings=True
    )

    embeddings = np.array(embeddings, dtype="float32")

    np.save(EMBEDDINGS_PATH, embeddings)

    with open(IDS_PATH, "w", encoding="utf-8") as f:
        json.dump(candidate_ids, f)

    print("\nDone.")
    print("Embeddings shape:", embeddings.shape)
    print("Saved:", EMBEDDINGS_PATH)
    print("Saved:", IDS_PATH)


if __name__ == "__main__":
    main()