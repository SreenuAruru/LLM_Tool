from opcua import Server
from datetime import datetime
import pandas as pd
import time
import random

# Update the file path to the location of the Excel file
excel_path = r"C:\Users\Sreen\Downloads\Project 10001_Instrument Index_R3_18-Mar-2024 (1).xlsx"

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
server.set_server_name("Excel-Based OPC UA Server")

# Set namespace
namespace = server.register_namespace("ExcelInstrumentNamespace")
objects = server.nodes.objects

# Create a single folder for all tags under the "Objects" node
tags_folder = objects.add_object(namespace, "AllTags")

# Add nodes dynamically based on Excel data
nodes = {}
for index, row in tags_data.iterrows():
    tag_id = row["TG NO"]
    parameter_name = row["INST. TYPE DESCRIPTION"]
    tag_service = row["TAG SERVICE"]

    # Create the display name in the format: "TagID (ParameterName)"
    display_name = tag_id
    sanitized_tag_id = tag_id.replace("-", "_")  # Replace hyphens for valid identifiers

    # Ensure numeric calibration range
    try:
        min_range = float(row["CALIB. RANGE MIN"]) if not pd.isna(row["CALIB. RANGE MIN"]) else 0.0
    except ValueError:
        min_range = 0.0

    try:
        max_range = float(row["CALIB. RANGE MAX"]) if not pd.isna(row["CALIB. RANGE MAX"]) else 100.0
    except ValueError:
        max_range = 100.0

    # Add variable directly to the single "AllTags" folder
    value_variable = tags_folder.add_variable(
        namespace, f"{display_name}", random.uniform(min_range, max_range)
    )
    value_variable.set_writable()

    # Print information about the added tag
    print(f"Added tag: {display_name}, Increment Rate: Randomly assigned, Range: {min_range}-{max_range}")

    # Assign a random increment rate (1, 2, or 0.5)
    increment = random.choice([1, 2, 0.5])

    # Save the variable, increment, and ranges for updates
    nodes[sanitized_tag_id] = {
        "variable": value_variable,
        "increment": increment,
        "min_range": min_range,
        "max_range": max_range,
        "last_value": value_variable.get_value(),  # Initialize the last value
    }

# Start server
server.start()
print(f"Server started at {server.endpoint}")

try:
    while True:
        # Update tags with their respective increment values every 2 seconds
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
                node_data["last_value"] = current_value
                continue  # Skip auto-update this cycle to respect client changes

            # Increment the value
            new_value = current_value + increment
            if new_value > max_range:
                new_value = min_range  # Reset to min if it exceeds max

            # Update the variable
            print(f"Updating {sanitized_tag_id}: {current_value:.2f} -> {new_value:.2f} (Increment: {increment})")
            variable.set_value(new_value)
            node_data["last_value"] = new_value  # Update the last value

        # Wait for 2 seconds before the next update
        time.sleep(20)
except KeyboardInterrupt:
    print("Server stopped")
    server.stop()
