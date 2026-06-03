import plotly.express as px


def score_distribution_chart(df):
    fig = px.histogram(
        df,
        x="score",
        nbins=20,
        title="Candidate Score Distribution",
    )
    return fig


def top_candidates_chart(df):
    top_10 = df.head(10)

    fig = px.bar(
        top_10,
        x="candidate_id",
        y="score",
        title="Top 10 Candidate Scores",
        text="score",
    )

    fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig.update_layout(xaxis_title="Candidate ID", yaxis_title="Score")

    return fig