from groq import Groq
from dotenv import load_dotenv
import os
import json
from sqlalchemy import create_engine, text

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

# -------------------------
# Load existing skills cache
# -------------------------

def load_skills_cache():
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                SELECT skill_id,
                       skill_name
                FROM skills
            """)
        )
        return {
            row.skill_name.lower(): row.skill_id
            for row in result
        }
skills_cache = load_skills_cache()

# -------------------------
# Check processed jobs
# -------------------------

def job_already_processed(job_id):
    with engine.connect() as connection:
        result = connection.execute(
            text("""
            SELECT COUNT(*)
            FROM job_skills
            WHERE job_id = :job_id
            """),
            {
                "job_id": job_id
            }
        )
        return result.fetchone()[0] > 0

# -------------------------
# AI extraction
# -------------------------

def extract_skills(description):
    response = client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=[

            {
                "role": "system",
                "content": """

You are a labour market data analyst.

Extract professional skills from job descriptions.

Rules:

Extract only skills useful for labour market analysis.

Prioritise:

- Technical skills
- Business skills
- Industry/domain knowledge
- Professional methodologies


Avoid generic personality traits.

Do not extract:

enthusiasm
confidence
motivation
kindness
passion
commitment
hardworking
flexibility


Avoid broad words:

work
experience
people
team
support


Merge similar skills.


Return confidence score:

1.0 = explicitly mentioned
0.7 = strongly implied
0.5 = weakly implied


Allowed categories:

Technical
Business
Methodology
Domain
Soft Skill


Return only JSON.

Format:

{
 "skills":[
   {
    "name":"Skill name",
    "category":"Category",
    "confidence":0.9
   }
 ]
}

No markdown.
No explanation.

"""
            },

            {
                "role": "user",
                "content": description[:4000]
            }

        ],

        temperature=0
    )


    output = response.choices[0].message.content


    clean = (
        output
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )


    return json.loads(clean)



# -------------------------
# Skill handling
# -------------------------

def get_or_create_skill(skill_name, category):

    global skills_cache


    key = skill_name.lower()


    # موجود در Cache
    if key in skills_cache:

        return skills_cache[key]



    # ساخت Skill جدید

    with engine.begin() as connection:

        result = connection.execute(

            text("""
            INSERT INTO skills(
                skill_name,
                category
            )
            VALUES(
                :skill,
                :category
            )
            RETURNING skill_id
            """),

            {
                "skill": skill_name,
                "category": category
            }

        )


        skill_id = result.fetchone()[0]


        skills_cache[key] = skill_id


        return skill_id



# -------------------------
# Save relationship
# -------------------------

def save_job_skill(job_id, skill_id, confidence):


    confidence = max(
        0,
        min(
            confidence,
            1
        )
    )


    with engine.begin() as connection:


        connection.execute(

            text("""
            INSERT INTO job_skills(
                job_id,
                skill_id,
                confidence_score
            )
            VALUES(
                :job_id,
                :skill_id,
                :confidence
            )

            ON CONFLICT DO NOTHING

            """),

            {
                "job_id": job_id,
                "skill_id": skill_id,
                "confidence": confidence
            }

        )



# -------------------------
# Load jobs
# -------------------------

with engine.connect() as connection:

    result = connection.execute(

        text("""
        SELECT job_id, description
        FROM jobs
        LIMIT 50
        """)

    )

    jobs = result.fetchall()



# -------------------------
# Process
# -------------------------

for job in jobs:


    job_id = job[0]

    description = job[1]



    if job_already_processed(job_id):

        print(
            f"Skipping {job_id}, already processed"
        )

        continue



    print("\n-------------------------")

    print(
        f"Processing job: {job_id}"
    )



    try:


        skills_json = extract_skills(
            description
        )


        print(
            json.dumps(
                skills_json,
                indent=2
            )
        )



        for item in skills_json["skills"]:


            skill_name = item["name"]

            category = item["category"]

            confidence = item.get(
                "confidence",
                0.5
            )



            skill_id = get_or_create_skill(
                skill_name,
                category
            )



            save_job_skill(
                job_id,
                skill_id,
                confidence
            )



        print(
            "Skills saved successfully"
        )



    except Exception as e:

        print(
            f"Error processing {job_id}"
        )

        print(e)



print("\nFinished")