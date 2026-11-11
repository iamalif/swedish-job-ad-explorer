CREATE TABLE jobs (
    id TEXT PRIMARY KEY,
    headline TEXT,
    description TEXT,
    number_of_vacancies INTEGER,
    employer_name TEXT,
    employer_org_number TEXT,
    occupation_label TEXT,
    occupation_group TEXT,
    occupation_field TEXT,
    municipality TEXT,
    region TEXT,
    employment_type TEXT,
    working_hours_type TEXT,
    publication_date TIMESTAMPTZ,
    last_publication_date TIMESTAMPTZ,
    application_deadline TIMESTAMPTZ,
    removed BOOLEAN,
    removed_date TIMESTAMPTZ
);


SELECT * FROM jobs;

SELECT id, headline, employer_name, municipality, publication_date FROM jobs;

SELECT COUNT(*) FROM jobs;

SELECT * FROM jobs LIMIT 50;

SELECT COUNT(*) FROM jobs
WHERE municipality IS NULL;

SELECT
    COUNT(*) AS total,
    COUNT(municipality) AS non_null,
    COUNT(*) - COUNT(municipality) AS null_count
FROM jobs;

SELECT headline, employer_name FROM jobs
WHERE municipality IS NULL
LIMIT 50;

SELECT
    COUNT(*) AS total,
    COUNT(municipality) AS municipality_non_null,
    COUNT(*) - COUNT(municipality) AS municipality_null,
    COUNT(occupation_field) AS occupation_field_non_null,
    COUNT(*) - COUNT(occupation_field) AS occupation_field_null,
    COUNT(employer_name) AS employer_name_non_null,
    COUNT(*) - COUNT(employer_name) AS employer_name_null,
    COUNT(number_of_vacancies) AS number_of_vacancies_non_null,
    COUNT(*) - COUNT(number_of_vacancies) AS number_of_vacancies_null,
    COUNT(publication_date) AS publication_date_non_null,
    COUNT(*) - COUNT(publication_date) AS publication_date_null
FROM jobs;

SELECT occupation_field, COUNT(*) FROM jobs
GROUP BY occupation_field
ORDER BY COUNT(*) DESC;

SELECT employer_name, COUNT(*) FROM jobs
GROUP BY employer_name
ORDER BY COUNT(*) DESC
LIMIT 10;

SELECT employer_name, COUNT(*) FROM jobs
WHERE employer_name ILIKE '%academic work%'
GROUP BY employer_name
ORDER BY COUNT(*) DESC;

SELECT UPPER(employer_name), COUNT(*) FROM jobs
GROUP BY UPPER(employer_name)
ORDER BY COUNT(*) DESC
LIMIT 10;

WITH monthly AS (
    SELECT
        date_trunc('month', publication_date) AS month,
        COUNT(*) AS listings
    FROM jobs
    GROUP BY date_trunc('month', publication_date)
)
SELECT
    month,
    listings,
    listings - LAG(listings) OVER (ORDER BY month) AS change_from_prev
FROM monthly
ORDER BY month;