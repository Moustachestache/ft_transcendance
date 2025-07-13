import psycopg2
import os
import time

conn = None

"""
    nota bene
        this script updates the database with preset information from a .csv file.

        The file has to be added to the DATABASE DOCKER, because the *execution* of the commands takes place in the DATABASE DOCKER, even if we launch it from the DJANGO DOCKER
"""
""" 
try: """
conn = psycopg2.connect(
    host = 'postgres',
    dbname = os.getenv('POSTGRES_DB'),
    user = os.getenv('POSTGRES_USER'),
    password = os.getenv('POSTGRES_PASSWORD'),
    port = 5432
)

# https://www.psycopg.org/docs/cursor.html
cursor = conn.cursor()
cursor.execute("SELECT * FROM api_news")
if (cursor.rowcount > 0):
    print('hello, superior to zero so quitos')
    exit(0)

print('UPDATING DATABASE ACCORDING TO json and the ARGonauts')

cursor.execute("COPY api_news FROM '/tmp/news_backup.csv' DELIMITER ',';")
# maybe pre-add players
# cursor.execute("COPY api_news FROM '/tmp/news_backup.csv' DELIMITER ',';")
    
conn.commit()
cursor.close()
conn.close()

""" except(Exception, psycopg2.DatabaseError) as error:
    print('ERROR WITH CONNECTING TO DATABASE')
    exit(1) """