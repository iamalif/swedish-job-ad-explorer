# Swedish Job-Ad Explorer

A personal data project combining Python, PostgreSQL, SQL analysis and Streamlit to explore Swedish job advertisements retrieved through the JobTech JobSearch API. A text-classification pipeline predicts an advertisement's occupation field from its headline and description.

The project connects data ingestion, relational storage, analytical queries, machine learning and an interactive interface in one local workflow.

## What it includes

- Paginated API ingestion using the search term `data`.
- PostgreSQL storage for advertisement text, employer details, occupation taxonomy, geography and publication dates.
- SQL analysis of occupation fields, employers, regions and municipalities.
- Common table expressions and window functions for monthly comparisons and ranking occupation fields within regions.
- Data-completeness queries for key fields.
- A TF-IDF and logistic-regression classifier with a majority-class baseline.
- A Streamlit interface with regional charts and an occupation-prediction demonstration.

## Workflow

```text
JobTech JobSearch API
        |
     ingest.py
        |
PostgreSQL: jobads / jobs
        |
        +--- src/analysis.sql: analytical queries
        |
        +--- train.py: baseline, evaluation and saved classifier
        |
        +--- app/streamlit_app.py: charts and text predictions
```

## Interface

The Streamlit application provides:

- A region selector.
- Advertisement counts by occupation field for the selected region.
- The selected region's top employers, normalising employer-name casing.
- A monthly publication-date chart across all regions in the stored dataset.
- A text box for predicting an occupation field from a pasted title and description.

The monthly chart is not filtered by the region selector.

## Files

| Path | Purpose |
|---|---|
| `explore.py` | Inspect a small API response and write a local `sample.json` |
| `ingest.py` | Fetch search results and insert advertisements into PostgreSQL |
| `schema.sql` | Table definition extracted unchanged from the original SQL session |
| `src/analysis.sql` | Curated analytical queries |
| `jobads.session.sql` | Original schema and exploratory SQL session |
| `train.py` | Prepare text, split data, evaluate and save the classifier |
| `occupation_classifier.joblib` | Existing model artifact from the original local work |
| `app/streamlit_app.py` | Interactive charts and prediction interface |
| `requirements.txt` | Python dependencies identified from the source imports |

## Local setup

### 1. Python dependencies

Create and activate a Python 3 virtual environment, then install:

```bash
python -m pip install -r requirements.txt
```

### 2. PostgreSQL

The existing code expects PostgreSQL at `localhost:5432`, a database named `jobads` and a role named `alif`. These settings appear in `ingest.py`, `train.py` and `app/streamlit_app.py`.

Set up a local database and role with the required permissions, or adapt those connection arguments to your own environment. Authentication must be configured locally. The source does not read connection settings from a `.env` file.

In an empty `jobads` database, run the table definition in `schema.sql`. With the PostgreSQL command-line client and matching local connection settings:

```bash
psql -h localhost -p 5432 -U alif -d jobads -f schema.sql
```

The statement creates the `jobs` table and is intended for initial setup, not repeated execution against an existing table.

### 3. Populate the database

From the repository root:

```bash
python ingest.py
```

The script searches for `data`, fetches batches of advertisements and inserts rows. Duplicate advertisement IDs are skipped. Existing rows are not refreshed by this conflict-handling strategy.

### 4. Train in your environment

```bash
python train.py
```

Training prints the class distribution, split sizes, baseline accuracy, model accuracy and classification report, then writes `occupation_classifier.joblib` in the current directory. The dataset must contain enough eligible examples for the stratified split.

The included model preserves the original local artifact. Its original dependency versions are not recorded, so retraining provides an artifact matched to your installed environment. No new evaluation scores are claimed here.

### 5. Open the interface

Run from the repository root so the model's relative path resolves correctly:

```bash
streamlit run app/streamlit_app.py
```

The dashboard requires a populated local database. The saved model alone does not provide the data for its charts.

## Classification approach

`train.py` combines each advertisement's headline and description, excludes occupation fields with fewer than 10 examples and uses an 80/20 stratified train/test split with `random_state=42`.

The pipeline contains TF-IDF features with unigrams and bigrams, a maximum of 5,000 features, and logistic regression with balanced class weights. It compares holdout accuracy with a most-frequent-class baseline and prints per-class precision, recall and F1 scores.

This is a random advertisement-level split, not a temporal or employer-grouped evaluation. Similar advertisements may share language across partitions. The classifier predicts the source occupation taxonomy; it does not assess applicant suitability or recommend hiring decisions.

## Interpreting the data

The search term `data` defines a keyword-selected sample, not a comprehensive or manually verified census of Swedish data-science jobs. Charts count advertisements, not the number of vacancies within each advertisement.

A snapshot of available advertisements does not establish historical hiring growth. Older listings can disappear, and repeated ingestion skips existing IDs rather than maintaining a complete history of updates and removals. Employer-name normalisation merges casing differences but is not full entity resolution.

## Status and attribution

Published from the existing local project, with the Python implementation, analytical SQL and saved model preserved unchanged. Documentation, a dependency list and a separate copy of the schema were added for navigation and setup. No project execution or fresh end-to-end validation was performed during publication preparation.

The full local database and raw API-response sample are not bundled. Advertisement content and taxonomy originate from JobTech and the underlying publishers. This repository claims the project implementation, not authorship of the advertisements.

## Skills demonstrated

Python, PostgreSQL, SQL, API ingestion, relational data modelling, data-quality checks, CTEs, window functions, pandas, scikit-learn, TF-IDF, text classification and Streamlit.
