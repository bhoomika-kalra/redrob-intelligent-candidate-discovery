import json

with open("data/sample_candidates.json", "r", encoding="utf-8") as f:
    candidates = json.load(f)

print("=" * 50)
print("TOTAL SAMPLE CANDIDATES:", len(candidates))
print("=" * 50)

first = candidates[0]

print("\nCandidate ID:")
print(first["candidate_id"])

print("\nProfile Keys:")
print(first["profile"].keys())

print("\nSkills Count:")
print(len(first["skills"]))

print("\nRedrob Signal Keys:")
print(first["redrob_signals"].keys())