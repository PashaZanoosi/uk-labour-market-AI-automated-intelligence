CREATE TABLE jobs (

    job_id VARCHAR(50) PRIMARY KEY,

    title TEXT,

    company TEXT,

    location TEXT,

    salary_min INTEGER,

    salary_max INTEGER,

    average_salary INTEGER,

    created_date DATE,

    description TEXT

);