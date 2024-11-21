import logging
from opcua import Client, ua
from typing import Optional
import re

# Initialize logging
logging.basicConfig(level=logging.INFO)

def connect_to_opcua_server(endpoint: str) :
    """Connects to the OPC UA server and returns the client instance if successful."""
    client = Client(endpoint)
    try:
        client.connect()
        logging.info("Connected to OPC UA Server at %s", endpoint)
        
        return client
    except Exception as e:
        logging.error("Failed to connect to OPC UA Server: %s", str(e))
        return None  # Return None if connection fails

def update_single_node_value(client: Client, answer: str, question: str):
    """
    Update a single node's value based on the provided node_id and the question provided.
    The node is updated only if there's a word match between the display name and the sanitized question.
    The answer is processed to extract numeric values (space-separated) before updating the node.
    """
    try:
        # Define the node ID to update
        node_id = "ns=2;i=10221"
        node = client.get_node(node_id)
        current_value = node.get_value()
        logging.info("Current value of the node '%s' is: %s", node_id, current_value)

        # Get the display name of the node
        display_name = node.get_display_name().Text
        display_name_words = set(display_name.lower().split())  # Split and convert to lowercase for matching

        # Sanitize the question: remove special characters and split into words
        sanitized_question = re.sub(r'[^\w\s]', '', question)  # Remove punctuation
        question_words = set(sanitized_question.lower().split())

        logging.info("Checking node with display name: %s", display_name)

        # Process the answer to extract space-separated numeric values
        sanitized_answer = ' '.join(word.strip(',.?!\'"') for word in answer.split())  # Remove leading/trailing chars
        numeric_values = [int(word) for word in sanitized_answer.split() if word.isdigit()]  # Filter numeric values

        if numeric_values:
            # Use the first numeric value for the update
            numeric_value = numeric_values[0]
            logging.info("Extracted numeric value from answer: %s", numeric_value)
        else:
            logging.warning("No numeric value found in the answer. Update aborted.")
            return False  # Abort if no numeric value is found

        # Check if there's any word overlap between the question and the display name
        if question_words & display_name_words:  # Intersection to find common words
            logging.info("Match found! Updating node '%s' with new value: %s", display_name, numeric_value)
            
            # Update the node's value with the extracted numeric value
            node.set_value(ua.Variant(numeric_value, ua.VariantType.Int32))
            logging.info("Node '%s' updated successfully.", display_name)
            return True  # Successfully updated the node
        else:
            logging.info("No word match found for node '%s'. No update performed.", display_name)
            return False  # No match found, update not performed

    except Exception as e:
        logging.error("Error while updating node '%s': %s", node_id, str(e))
        return False  # Indicate failure if an error occurs
