import csv
import os
import mysql.connector
from datetime import datetime

def process_csv_file(csv_file, bssid_power_dict):
    with open(csv_file, newline='', encoding='utf-8') as csvfile:
        column_names = ['BSSID',' First time seen', ' Last time seen', ' channel', ' Speed', ' Privacy', ' Cipher', ' Authentication', ' Power', ' # beacons', ' # IV', ' LAN IP', ' ID-length', ' ESSID', ' Key']  # Add other column names if needed
        airodump_reader = csv.DictReader(csvfile, fieldnames=column_names)

        # Skip the first row in the CSV file
        # next(airodump_reader, None)
        for row in airodump_reader:
            # print(row)
            
            bssid = row['BSSID']
            power = row[' Power']
            first = row[' First time seen']
            print(bssid)
            print(first)
            print(power)
            if bssid == "Station MAC":
                print("end at Station MAC row")
                break

            if bssid != "BSSID":
                if power:
                    try:
                        power = int(power)
                    except ValueError:
                        print(f"Skipping invalid power value: {power}")
                        power = None
                if first:
                    try:
                        timestamp = datetime.strptime(first.strip(), '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        print(f"Skipping invalid timestamp value: {first}")
                        timestamp = None

                if bssid in bssid_power_dict:
                    bssid_power_dict[bssid].append((power, timestamp))
                else:
                    bssid_power_dict[bssid] = [(power, timestamp)]

connection = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="root",
    password="xxxxx",
    database="ap_rssi"
)

cursor = connection.cursor()
# table_name = "location_1"


# Create table if not exists
cursor.execute('''CREATE TABLE IF NOT EXISTS access_points (
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    bssid VARCHAR(255),
    power INT,
    timestamp DATETIME
);
''')
connection.commit()

# Set the directory containing CSV files
csv_directory = "C:\\Users\\8RE\\Aim\\sqlite\\rp"  # Replace with the path to your directory containing the CSV files

bssid_power_dict = {}
# Loop through all files in the directory
for filename in os.listdir(csv_directory):
    if filename.endswith(".csv"):
        csv_file = os.path.join(csv_directory, filename)

        # Skip empty files
        if os.path.getsize(csv_file) > 0:
            print(f"Processing {csv_file}...")
            process_csv_file(csv_file, bssid_power_dict)
        else:
            print(f"Skipping empty file: {csv_file}")


# Insert BSSID, Power, and Timestamp values into the database
for bssid, power_timestamp_list in bssid_power_dict.items():
    for power, timestamp in power_timestamp_list:
        query = "INSERT INTO access_points (bssid, power, timestamp) VALUES (%s, %s, %s)"
        data = (bssid, power, timestamp)
        cursor.execute(query, data)
        connection.commit()


# Close the database connection
cursor.close()
connection.close()
