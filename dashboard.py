import streamlit as st
import pandas as pd
import sqlite3
from scipy.stats import ttest_ind, mannwhitneyu
import plotly.express as px
import tempfile
import os

st.set_page_config(page_title="A/B Test Dashboard", layout="wide")
st.title("🔍 A/B Test Analysis for Search UX")

st.sidebar.markdown("""
### 📘 About This App
This dashboard compares two variants (A and B) from an A/B test, using search-related engagement metrics.

It is designed as a flexible template for experiment-driven teams working on AI-powered products, user experience optimization, or search relevance evaluation.

You can configure the meaning of each variant below:
""")

variant_a_desc = st.sidebar.text_input("Variant A Description", "Control – current experience")
variant_b_desc = st.sidebar.text_input("Variant B Description", "Test – improved LLM format")

@st.cache_data
def load_data_from_db(path):
    conn = sqlite3.connect(path)
    df = pd.read_sql_query("SELECT * FROM ab_test_logs", conn)
    conn.close()
    return df

@st.cache_data
def load_data_from_csv(uploaded_file):
    return pd.read_csv(uploaded_file)

@st.cache_data
def load_data_from_excel(uploaded_file):
    return pd.read_excel(uploaded_file)

@st.cache_data
def load_data_from_parquet(uploaded_file):
    return pd.read_parquet(uploaded_file)

@st.cache_data
def analyze_ab_test(df: pd.DataFrame):
    summary = df.groupby("variant").agg(
        sample_size=("session_id", "count"),
        click_rate=("clicks", "mean"),
        avg_dwell_time=("dwell_time_sec", "mean"),
        feedback_positive_rate=("feedback_score", lambda x: (x > 0).mean())
    ).reset_index()

    variant_a = df[df["variant"] == "A"]
    variant_b = df[df["variant"] == "B"]

    click_test = ttest_ind(variant_a["clicks"], variant_b["clicks"])
    dwell_test = ttest_ind(variant_a["dwell_time_sec"], variant_b["dwell_time_sec"])
    feedback_test = mannwhitneyu((variant_a["feedback_score"] > 0).astype(int),
                                 (variant_b["feedback_score"] > 0).astype(int), alternative="two-sided")

    summary["click_rate_p_value"] = click_test.pvalue
    summary["dwell_time_p_value"] = dwell_test.pvalue
    summary["feedback_score_p_value"] = feedback_test.pvalue

    desc_map = {"A": variant_a_desc, "B": variant_b_desc}
    summary["description"] = summary["variant"].map(desc_map)

    return summary

# File uploader
st.sidebar.subheader("Upload A/B Test Data")
uploaded_db = st.sidebar.file_uploader("SQLite (.db)", type="db")
uploaded_csv = st.sidebar.file_uploader("CSV (.csv)", type="csv")
uploaded_excel = st.sidebar.file_uploader("Excel (.xlsx)", type="xlsx")
uploaded_parquet = st.sidebar.file_uploader("Parquet (.parquet)", type="parquet")

if uploaded_csv is not None:
    df = load_data_from_csv(uploaded_csv)
elif uploaded_excel is not None:
    df = load_data_from_excel(uploaded_excel)
elif uploaded_parquet is not None:
    df = load_data_from_parquet(uploaded_parquet)
elif uploaded_db is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        tmp.write(uploaded_db.read())
        tmp_path = tmp.name
    df = load_data_from_db(tmp_path)
    os.unlink(tmp_path)
else:
    df = load_data_from_db("ab_test_search_logs.db")

st.sidebar.header("Filters")
query_filter = st.sidebar.multiselect("Filter by query", options=sorted(df["query"].unique()), default=None)

if query_filter:
    df = df[df["query"].isin(query_filter)]

summary = analyze_ab_test(df)

st.subheader("Summary Statistics")
st.dataframe(summary.style.format({
    "click_rate": "{:.2%}",
    "avg_dwell_time": "{:.1f} sec",
    "feedback_positive_rate": "{:.2%}",
    "click_rate_p_value": "{:.2e}",
    "dwell_time_p_value": "{:.2e}",
    "feedback_score_p_value": "{:.2e}"
}))

# Interactive Bar Charts
st.subheader("📊 Metric Comparison Between Variants")

fig1 = px.bar(
    summary,
    x="variant",
    y="click_rate",
    color="variant",
    text="description",
    title="Click Rate\nProportion of sessions with at least one click",
    labels={"click_rate": "Proportion"},
    hover_data=["sample_size", "click_rate_p_value"]
)
st.plotly_chart(fig1, use_container_width=True)

fig2 = px.bar(
    summary,
    x="variant",
    y="avg_dwell_time",
    color="variant",
    text="description",
    title="Average Dwell Time\nMean time (in seconds) users spent on the page",
    labels={"avg_dwell_time": "Seconds"},
    hover_data=["sample_size", "dwell_time_p_value"]
)
st.plotly_chart(fig2, use_container_width=True)

fig3 = px.bar(
    summary,
    x="variant",
    y="feedback_positive_rate",
    color="variant",
    text="description",
    title="Positive Feedback Rate\nProportion of sessions with positive feedback score",
    labels={"feedback_positive_rate": "Proportion"},
    hover_data=["sample_size", "feedback_score_p_value"]
)
st.plotly_chart(fig3, use_container_width=True)
