import logging
import re
from opcua import Client, ua
from typing import Optional, Set

# Initialize logging
logging.basicConfig(level=logging.INFO)

def connect_to_opcua_server(endpoint: str) -> Optional[Client]:
    """Connects to the OPC UA server and returns the client instance if successful."""
    client = Client(endpoint)
    try:
        client.connect()
        logging.info("Connected to OPC UA Server at %s", endpoint)
        return client
    except Exception as e:
        logging.error("Failed to connect to OPC UA Server: %s", str(e))
        return None

def extract_keywords(text: str) -> Set[str]:
    """
    Extracts keywords including tags like 'TI101.PV' or 'TE-102' from the input text.
    """
    return set(re.findall(r'\b\w+(?:\.\w+)*\b', text.lower()))

def count_matching_words(set1: Set[str], set2: Set[str]) -> int:
    """
    Counts how many words in set1 are present in set2.
    """
    return len(set1 & set2)

def check_matching_conditions(answer_keywords: Set[str], description_keywords: Set[str]) -> bool:
    """
    Checks the following conditions:
    1. Combine word pattern two or more match to answer and description.
    2. Each word three or more match to answer and description.
    """
    # Condition 1.1: At least two combined word patterns match
    if count_matching_words(answer_keywords, description_keywords) >= 2:
        return True

    # Condition 1.2: At least three individual words match
    if len({word for word in answer_keywords if word in description_keywords}) >= 3:
        return True

    return False

def find_matching_node(client: Client, primary_keywords: Set[str], fallback_keywords: Optional[Set[str]] = None) -> Optional[str]:
    """
    Searches for a node matching the given keywords using descriptions.
    Falls back to other keywords if no match is found.
    """
    try:
        objects_node = client.get_objects_node()

        def recursive_search(node):
            description = node.get_description().Text if node.get_description() else ""
            description_keywords = extract_keywords(description)
            logging.info("Checking node: %s with description: %s", node.nodeid.to_string(), description_keywords)

            # Check primary matching conditions
            if check_matching_conditions(primary_keywords, description_keywords):
                logging.info("Match found for node: %s", node.nodeid.to_string())
                return node.nodeid.to_string()

            # Recursively search child nodes
            for child in node.get_children():
                result = recursive_search(child)
                if result:
                    return result

            return None

        # Start searching with primary keywords
        matching_node = recursive_search(objects_node)
        if matching_node:
            return matching_node

        # Fallback to secondary keywords if provided
        if fallback_keywords:
            logging.info("Fallback to secondary keywords.")
            return recursive_search(objects_node)

        return None

    except Exception as e:
        logging.error("Error during node search: %s", str(e))
        return None

def update_single_node_value(client: Client, answer: str, question: str) -> bool:
    """
    Updates the value of a node based on the matching logic described.
    """
    try:
        # Extract keywords
        answer_keywords = extract_keywords(answer)
        question_keywords = extract_keywords(question)

        logging.info("Answer Keywords: %s", answer_keywords)
        logging.info("Question Keywords: %s", question_keywords)

        # Check if the answer is short (two or fewer words)
        if len(answer_keywords) <= 2:
            # Use question keywords as the primary source
            primary_keywords = question_keywords
            fallback_keywords = None
        else:
            # Use answer keywords as the primary source
            primary_keywords = answer_keywords
            fallback_keywords = question_keywords

        # Find the matching node
        node_id = find_matching_node(client, primary_keywords, fallback_keywords)
        if not node_id:
            logging.warning("No matching node found. Update skipped.")
            return False

        # Retrieve and update the node
        node = client.get_node(node_id)
        description = node.get_description().Text if node.get_description() else ""
        logging.info("Updating node with ID: %s and Description: %s", node_id, description)

        # Extract numeric values from the answer
        numeric_values = [int(word) for word in answer.split() if word.isdigit()]

        if numeric_values:
            numeric_value = numeric_values[0]
            logging.info("Updating node value to: %s", numeric_value)
            node.set_value(ua.Variant(numeric_value, ua.VariantType.Int32))

            # Update the node description
            updated_description = f"{description} (Value Updated: {numeric_value})"
            node.set_attribute(ua.AttributeIds.Description, ua.DataValue(ua.LocalizedText(updated_description)))
            logging.info("Node description updated to: %s", updated_description)

            return True
        else:
            logging.warning("No numeric value found in the answer. Update skipped.")
            return False

    except Exception as e:
        logging.error("Error updating node value: %s", str(e))
        return False
