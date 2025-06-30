import streamlit as st
import pandas as pd
import sqlite3
from scipy.stats import ttest_ind, mannwhitneyu
import matplotlib.pyplot as plt
import tempfile
import os

st.set_page_config(page_title="A/B Test Dashboard", layout="wide")
st.title("🔍 A/B Test Analysis for Search UX")

@st.cache_data
def load_data_from_db(path):
    conn = sqlite3.connect(path)
    df = pd.read_sql_query("SELECT * FROM ab_test_logs", conn)
    conn.close()
    return df

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

    return summary

# File uploader
uploaded_file = st.sidebar.file_uploader("Upload SQLite DB", type="db")

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        tmp.write(uploaded_file.read())
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

# Add bar charts
st.subheader("📊 Metric Comparison Between Variants")
col1, col2, col3 = st.columns(3)

with col1:
    fig1, ax1 = plt.subplots()
    ax1.bar(summary["variant"], summary["click_rate"], color="skyblue")
    ax1.set_title("Click Rate")
    ax1.set_ylabel("Proportion")
    st.pyplot(fig1)

with col2:
    fig2, ax2 = plt.subplots()
    ax2.bar(summary["variant"], summary["avg_dwell_time"], color="salmon")
    ax2.set_title("Average Dwell Time")
    ax2.set_ylabel("Seconds")
    st.pyplot(fig2)

with col3:
    fig3, ax3 = plt.subplots()
    ax3.bar(summary["variant"], summary["feedback_positive_rate"], color="lightgreen")
    ax3.set_title("Positive Feedback Rate")
    ax3.set_ylabel("Proportion")
    st.pyplot(fig3)
