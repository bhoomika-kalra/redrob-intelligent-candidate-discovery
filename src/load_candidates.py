import json
from tqdm import tqdm

DATA_PATH = "data/candidates.jsonl"


def load_candidates(limit=None):
    candidates = []

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        for i, line in enumerate(tqdm(f, desc="Loading candidates")):
            if limit and i >= limit:
                break

            if line.strip():
                candidates.append(json.loads(line))

    return candidates


if __name__ == "__main__":
    candidates = load_candidates(limit=1000)
    print(f"\nLoaded {len(candidates)} candidates")
    print("First candidate:", candidates[0]["candidate_id"])