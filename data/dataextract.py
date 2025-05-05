import psycopg2
import pandas as pd

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname="smart_composting_api",
    user="npds_2025",
    password="npds_2025_eh0atNiA5MVx2FYY3UnqVo5Vzv_0N9MRnSZ_3dkJgT_r2EIONEpFzV1o3IXHSFsjUX8hXT-9OgKqt8f512RPWJohKdM_pA-dAfimfXXOuke5C0Z9irOt4GrEV5R",
    host="db.composting.tinkerthings.global",  # or the IP address of your DB server
    port="6969"        # default PostgreSQL port
)

# Table names
table_names = [
    "devicedata", "devices", "devicesensors", "devicetypes",
    "errors", "sensordata", "sensors", "users"
]

# Dictionary to store DataFrames
dfs = {}

# Load each table into a DataFrame
for table in table_names:
    query = f"SELECT * FROM {table} LIMIT 100000;"
    dfs[table] = pd.read_sql_query(query, conn)
    print(f"Loaded {table} with {len(dfs[table])} rows.")

# Close connection
conn.close()