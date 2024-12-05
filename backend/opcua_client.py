import logging
import re
from opcua import Client, ua
from opcua.common.node import Node
from typing import Optional, Set

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

# Configure logging
logging.basicConfig(level=logging.INFO)

def extract_keywords(text: str) -> Set[str]:
    """
    Extracts keywords (words or patterns like 'TE-102') from the input text.
    """
    return set(re.findall(r'\b\w+-?\d*\b', text.lower()))

def iterate_and_find_node(client: Client, node: Node, matching_keywords: Set[str]) -> Optional[str]:
    """
    Recursively iterates through the OPC UA node hierarchy to find a node
    with a display name matching the provided keywords.
    """
    try:
        # Get the display name of the current node
        display_name = node.get_display_name().Text
        display_name_keywords = extract_keywords(display_name)

        logging.info("Checking node: %s with display name: %s", node.nodeid.to_string(), display_name_keywords)

        # Check if the display name matches the keywords
        if matching_keywords & display_name_keywords:
            logging.info("Match found for node: %s with display name: %s", node.nodeid.to_string(), display_name)
            return node.nodeid.to_string()

        # Recursively check child nodes
        child_nodes = node.get_children()
        for child_node in child_nodes:
            result = iterate_and_find_node(client, child_node, matching_keywords)
            if result:
                return result

        return None
    except Exception as e:
        logging.warning("Failed to process node: %s", str(e))
        return None

def find_node_id_by_display_name(client: Client, matching_keywords: Set[str]) -> Optional[str]:
    """
    Finds the node_id of a node whose display name matches the provided keywords.
    """
    try:
        # Start from the Objects node
        objects_node = client.get_objects_node()
        return iterate_and_find_node(client, objects_node, matching_keywords)
    except Exception as e:
        logging.error("Error while retrieving nodes: %s", str(e))
        return None

def update_single_node_value(client: Client, answer: str, question: str) -> bool:
    """
    Updates the value of a node dynamically identified by matching keywords in the question and answer.
    """
    try:
        # Extract keywords from question and answer
        question_keywords = extract_keywords(question)
        answer_keywords = extract_keywords(answer)

        logging.info("Question Keywords: %s", question_keywords)
        logging.info("Answer Keywords: %s", answer_keywords)

        # Find intersection of question and answer keywords
        matching_keywords = question_keywords
        logging.info("Matching Keywords: %s", matching_keywords)

        if not matching_keywords:
            logging.warning("No keyword match found between question and answer. Update skipped.")
            return False

        # Find the node ID by matching keywords to display names
        node_id = find_node_id_by_display_name(client, matching_keywords)
        if not node_id:
            logging.warning("No node matched the keywords. Update skipped.")
            return False

        # Retrieve and update the matched node
        node = client.get_node(node_id)
        display_name = node.get_display_name().Text
        logging.info("Updating node with ID: %s and Display Name: %s", node_id, display_name)

        # Process and sanitize the answer to extract numeric values
        sanitized_answer = ' '.join(word.strip(',.?!\'"') for word in answer.split())
        numeric_values = [int(word) for word in sanitized_answer.split() if word.isdigit()]

        if numeric_values:
            numeric_value = numeric_values[0]
            logging.info("Updating node value: %s", numeric_value)
            node.set_value(ua.Variant(numeric_value, ua.VariantType.Int32))

            # Update the node description
            current_description = node.get_description().Text if node.get_description() else ""
            updated_description = f"{current_description} (Value Updated: {numeric_value})".strip()
            node.set_attribute(ua.AttributeIds.Description, ua.DataValue(ua.LocalizedText(updated_description)))
            logging.info("Node description updated to: %s", updated_description)

            return True
        else:
            logging.warning("No numeric value found in the answer: %s", sanitized_answer)
            return False
    except Exception as e:
        logging.error("Error updating node: %s", str(e))
        return False