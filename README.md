# A/B Test Dashboard

This Streamlit dashboard analyzes A/B testing results for a search engine UX scenario, simulating click-through rates, dwell time, and feedback scores between two variants (A and B).

## Features
- Upload a SQLite database of user session logs
- View summary statistics and significance testing
- Interactive charts (click rate, dwell time, feedback)
- Query-level filtering

## Running Locally

1. Clone the repo
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the app:
   ```
   streamlit run dashboard.py
   ```

You can upload your own `.db` file with a table named `ab_test_logs` or use the included sample.
