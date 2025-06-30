# A/B Test Dashboard

This Streamlit app allows you to upload and analyze A/B test results for search UX experiments.

It is designed for reusability across different experiments by supporting dynamic configuration of variant descriptions and interpreting behavioral metrics like:

- **Click Rate**
- **Dwell Time**
- **Positive Feedback Rate**

---

## 🚀 Features

- 📊 Compare engagement metrics between control and test groups (A vs B)
- 📁 Upload custom `.db` files with a table named `ab_test_logs`
- 📝 **Configure what Variant A and B represent** via sidebar inputs
- 📈 Interactive charts + statistical testing
- 🔎 Filter by search query
- 🧪 See significance with auto-calculated p-values

---

## 🧠 Ideal Use Cases

- LLM output testing (prompt rewrites, summary formats)
- Ranking model experiments (search re-ranking, filtering)
- Interface UX adjustments (snippets, result layout)

---

## 🧰 How to Run Locally

1. Clone the repo:

```bash
git clone https://github.com/<your-username>/ab_test_dashboard.git
cd ab_test_dashboard
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
streamlit run dashboard.py
```

---

## 🗂 Database Format

The SQLite file should contain a table named `ab_test_logs` with columns:

| Column Name         | Type     | Description                                 |
|---------------------|----------|---------------------------------------------|
| user_id             | string   | Unique user identifier                      |
| session_id          | string   | Unique session identifier                   |
| query               | string   | User search query                           |
| variant             | A/B      | Experiment variant                          |
| timestamp           | datetime | When session occurred                       |
| clicks              | 0/1      | Whether a result was clicked                |
| dwell_time_sec      | float    | Time user spent viewing results             |
| follow_up_query     | bool     | Whether user refined or continued the query |
| feedback_score      | -1/0/1   | Rating signal (bad/neutral/good)            |

---

## 📦 Deployment

You can deploy this directly to [Streamlit Community Cloud](https://streamlit.io/cloud):

- Set `dashboard.py` as the main file
- Include `requirements.txt`
- (Optional) Upload `ab_test_search_logs.db` for demo

---

## 📬 Feedback

This dashboard is designed as a flexible template for experiment-driven teams working on AI-powered products, user experience optimization, or search relevance evaluation.

Feel free to fork and customize it further!

