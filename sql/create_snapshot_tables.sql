CREATE TABLE job_snapshots (
    snapshot_id SERIAL PRIMARY KEY,
    job_id VARCHAR(50),
    snapshot_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);