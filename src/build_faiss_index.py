import faiss
import numpy as np
import os

EMBEDDINGS_PATH = "outputs/candidate_embeddings.npy"
INDEX_PATH = "outputs/faiss_index.index"


def main():
    print("Loading embeddings...")
    embeddings = np.load(EMBEDDINGS_PATH).astype("float32")

    print("Embeddings shape:", embeddings.shape)

    dimension = embeddings.shape[1]

    print("Building FAISS index...")
    index = faiss.IndexFlatIP(dimension)

    index.add(embeddings)

    os.makedirs("outputs", exist_ok=True)

    faiss.write_index(index, INDEX_PATH)

    print("FAISS index built successfully.")
    print("Total vectors:", index.ntotal)
    print("Saved:", INDEX_PATH)


if __name__ == "__main__":
    main()