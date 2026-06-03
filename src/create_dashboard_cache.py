import json
import pandas as pd

from load_candidates import load_candidates

SUBMISSION_PATH = "outputs/final_submission.csv"
CACHE_PATH = "outputs/dashboard_candidates.json"


def main():
    df = pd.read_csv(SUBMISSION_PATH)
    required_ids = set(df["candidate_id"].tolist())

    candidate_map = {}

    for candidate in load_candidates():
        candidate_id = candidate["candidate_id"]

        if candidate_id in required_ids:
            candidate_map[candidate_id] = candidate

        if len(candidate_map) == len(required_ids):
            break

    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(candidate_map, f, ensure_ascii=False, indent=2)

    print(f"Saved dashboard cache: {CACHE_PATH}")
    print(f"Candidates saved: {len(candidate_map)}")


if __name__ == "__main__":
    main()