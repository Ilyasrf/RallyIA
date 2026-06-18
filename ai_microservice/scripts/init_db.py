import os

import psycopg2

SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/igudar_ai"
)


def main():
    conn = psycopg2.connect(SQLALCHEMY_DATABASE_URL)
    conn.autocommit = True

    with open(os.path.join(os.path.dirname(__file__), "init_db.sql")) as f:
        sql = f.read()

    with conn.cursor() as cur:
        cur.execute(sql)
        print("Database initialized successfully.")

    conn.close()


if __name__ == "__main__":
    main()
