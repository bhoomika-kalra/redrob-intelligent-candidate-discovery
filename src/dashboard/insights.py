def get_fit_label(score):
    if score >= 75:
        return "Strong Fit"
    if score >= 50:
        return "Good Fit"
    return "Needs Review"


def build_recruiter_insights(df):
    insights = {}

    insights["strong_fit_count"] = len(df[df["score"] >= 75])
    insights["good_fit_count"] = len(df[(df["score"] >= 50) & (df["score"] < 75)])
    insights["review_count"] = len(df[df["score"] < 50])

    insights["top_candidate"] = df.iloc[0]["candidate_id"]
    insights["top_score"] = round(df.iloc[0]["score"], 2)

    return insights