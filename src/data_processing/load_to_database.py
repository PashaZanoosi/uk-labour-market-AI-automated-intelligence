import pandas as pd
from sqlalchemy import create_engine


df = pd.read_csv(
    "data/processed/jobs_clean.csv"
)


engine = create_engine(
    "postgresql://postgres:AApz%403236012@localhost:5432/uk_labour_market"
)


df.to_sql(
    "jobs",
    engine,
    if_exists="append",
    index=False
)


print("Data loaded successfully")