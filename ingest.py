import requests
import psycopg2

# --- connect ---
conn = psycopg2.connect(
    host="localhost",
    port="5432",
    dbname="jobads",
    user="alif",
)
cur = conn.cursor()

# --- fetch batches ---
url = "https://jobsearch.api.jobtechdev.se/search"
limit = 100
offset = 0
all_inserted = 0

# --- loop and insert ---
while True:
    params = {"q": "data", "limit": limit, "offset": offset}
    response = requests.get(url, params=params)
    ads = response.json()["hits"]

    if not ads:          # empty page → no more results, stop
        break

    print(f"Page at offset {offset}: {len(ads)} ads")

    for ad in ads:
        values = (
        ad.get("id"),
        ad.get("headline"),
        ad.get("description", {}).get("text"),
        ad.get("number_of_vacancies"),
        ad.get("employer", {}).get("name"),
        ad.get("employer", {}).get("organization_number"),
        ad.get("occupation", {}).get("label"),
        ad.get("occupation_group", {}).get("label"),
        ad.get("occupation_field", {}).get("label"),
        ad.get("workplace_address", {}).get("municipality"),
        ad.get("workplace_address", {}).get("region"),
        ad.get("employment_type", {}).get("label"),
        ad.get("working_hours_type", {}).get("label"),
        ad.get("publication_date"),
        ad.get("last_publication_date"),
        ad.get("application_deadline"),
        ad.get("removed"),
        ad.get("removed_date"),)

        cur.execute(
        """
        INSERT INTO jobs (
            id, headline, description, number_of_vacancies,
            employer_name, employer_org_number,
            occupation_label, occupation_group, occupation_field,
            municipality, region,
            employment_type, working_hours_type,
            publication_date, last_publication_date, application_deadline,
            removed, removed_date
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING;
        """,
        values,)
        all_inserted += cur.rowcount

    offset += limit        # advance to the next page

    if len(ads) < limit:   # last page was partial → that was the end
        break

conn.commit()
print(f"Total rows inserted: {all_inserted}")

cur.close()
conn.close()



