from groq import Groq
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import os
import json


load_dotenv()


client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)



def load_taxonomy():

    with engine.connect() as connection:

        result = connection.execute(
            text("""
            SELECT taxonomy_id, name
            FROM skill_taxonomy
            WHERE level = 2
            """)
        )

        return [
            {
                "id": row.taxonomy_id,
                "name": row.name
            }
            for row in result
        ]



def classify_skill(skill_name, taxonomy):


    taxonomy_text = "\n".join(
        [
            f"{x['id']}: {x['name']}"
            for x in taxonomy
        ]
    )


    response = client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        temperature=0,

        messages=[

            {
                "role":"system",
                "content":f"""

You classify labour market skills.

Choose the best taxonomy category.

Available taxonomy:

{taxonomy_text}


Rules:

Return only JSON.

Format:

{{
"taxonomy_id": 12
}}

Choose the closest category.

"""
            },

            {
                "role":"user",
                "content":skill_name
            }

        ]

    )


    output = response.choices[0].message.content


    output = (
        output
        .replace("```json","")
        .replace("```","")
        .strip()
    )


    return json.loads(output)["taxonomy_id"]




def update_skill_taxonomy(skill_id, taxonomy_id):


    with engine.begin() as connection:

        connection.execute(

            text("""
            UPDATE skills
            SET taxonomy_id = :taxonomy_id
            WHERE skill_id = :skill_id
            """),

            {
                "taxonomy_id": taxonomy_id,
                "skill_id": skill_id
            }

        )





taxonomy = load_taxonomy()


with engine.connect() as connection:

    result = connection.execute(

        text("""
        SELECT skill_id, skill_name
        FROM skills
        WHERE taxonomy_id IS NULL
        """)

    )

    skills = result.fetchall()



print(f"Skills to classify: {len(skills)}")



for skill in skills:


    skill_id = skill.skill_id
    skill_name = skill.skill_name


    print("--------------------")
    print(skill_name)


    try:

        taxonomy_id = classify_skill(
            skill_name,
            taxonomy
        )


        print(
            f"Taxonomy ID: {taxonomy_id}"
        )


        update_skill_taxonomy(
            skill_id,
            taxonomy_id
        )


    except Exception as e:

        print(
            f"Error: {skill_name}"
        )

        print(e)



print("Finished")