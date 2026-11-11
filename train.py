import psycopg2
import pandas as pd

conn = psycopg2.connect(
    host="localhost",
    port="5432",
    dbname="jobads",
    user="alif",
)

query = """
    SELECT
        headline,
        description,
        occupation_field
    FROM jobs
    WHERE occupation_field IS NOT NULL
      AND description IS NOT NULL;
"""

df = pd.read_sql(query, conn)

conn.close()

print("Shape:", df.shape)
print()
print("First few rows:")
print(df.head())
print()
print("Label distribution:")
print(df["occupation_field"].value_counts())

# --- combine headline + description into one text field ---
df["text"] = df["headline"].fillna("") + " " + df["description"].fillna("")

# --- drop rare classes (fewer than 10 examples) ---
counts = df["occupation_field"].value_counts()
keep_fields = counts[counts >= 10].index
df = df[df["occupation_field"].isin(keep_fields)]

print("Shape after dropping rare classes:", df.shape)
print("Classes kept:", len(keep_fields))

from sklearn.model_selection import train_test_split

X = df["text"]                # the input: combined ad text
y = df["occupation_field"]    # the label: what we predict

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,            # 20% held back for testing
    random_state=42,          # reproducibility
    stratify=y,               # preserve class proportions in both splits
)

print("Training examples:", len(X_train))
print("Test examples:", len(X_test))

from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score

# --- the dumb baseline: always predict the most frequent class ---
dummy = DummyClassifier(strategy="most_frequent")
dummy.fit(X_train, y_train)

dummy_preds = dummy.predict(X_test)
dummy_acc = accuracy_score(y_test, dummy_preds)

print("Baseline accuracy (always predict most common):", round(dummy_acc, 3))

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

# --- build the pipeline: TF-IDF then logistic regression ---
model = Pipeline([
    ("tfidf", TfidfVectorizer(max_features=5000, ngram_range=(1, 2))),
    ("clf", LogisticRegression(max_iter=1000, class_weight="balanced")),
])

# --- train it ---
model.fit(X_train, y_train)

# --- predict on the held-back test set ---
preds = model.predict(X_test)

# --- score it against the baseline ---
acc = accuracy_score(y_test, preds)
print("Model accuracy:", round(acc, 3))
print("Baseline accuracy:", round(dummy_acc, 3))

from sklearn.metrics import classification_report

print(classification_report(y_test, preds))

import joblib

joblib.dump(model, "occupation_classifier.joblib")
print("Model saved to occupation_classifier.joblib")