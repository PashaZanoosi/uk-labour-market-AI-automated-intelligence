import json
import pandas as pd
import glob


files = glob.glob("data/raw/jobs_*.json")

latest_file = max(files)


with open(latest_file, "r", encoding="utf-8") as file:
    data = json.load(file)


jobs = data["results"]


records = []


for job in jobs:

    records.append({

        "job_id": job.get("id"),

        "title": job.get("title"),

        "company": job.get("company", {}).get(
            "display_name",
            "Unknown"
        ),

        "location": job.get("location", {}).get(
            "display_name",
            "Unknown"
        ),

        "salary_min": job.get("salary_min"),

        "salary_max": job.get("salary_max"),

        "created_date": job.get("created"),

        "description": job.get("description")

    })


df = pd.DataFrame(records)


df.drop_duplicates(
    subset=["job_id"],
    inplace=True
)


df["average_salary"] = (
    df["salary_min"] + df["salary_max"]
) / 2


output = "data/processed/jobs_clean.csv"


df.to_csv(
    output,
    index=False,
    encoding="utf-8"
)


print("Rows processed:", len(df))
print("Saved:", output)