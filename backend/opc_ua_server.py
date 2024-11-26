from opcua import Server, ua
from datetime import datetime
import pandas as pd
import mysql.connector
import time
import random
import logging

# Set up logging
logging.basicConfig(filename="opcua_server.log", level=logging.INFO, format="%(asctime)s - %(message)s")

# Update the file path to the location of the Excel file
excel_path = r"C:\Users\Sreen\Downloads\Project 10001_Instrument Index_R3_18-Mar-2024 (1).xlsx"

# Connect to MySQL database
db_connection = mysql.connector.connect(
    host="localhost",
    user="root",         # Replace with your MySQL username
    password="SreenuAruru@2640",     # Replace with your MySQL password
    database="iadb"       # Database created earlier
)
cursor = db_connection.cursor()

# Create a table for historical data if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tag_id VARCHAR(100) NOT NULL,
    timestamp DATETIME NOT NULL,
    value DOUBLE NOT NULL
)
""")
db_connection.commit()

# Load the Excel file
data = pd.read_excel(excel_path, engine='openpyxl')  # Use openpyxl as the engine

# Extract relevant columns
relevant_columns = [
    "TG NO",
    "INST. TYPE DESCRIPTION",
    "TAG SERVICE",
    "CALIB. RANGE MIN",
    "CALIB. RANGE MAX",
    "CALIB. RANGE UOM",
    "SIGNAL TYPE"
]
tags_data = data[relevant_columns].dropna(subset=["TG NO"])

# Initialize OPC UA server
server = Server()
server.set_endpoint("opc.tcp://127.0.0.1:4841/llmtool/server/")  # Use IPv4 and an alternative port
server.set_server_name("Enhanced Excel-Based OPC UA Server")

# Set namespace
namespace = server.register_namespace("ExcelInstrumentNamespace")
objects = server.nodes.objects

# Create a folder for all tags
tags_folder = objects.add_folder(namespace, "Tags")

# Add nodes dynamically based on Excel data
nodes = {}
for index, row in tags_data.iterrows():
    tag_id = row["TG NO"]
    sanitized_tag_id = tag_id  # Replace hyphens for valid identifiers

    # Ensure numeric calibration range
    try:
        min_range = float(row["CALIB. RANGE MIN"]) if not pd.isna(row["CALIB. RANGE MIN"]) else 0.0
    except ValueError:
        min_range = 0.0

    try:
        max_range = float(row["CALIB. RANGE MAX"]) if not pd.isna(row["CALIB. RANGE MAX"]) else 100.0
    except ValueError:
        max_range = 100.0

    # Add the main value variable under the Tags folder
    value_variable = tags_folder.add_variable(namespace, sanitized_tag_id, random.uniform(min_range, max_range))
    value_variable.set_writable()

    # Add descriptions
    signal_type = row.get("SIGNAL TYPE", "Unknown")  # Default to "Unknown" if no signal type
    variable_description = (
        f"Main value of the instrument. Measures {row['INST. TYPE DESCRIPTION']}.\n"
        f"Range: {min_range}-{max_range} {row['CALIB. RANGE UOM']}.\n"
        f"Signal Type: {signal_type}."
    )
    value_variable.set_attribute(ua.AttributeIds.Description, ua.DataValue(ua.LocalizedText(variable_description)))

    # Print information about the added variable
    print(f"Added tag: {tag_id}, Range: {min_range}-{max_range}, Signal Type: {signal_type}")
    logging.info(f"Added tag: {tag_id}, Range: {min_range}-{max_range}, Signal Type: {signal_type}")

    # Assign a random increment rate (1, 2, or 0.5)
    increment = random.choice([1, 2, 0.5])

    # Save the variable and ranges for updates
    nodes[sanitized_tag_id] = {
        "variable": value_variable,
        "increment": increment,
        "min_range": min_range,
        "max_range": max_range,
        "last_value": value_variable.get_value(),  # Initialize the last value
    }

    # Log the initial value to the database
    cursor.execute(
        "INSERT INTO history (tag_id, timestamp, value) VALUES (%s, %s, %s)",
        (tag_id, datetime.now(), value_variable.get_value())
    )
    db_connection.commit()

# Define a custom method for querying historical data
def query_history(parent, tag_id):
    """
    Custom OPC UA method to query historical data for a given tag ID.
    """
    cursor.execute("SELECT timestamp, value FROM history WHERE tag_id = %s ORDER BY timestamp ASC", (tag_id,))
    results = cursor.fetchall()
    return [
        f"Timestamp: {row[0]}, Value: {row[1]}" for row in results
    ]

# Add method for querying historical data
history_node = objects.add_object(namespace, "HistoryQuery")
history_query_method = history_node.add_method(
    namespace,
    "QueryHistory",
    query_history,
    [ua.VariantType.String],  # Input argument: tag ID
    [ua.VariantType.String]   # Output argument: List of historical values
)

# Start server
server.start()
print(f"Server started at {server.endpoint}")
logging.info("Server started")

try:
    while True:
        # Update tags with their respective increment values every 20 seconds
        for sanitized_tag_id, node_data in nodes.items():
            variable = node_data["variable"]
            increment = node_data["increment"]
            min_range = node_data["min_range"]
            max_range = node_data["max_range"]

            # Get the current value (from client or server)
            current_value = variable.get_value()

            # Check if the client updated the value
            if current_value != node_data["last_value"]:
                print(f"Client updated {sanitized_tag_id}: New Value = {current_value}")
                logging.info(f"Client updated {sanitized_tag_id}: New Value = {current_value}")
                node_data["last_value"] = current_value
                continue  # Skip auto-update this cycle to respect client changes

            # Increment the value
            new_value = current_value + increment
            if new_value > max_range:
                new_value = min_range  # Reset to min if it exceeds max

            # Update the variable
            print(f"Updating {sanitized_tag_id}: {current_value:.2f} -> {new_value:.2f} (Increment: {increment})")
            logging.info(f"Updated {sanitized_tag_id}: {current_value:.2f} -> {new_value:.2f}")
            variable.set_value(new_value)
            node_data["last_value"] = new_value  # Update the last value

            # Log the new value to the database
            cursor.execute(
                "INSERT INTO history (tag_id, timestamp, value) VALUES (%s, %s, %s)",
                (sanitized_tag_id, datetime.now(), new_value)
            )
            db_connection.commit()

        # Wait for 20 seconds before the next update cycle
        time.sleep(20)
except KeyboardInterrupt:
    print("Server stopped")
    logging.info("Server stopped")
finally:
    server.stop()
    db_connection.close()
    logging.info("Database connection closed.")
