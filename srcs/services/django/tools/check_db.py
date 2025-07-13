import psycopg2
import os
import time

conn = None

while (1):
    try:
        conn = psycopg2.connect(
            host = 'postgres',
            dbname = os.getenv('POSTGRES_DB'),
            user = os.getenv('POSTGRES_USER'),
            password = os.getenv('POSTGRES_PASSWORD'),
            port = 5432
        )

    except(Exception, psycopg2.DatabaseError) as error:
        print('Waiting for database...')
        time.sleep(5)
    finally:
        if conn is not None:
            conn.close()
            print('Database is available, starting Django...')
            exit(0)