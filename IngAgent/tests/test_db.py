import sqlite3
import json

conn = sqlite3.connect("review.db")
cursor = conn.execute("SELECT agent_name, output_data FROM agent_outputs")

for row in cursor.fetchall():
    print("\nAgent:", row[0])
    print("Data:")
    print(json.dumps(json.loads(row[1]), indent=4))
