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
    try:
        node_id = "ns=2;i=2"  # Adjust the node ID as required
        node = client.get_node(node_id)
        display_name = node.get_display_name().Text

        logging.info("Retrieved Display Name: %s", display_name)

        # Normalize to lowercase
        sanitized_display_name = re.findall(r'\b\w+-?\d*\b', display_name.lower())  # Extract words or patterns like te-102
        sanitized_question = re.findall(r'\b\w+-?\d*\b', question.lower())  # Same normalization for question
        
        logging.info("Sanitized Display Name Words: %s", sanitized_display_name)
        logging.info("Sanitized Question Words: %s", sanitized_question)
        
        # Check for matches
        intersection = set(sanitized_display_name) & set(sanitized_question)
        logging.info("Intersection: %s", intersection)
        
        if intersection:
            sanitized_answer = ' '.join(word.strip(',.?!\'"') for word in answer.split())
            numeric_values = [int(word) for word in sanitized_answer.split() if word.isdigit()]
            
            if numeric_values:
                numeric_value = numeric_values[0]
                logging.info("Match found! Updating node with value: %s", numeric_value)
                node.set_value(ua.Variant(numeric_value, ua.VariantType.Int32))
                return True
            else:
                logging.warning("No numeric value found in the answer: %s", sanitized_answer)
                return False
        else:
            logging.info("No word match found. Update not performed.")
            return False
    except Exception as e:
        logging.error("Error updating node: %s", str(e))
        return False

