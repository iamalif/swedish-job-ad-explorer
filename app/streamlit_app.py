import streamlit as st
import psycopg2
import pandas as pd
import joblib

st.title("Swedish Data Jobs")
st.write("Explore the Swedish data-job market.")


# --- helper: one place to get a connection ---
def get_connection():
    return psycopg2.connect(
        host="localhost",
        port="5432",
        dbname="jobads",
        user="alif",
    )


# --- load the list of regions for the dropdown (cached) ---
@st.cache_data
def load_regions():
    conn = get_connection()
    df = pd.read_sql(
        "SELECT DISTINCT region FROM jobs WHERE region IS NOT NULL ORDER BY region;",
        conn,
    )
    conn.close()
    return df["region"].tolist()


# --- load field counts, filtered by region (cached per region) ---
@st.cache_data
def load_field_counts(region):
    conn = get_connection()
    query = """
        SELECT occupation_field, COUNT(*) AS listings
        FROM jobs
        WHERE region = %s
        GROUP BY occupation_field
        ORDER BY listings DESC;
    """
    df = pd.read_sql(query, conn, params=(region,))
    conn.close()
    return df


# --- top employers, filtered by region (cached per region) ---
@st.cache_data
def load_top_employers(region):
    conn = get_connection()
    query = """
        SELECT UPPER(employer_name) AS employer, COUNT(*) AS listings
        FROM jobs
        WHERE region = %s AND employer_name IS NOT NULL
        GROUP BY UPPER(employer_name)
        ORDER BY listings DESC
        LIMIT 10;
    """
    df = pd.read_sql(query, conn, params=(region,))
    conn.close()
    return df


# --- monthly trend (whole country, not region-filtered) ---
@st.cache_data
def load_monthly_trend():
    conn = get_connection()
    query = """
        SELECT
            to_char(date_trunc('month', publication_date), 'YYYY-MM') AS month,
            COUNT(*) AS listings
        FROM jobs
        WHERE publication_date IS NOT NULL
        GROUP BY date_trunc('month', publication_date)
        ORDER BY date_trunc('month', publication_date);
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


# --- load the trained model once, cached ---
@st.cache_resource
def load_model():
    return joblib.load("occupation_classifier.joblib")


# --- the filter widget ---
regions = load_regions()
selected_region = st.selectbox("Choose a region", regions)

# --- chart, driven by the selection ---
st.header(f"Demand by occupation field — {selected_region}")
field_counts = load_field_counts(selected_region)
st.bar_chart(field_counts, x="occupation_field", y="listings")

# --- top employers chart ---
st.header(f"Top employers — {selected_region}")
top_employers = load_top_employers(selected_region)
st.bar_chart(top_employers, x="employer", y="listings")

# --- monthly trend (national) ---
st.header("Monthly listing trend (all regions)")
monthly = load_monthly_trend()
st.line_chart(monthly, x="month", y="listings")


# --- model prediction demo ---
st.header("Predict occupation field from a job description")
st.write("Paste a job title and description below, and the model will predict the field.")

user_text = st.text_area("Job text", height=200)

if st.button("Predict field"):
    if user_text.strip() == "":
        st.warning("Please paste some job text first.")
    else:
        model = load_model()
        prediction = model.predict([user_text])[0]
        st.success(f"Predicted occupation field: **{prediction}**")