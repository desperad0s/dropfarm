import psycopg2

# Connect to your database
conn = psycopg2.connect(
    dbname="dropfarm",
    user="postgres",
    password="dropfarmpostgres",
    host="localhost",
    port="5432"
)

# Open a cursor to perform database operations
cur = conn.cursor()

# Drop the alembic_version table if it exists
cur.execute("DROP TABLE IF EXISTS alembic_version;")

# Commit the changes
conn.commit()

# Close communication with the database
cur.close()
conn.close()

print("alembic_version table has been dropped if it existed.")