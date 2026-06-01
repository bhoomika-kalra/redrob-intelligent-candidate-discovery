import os
import pandas as pd

SUBMISSION_PATH = "outputs/final_submission.csv"

REQUIRED_COLUMNS = [
    "candidate_id",
    "rank",
    "score",
    "reasoning"
]


def validate_submission():
    errors = []

    if not os.path.exists(SUBMISSION_PATH):
        errors.append("Submission file does not exist.")
        return errors

    df = pd.read_csv(SUBMISSION_PATH)

    if list(df.columns) != REQUIRED_COLUMNS:
        errors.append(
            f"Columns must be exactly {REQUIRED_COLUMNS}, but got {list(df.columns)}"
        )

    if len(df) != 100:
        errors.append(f"Submission must contain exactly 100 rows, but got {len(df)}")

    expected_ranks = list(range(1, 101))
    actual_ranks = df["rank"].tolist()

    if actual_ranks != expected_ranks:
        errors.append("Ranks must be exactly 1 to 100 in order.")

    if df["candidate_id"].duplicated().any():
        errors.append("Duplicate candidate IDs found.")

    scores = df["score"].tolist()
    for i in range(len(scores) - 1):
        if scores[i] < scores[i + 1]:
            errors.append("Scores must be monotonically non-increasing.")
            break

    if df["reasoning"].isnull().any():
        errors.append("Some reasoning values are missing.")

    empty_reasoning = df["reasoning"].astype(str).str.strip().eq("")
    if empty_reasoning.any():
        errors.append("Some reasoning values are empty.")

    return errors


if __name__ == "__main__":
    validation_errors = validate_submission()

    if not validation_errors:
        print("✅ Submission validation passed successfully.")
        print("File is ready:", SUBMISSION_PATH)
    else:
        print("❌ Submission validation failed:")
        for error in validation_errors:
            print("-", error)