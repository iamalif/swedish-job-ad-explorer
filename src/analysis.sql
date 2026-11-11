-- =====================================================================
-- analysis.sql — Swedish Job-Market Data Pipeline (Project 1)
--
-- Curated analysis queries for the `jobs` table in PostgreSQL (db: jobads).
-- These double as (a) the backend for the Streamlit app and
-- (b) portfolio evidence of the analysis layer.
--
-- Notes / decisions baked in:
--   * employer_name is free-text and carries casing-duplicates
--     (e.g. "ACADEMIC WORK SWEDEN AB" vs "Academic Work Sweden AB").
--     We normalise with UPPER() at query time so variants merge.
--     (Source data left untouched — clean on read, not on store.)
--   * ~6.5% of ads lack municipality; no clustering found on inspection,
--     so geographic queries exclude NULLs rather than impute them.
--   * Monthly trend likely reflects survivorship bias in the open-ads
--     snapshot (older ads have closed), not pure hiring growth.
-- =====================================================================


-- ---------------------------------------------------------------------
-- 1. Demand by occupation field
--    Q: Which occupation fields have the most listings overall?
--    (occupation_field is taxonomy-sourced and clean; 0 nulls.)
-- ---------------------------------------------------------------------
SELECT
    occupation_field,
    COUNT(*) AS listings
FROM jobs
GROUP BY occupation_field
ORDER BY listings DESC;


-- ---------------------------------------------------------------------
-- 2. Demand by occupation field, within a chosen region
--    Q: Within one region, how is demand split across fields?
--    (Region is passed as a parameter by the app; example uses Stockholm.)
-- ---------------------------------------------------------------------
SELECT
    occupation_field,
    COUNT(*) AS listings
FROM jobs
WHERE region = 'Stockholms län'
GROUP BY occupation_field
ORDER BY listings DESC;


-- ---------------------------------------------------------------------
-- 3. Top 10 employers (case-normalised)
--    Q: Who is hiring most? UPPER() merges spelling-case duplicates so
--       the ranking is not fragmented across variant spellings.
-- ---------------------------------------------------------------------
SELECT
    UPPER(employer_name) AS employer,
    COUNT(*) AS listings
FROM jobs
WHERE employer_name IS NOT NULL
GROUP BY UPPER(employer_name)
ORDER BY listings DESC
LIMIT 10;


-- ---------------------------------------------------------------------
-- 4. Top 10 employers within a chosen region (case-normalised)
--    Q: Who hires most in a specific region?
-- ---------------------------------------------------------------------
SELECT
    UPPER(employer_name) AS employer,
    COUNT(*) AS listings
FROM jobs
WHERE region = 'Stockholms län'
  AND employer_name IS NOT NULL
GROUP BY UPPER(employer_name)
ORDER BY listings DESC
LIMIT 10;


-- ---------------------------------------------------------------------
-- 5. Hiring by region
--    Q: Where are the listings concentrated geographically?
--    (Excludes NULL municipality/region per the documented decision.)
-- ---------------------------------------------------------------------
SELECT
    region,
    COUNT(*) AS listings
FROM jobs
WHERE region IS NOT NULL
GROUP BY region
ORDER BY listings DESC;


-- ---------------------------------------------------------------------
-- 6. Top hiring municipalities
--    Q: Which cities/municipalities have the most listings?
-- ---------------------------------------------------------------------
SELECT
    municipality,
    COUNT(*) AS listings
FROM jobs
WHERE municipality IS NOT NULL
GROUP BY municipality
ORDER BY listings DESC
LIMIT 15;


-- ---------------------------------------------------------------------
-- 7. Monthly listing trend
--    Q: How do listing counts move month over month?
--    to_char(...,'YYYY-MM') gives a clean categorical month label for
--    charting; GROUP/ORDER BY the real date_trunc value so months sort
--    chronologically (not alphabetically).
--    NB: rising curve is likely survivorship bias (see header note).
-- ---------------------------------------------------------------------
SELECT
    to_char(date_trunc('month', publication_date), 'YYYY-MM') AS month,
    COUNT(*) AS listings
FROM jobs
WHERE publication_date IS NOT NULL
GROUP BY date_trunc('month', publication_date)
ORDER BY date_trunc('month', publication_date);


-- ---------------------------------------------------------------------
-- 8. Monthly trend with month-over-month change (window function)
--    Q: How much did listings rise/fall vs the previous month?
--    LAG() reads the prior month's count over a month-ordered window;
--    first row's change is NULL (no prior month) — expected, not a bug.
-- ---------------------------------------------------------------------
WITH monthly AS (
    SELECT
        date_trunc('month', publication_date) AS month,
        COUNT(*) AS listings
    FROM jobs
    WHERE publication_date IS NOT NULL
    GROUP BY date_trunc('month', publication_date)
)
SELECT
    to_char(month, 'YYYY-MM') AS month,
    listings,
    listings - LAG(listings) OVER (ORDER BY month) AS change_from_prev
FROM monthly
ORDER BY month;


-- ---------------------------------------------------------------------
-- 9. Top occupation field per region (top-N-per-group pattern)
--    Q: What is the single most-demanded field in each region?
--    ROW_NUMBER() partitions by region, ranks fields by count, and the
--    outer WHERE rn = 1 keeps each region's leader.
-- ---------------------------------------------------------------------
WITH ranked AS (
    SELECT
        region,
        occupation_field,
        COUNT(*) AS listings,
        ROW_NUMBER() OVER (
            PARTITION BY region
            ORDER BY COUNT(*) DESC
        ) AS rn
    FROM jobs
    WHERE region IS NOT NULL
    GROUP BY region, occupation_field
)
SELECT
    region,
    occupation_field,
    listings
FROM ranked
WHERE rn = 1
ORDER BY listings DESC;


-- ---------------------------------------------------------------------
-- 10. Data-completeness profile (data-quality evidence)
--     Q: How populated are the columns the analysis relies on?
--     COUNT(col) ignores NULLs; COUNT(*) counts all rows — the gap is
--     the null count. Documents trustworthiness of each key column.
-- ---------------------------------------------------------------------
SELECT
    COUNT(*)                                   AS total_rows,
    COUNT(municipality)                        AS has_municipality,
    COUNT(*) - COUNT(municipality)             AS missing_municipality,
    COUNT(occupation_field)                    AS has_occupation_field,
    COUNT(employer_name)                       AS has_employer_name,
    COUNT(publication_date)                    AS has_publication_date
FROM jobs;
