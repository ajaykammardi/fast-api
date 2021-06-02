import psycopg2 as pg

try:
    dbconnect = pg.connect(
            database='postgres_db',
            user='postgres_user',
            password='postgres',
            host='postgresdb',
            port=5432
        )
except Exception as error:
    print(error)