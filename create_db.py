import pandas as pd
import sqlite3

# Load your CSV
df = pd.read_csv("Sample - Superstore.csv", encoding="latin1")

# Create SQLite database
conn = sqlite3.connect("retail_analytics.db")

# Write data to 'orders' table
df.to_sql("orders", conn, if_exists="replace", index=False)

# Confirm rows inserted
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM orders")
print("Rows in 'orders' table:", cursor.fetchone()[0])

conn.close()
