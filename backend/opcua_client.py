# import logging
# import re
# from opcua import Client, ua
# from typing import Optional, Set

# # Initialize logging
# logging.basicConfig(level=logging.INFO)

# def connect_to_opcua_server(endpoint: str) -> Optional[Client]:
#     """Connects to the OPC UA server and returns the client instance if successful."""
#     client = Client(endpoint)
#     try:
#         client.connect()
#         logging.info("Connected to OPC UA Server at %s", endpoint)
#         return client
#     except Exception as e:
#         logging.error("Failed to connect to OPC UA Server: %s", str(e))
#         return None

# def extract_keywords(text: str) -> Set[str]:
#     """
#     Extracts keywords including tags like 'TI101.PV' or 'TE-102' from the input text.
#     """
#     return set(re.findall(r'\b\w+(?:\.\w+)*\b', text.lower()))

# def count_matching_words(set1: Set[str], set2: Set[str]) -> int:
#     """
#     Counts how many words in set1 are present in set2.
#     """
#     return len(set1 & set2)

# def check_matching_conditions(answer_keywords: Set[str], description_keywords: Set[str]) -> bool:
#     """
#     Checks the following conditions:
#     1. Combine word pattern two or more match to answer and description.
#     2. Each word three or more match to answer and description.
#     """
#     # Condition 1.1: At least two combined word patterns match
#     if count_matching_words(answer_keywords, description_keywords) >= 2:
#         return True

#     # Condition 1.2: At least three individual words match
#     if len({word for word in answer_keywords if word in description_keywords}) >= 3:
#         return True

#     return False

# def process_node(node, primary_keywords: Set[str], fallback_keywords: Optional[Set[str]], answer: str) -> bool:
#     """
#     Processes a single node, checks its description against the conditions,
#     and updates the node value if a match is found.
#     """
#     try:
#         # Get the node description
#         description = node.get_description().Text if node.get_description() else ""
#         description_keywords = extract_keywords(description)

#         logging.info("Node ID: %s | Description Keywords: %s", node.nodeid.to_string(), description_keywords)

#         # Apply the conditions
#         if check_matching_conditions(primary_keywords, description_keywords):
#             logging.info("Primary keywords matched for node: %s", node.nodeid.to_string())
#         elif fallback_keywords and check_matching_conditions(fallback_keywords, description_keywords):
#             logging.info("Fallback keywords matched for node: %s", node.nodeid.to_string())
#         else:
#             return False  # No match found for this node

#         # If a match is found, update the node value
#         numeric_values = [int(word) for word in answer.split() if word.isdigit()]
#         if numeric_values:
#             numeric_value = numeric_values[0]
#             logging.info("Updating node value to: %s", numeric_value)

#             # Update node value
#             node.set_value(ua.Variant(numeric_value, ua.VariantType.Int32))

#             # Update node description
#             updated_description = f"{description} (Value Updated: {numeric_value})"
#             node.set_attribute(ua.AttributeIds.Description, ua.DataValue(ua.LocalizedText(updated_description)))
#             logging.info("Node description updated to: %s", updated_description)

#             return True
#         else:
#             logging.warning("No numeric value found in the answer. Update skipped.")
#             return False

#     except Exception as e:
#         logging.error("Error processing node: %s", str(e))
#         return False

# def recursive_node_check(node, primary_keywords: Set[str], fallback_keywords: Optional[Set[str]], answer: str) -> bool:
#     """
#     Recursively checks all nodes starting from the given node.
#     """
#     if process_node(node, primary_keywords, fallback_keywords, answer):  # If the current node matches, update and stop recursion
#         return True

#     # Check children nodes
#     for child in node.get_children():
#         if recursive_node_check(child, primary_keywords, fallback_keywords, answer):
#             return True

#     return False

# def update_single_node_value(client: Client, answer: str, question: str) -> bool:
#     """
#     Applies the conditions to match each node's description against the given question and answer.
#     Updates the value of a matching node if the conditions are satisfied.
#     """
#     try:
#         # Extract keywords from the answer and question
#         answer_keywords = extract_keywords(answer)
#         question_keywords = extract_keywords(question)

#         logging.info("Answer Keywords: %s", answer_keywords)
#         logging.info("Question Keywords: %s", question_keywords)

#         # Determine primary and fallback keywords based on the length of the answer
#         if len(answer_keywords) <= 2:  # Short answer
#             primary_keywords = question_keywords
#             fallback_keywords = None
#         else:  # Longer answer
#             primary_keywords = answer_keywords
#             fallback_keywords = question_keywords

#         # Start the recursive check from the Objects node
#         objects_node = client.get_objects_node()
#         return recursive_node_check(objects_node, primary_keywords, fallback_keywords, answer)

#     except Exception as e:
#         logging.error("Error during update process: %s", str(e))
#         return False

# import logging
# import re
# from opcua import Client, ua
# from typing import Optional, Set

# # Initialize logging
# logging.basicConfig(level=logging.INFO)

# def connect_to_opcua_server(endpoint: str) -> Optional[Client]:
#     """Connects to the OPC UA server and returns the client instance if successful."""
#     client = Client(endpoint)
#     try:
#         client.connect()
#         logging.info("Connected to OPC UA Server at %s", endpoint)
#         return client
#     except Exception as e:
#         logging.error("Failed to connect to OPC UA Server: %s", str(e))
#         return None

# def extract_keywords(text: str) -> Set[str]:
#     """
#     Extracts keywords including tags like 'TI101.PV' or 'TE-102' from the input text.
#     """
#     return set(re.findall(r'\b\w+(?:\.\w+)*\b', text.lower()))

# def count_matching_words(set1: Set[str], set2: Set[str]) -> int:
#     """
#     Counts how many words in set1 are present in set2.
#     """
#     return len(set1 & set2)

# def check_matching_conditions(answer_keywords: Set[str], description_keywords: Set[str]) -> bool:
#     """
#     Checks the following conditions:
#     1. Combine word pattern two or more match to answer and description.
#     2. Each word three or more match to answer and description.
#     """
#     # Condition 1.1: At least two combined word patterns match
#     if count_matching_words(answer_keywords, description_keywords) >= 2:
#         return True

#     # Condition 1.2: At least three individual words match
#     if len({word for word in answer_keywords if word in description_keywords}) >= 3:
#         return True

#     return False

# def process_node(node, primary_keywords: Set[str], fallback_keywords: Optional[Set[str]], answer: str) -> bool:
#     """
#     Processes a single node, checks its description against the conditions,
#     and updates the node value if a match is found.
#     """
#     try:
#         # Get the node description
#         description = node.get_description().Text if node.get_description() else ""
#         description_keywords = extract_keywords(description)

#         logging.info("Node ID: %s | Description Keywords: %s", node.nodeid.to_string(), description_keywords)

#         # Apply the conditions
#         if check_matching_conditions(primary_keywords, description_keywords):
#             logging.info("Primary keywords matched for node: %s", node.nodeid.to_string())
#         elif fallback_keywords and check_matching_conditions(fallback_keywords, description_keywords):
#             logging.info("Fallback keywords matched for node: %s", node.nodeid.to_string())
#         else:
#             return False  # No match found for this node

#         # If a match is found, update the node value
#         numeric_values = [int(word) for word in answer.split() if word.isdigit()]
#         if numeric_values:
#             numeric_value = numeric_values[0]
#             logging.info("Updating node value to: %s", numeric_value)

#             # Update node value
#             node.set_value(ua.Variant(numeric_value, ua.VariantType.Int32))

#             # Update node description
#             updated_description = f"{description} (Value Updated: {numeric_value})"
#             node.set_attribute(ua.AttributeIds.Description, ua.DataValue(ua.LocalizedText(updated_description)))
#             logging.info("Node description updated to: %s", updated_description)

#             return True
#         else:
#             logging.warning("No numeric value found in the answer. Update skipped.")
#             return False

#     except Exception as e:
#         logging.error("Error processing node: %s", str(e))
#         return False

# def recursive_node_check(node, primary_keywords: Set[str], fallback_keywords: Optional[Set[str]], answer: str) -> bool:
#     """
#     Recursively checks all nodes starting from the given node.
#     """
#     if process_node(node, primary_keywords, fallback_keywords, answer):  # If the current node matches, update and stop recursion
#         return True

#     # Check children nodes
#     for child in node.get_children():
#         if recursive_node_check(child, primary_keywords, fallback_keywords, answer):
#             return True

#     return False

# def update_single_node_value(client: Client, answer: str, question: str) -> bool:
#     """
#     Applies the conditions to match each node's description against the given question and answer.
#     Updates the value of a matching node if the conditions are satisfied.
#     """
#     try:
#         # Extract keywords from the answer and question
#         answer_keywords = extract_keywords(answer)
#         question_keywords = extract_keywords(question)

#         logging.info("Answer Keywords: %s", answer_keywords)
#         logging.info("Question Keywords: %s", question_keywords)

#         # Determine primary and fallback keywords based on the length of the answer
#         if len(answer_keywords) <= 2:  # Short answer
#             primary_keywords = question_keywords
#             fallback_keywords = None
#         else:  # Longer answer
#             primary_keywords = answer_keywords
#             fallback_keywords = question_keywords

#         # Start the recursive check from the Objects node
#         objects_node = client.get_objects_node()
#         return recursive_node_check(objects_node, primary_keywords, fallback_keywords, answer)

#     except Exception as e:
#         logging.error("Error during update process: %s", str(e))
#         return False

# --------------------------------------> here we need provide FAISS Index

# import logging
# import re
# from opcua import Client, ua
# from typing import Optional, Set
# from langchain_community.vectorstores import FAISS
# import numpy as np
# from langchain.embeddings.openai import OpenAIEmbeddings
# import faiss

# # Initialize logging
# logging.basicConfig(level=logging.INFO)

# def connect_to_opcua_server(endpoint: str) -> Optional[Client]:
#     """Connects to the OPC UA server and returns the client instance if successful."""
#     client = Client(endpoint)
#     try:
#         client.connect()
#         logging.info("Connected to OPC UA Server at %s", endpoint)
#         return client
#     except Exception as e:
#         logging.error("Failed to connect to OPC UA Server: %s", str(e))
#         return None

# def get_all_opcua_tags(client: Client) -> dict:
#     """Get all tags from the OPC UA server."""
#     tags = {}
#     try:
#         # Get root node and the objects folder (adjust based on your server structure)
#         root = client.get_root_node()
#         objects = root.get_child(["0:Objects"])

#         # Process each node to get the description and NodeId
#         for node in objects.get_children():
#             if node.get_node_class() == ua.NodeClass.Variable:
#                 description = node.get_description()
#                 if description:
#                     tags[description.lower()] = node.nodeid  # Store description and node id
#                     logging.info("Found tag with description: %s, NodeID: %s", description, node.nodeid)
#         logging.info("All OPC UA tags fetched successfully.")
#     except Exception as e:
#         logging.error("Error fetching OPC UA tags: %s", str(e))
    
#     return tags

# def create_faiss_index(tags: dict) -> FAISS:
#     """Create a FAISS index from the tag descriptions."""
#     descriptions = list(tags.keys())
#     embeddings = np.array([OpenAIEmbeddings().embed_text(desc) for desc in descriptions]).astype('float32')
    
#     # Initialize FAISS index
#     dimension = embeddings.shape[1]  # Assuming embedding size is consistent
#     index = faiss.IndexFlatL2(dimension)
#     index.add(embeddings)
    
#     # Store the tags and their corresponding node IDs
#     faiss_index = FAISS(index=index, metadatas=descriptions, documents=list(tags.values()))
#     return faiss_index

# def extract_value_from_answer(answer: str) -> Optional[float]:
#     """Extract numerical value from the AI-generated answer."""
#     match = re.search(r'\b\d+(\.\d+)?\b', answer)  # Match integer or decimal number
#     if match:
#         return float(match.group(0))
#     return None

# def advanced_text_matching_with_faiss(answer: str, faiss_index: FAISS) -> Optional[ua.NodeId]:
#     """Match the answer with the tags using FAISS for advanced similarity search."""
#     try:
#         # Query the FAISS index with the answer embedding
#         embedding = OpenAIEmbeddings().embed_text(answer)
#         similar_tags = faiss_index.similarity_search_by_vector(embedding, k=1)  # Find most similar tag

#         if similar_tags:
#             best_match = similar_tags[0]
#             matched_description = best_match[0]  # Get the description of the most similar tag
#             node_id = best_match[1]  # Get the corresponding NodeId
#             logging.info("FAISS match found! Answer '%s' matches with tag description: '%s'", answer, matched_description)
#             return node_id
#         else:
#             logging.info("No similar tags found for answer: %s", answer)
#     except Exception as e:
#         logging.error("Error in FAISS matching: %s", str(e))
#     return None

# def update_opcua_tag_value(client: Client, node_id: ua.NodeId, value: float) -> bool:
#     """Update the value of the OPC UA tag."""
#     try:
#         # Retrieve the node using its node ID
#         node = client.get_node(node_id)
#         node.set_value(value)  # Set the new value
#         logging.info("Updated tag with Node ID '%s' with new value: %f", node_id, value)
#         return True
#     except Exception as e:
#         logging.error("Error in updating OPC UA tag value: %s", str(e))
#     return False

# def update_single_node_value(client: Client, answer: str, question: str, faiss_index: FAISS) -> bool:
#     """
#     This function matches the AI-generated answer with the tag descriptions and updates the corresponding OPC UA tag.
    
#     Args:
#     - client (Client): The OPC UA client to interact with the server.
#     - answer (str): The answer generated by the backend process (AI response).
#     - question (str): The original question that generated the answer (for logging purposes).
#     - faiss_index (FAISS): The FAISS index to perform similarity search for matching tags.
    
#     Returns:
#     - bool: Returns True if the tag was updated successfully, False otherwise.
#     """
#     try:
#         logging.info("Processing question: '%s', with answer: '%s'", question, answer)

#         # Match the AI answer with the appropriate OPC UA tag using FAISS
#         node_id = advanced_text_matching_with_faiss(answer, faiss_index)

#         if node_id:
#             # Extract numerical value from the answer (if any)
#             value = extract_value_from_answer(answer)
            
#             if value is not None:
#                 return update_opcua_tag_value(client, node_id, value)

#         logging.error("No matching tag found or valid value in answer. Exiting.")
#         return False
#     except Exception as e:
#         logging.error("Error in update_single_node_value: %s", str(e))
#         return False

# ---------------------------------------------> Here take global FAISS index.

# import logging
# import re
# from opcua import Client, ua
# from typing import Optional, Set
# from langchain_community.vectorstores import FAISS
# from langchain.embeddings.openai import OpenAIEmbeddings
# import numpy as np

# # Initialize logging
# logging.basicConfig(level=logging.INFO)

# # Global variable for FAISS index
# faiss_index = None

# def load_faiss_index(index_path: str):
#     """Load the FAISS index from a given path."""
#     global faiss_index
#     faiss_index = FAISS.load_local(index_path)  # Load your prebuilt FAISS index
#     logging.info("FAISS index loaded from: %s", index_path)

# def connect_to_opcua_server(endpoint: str) -> Optional[Client]:
#     """Connects to the OPC UA server and returns the client instance if successful."""
#     client = Client(endpoint)
#     try:
#         client.connect()
#         logging.info("Connected to OPC UA Server at %s", endpoint)
#         return client
#     except Exception as e:
#         logging.error("Failed to connect to OPC UA Server: %s", str(e))
#         return None

# def get_all_opcua_tags(client: Client) -> dict:
#     """Get all tags from the OPC UA server."""
#     tags = {}
#     try:
#         # Get root node and the objects folder (adjust based on your server structure)
#         root = client.get_root_node()
#         objects = root.get_child(["0:Objects"])

#         # Process each node to get the description and NodeId
#         for node in objects.get_children():
#             if node.get_node_class() == ua.NodeClass.Variable:
#                 description = node.get_description()
#                 if description:
#                     tags[description.lower()] = node.nodeid  # Store description and node id
#                     logging.info("Found tag with description: %s, NodeID: %s", description, node.nodeid)
#         logging.info("All OPC UA tags fetched successfully.")
#     except Exception as e:
#         logging.error("Error fetching OPC UA tags: %s", str(e))
    
#     return tags

# def extract_value_from_answer(answer: str) -> Optional[float]:
#     """Extract numerical value from the AI-generated answer."""
#     match = re.search(r'\b\d+(\.\d+)?\b', answer)  # Match integer or decimal number
#     if match:
#         return float(match.group(0))
#     return None

# def advanced_text_matching_with_faiss(answer: str) -> Optional[ua.NodeId]:
#     """Match the answer with the tags using FAISS for advanced similarity search."""
#     global faiss_index  # Use global FAISS index
#     if not faiss_index:
#         logging.error("FAISS index is not loaded.")
#         return None
    
#     try:
#         # Query the FAISS index with the answer embedding
#         embedding = OpenAIEmbeddings().embed_text(answer)
#         similar_tags = faiss_index.similarity_search_by_vector(embedding, k=1)  # Find most similar tag

#         if similar_tags:
#             best_match = similar_tags[0]
#             matched_description = best_match[0]  # Get the description of the most similar tag
#             node_id = best_match[1]  # Get the corresponding NodeId
#             logging.info("FAISS match found! Answer '%s' matches with tag description: '%s'", answer, matched_description)
#             return node_id
#         else:
#             logging.info("No similar tags found for answer: %s", answer)
#     except Exception as e:
#         logging.error("Error in FAISS matching: %s", str(e))
#     return None

# def update_opcua_tag_value(client: Client, node_id: ua.NodeId, value: float) -> bool:
#     """Update the value of the OPC UA tag."""
#     try:
#         # Retrieve the node using its node ID
#         node = client.get_node(node_id)
#         node.set_value(value)  # Set the new value
#         logging.info("Updated tag with Node ID '%s' with new value: %f", node_id, value)
#         return True
#     except Exception as e:
#         logging.error("Error in updating OPC UA tag value: %s", str(e))
#     return False

# def update_single_node_value(client: Client, answer: str, question: str) -> bool:
#     """
#     This function matches the AI-generated answer with the tag descriptions and updates the corresponding OPC UA tag.
    
#     Args:
#     - client (Client): The OPC UA client to interact with the server.
#     - answer (str): The answer generated by the backend process (AI response).
#     - question (str): The original question that generated the answer (for logging purposes).
    
#     Returns:
#     - bool: Returns True if the tag was updated successfully, False otherwise.
#     """
#     try:
#         logging.info("Processing question: '%s', with answer: '%s'", question, answer)

#         # Match the AI answer with the appropriate OPC UA tag using FAISS
#         node_id = advanced_text_matching_with_faiss(answer)

#         if node_id:
#             # Extract numerical value from the answer (if any)
#             value = extract_value_from_answer(answer)
            
#             if value is not None:
#                 return update_opcua_tag_value(client, node_id, value)

#         logging.error("No matching tag found or valid value in answer. Exiting.")
#         return False
#     except Exception as e:
#         logging.error("Error in update_single_node_value: %s", str(e))
#         return False

# -----------------------------------------> this is different

# import logging
# import re
# from opcua import Client, Node, ua
# from typing import Optional, Dict
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity
# import numpy as np

# # Initialize logging
# logging.basicConfig(level=logging.INFO)


# def connect_to_opcua_server(endpoint: str) -> Optional[Client]:
#     """Connects to the OPC UA server and returns the client instance if successful."""
#     client = Client(endpoint)
#     try:
#         client.connect()
#         logging.info("Connected to OPC UA Server at %s", endpoint)
#         return client
#     except Exception as e:
#         logging.error("Failed to connect to OPC UA Server: %s", str(e))
#         return None


# def fetch_all_tags_recursive(node: Node, tags: Dict[str, ua.NodeId]) -> None:
#     """Recursively fetch all tags (Variable nodes) and add them to the tags dictionary."""
#     try:
#         # Get all children of the current node
#         children = node.get_children()

#         for child in children:
#             node_class = child.get_node_class()
#             if node_class == ua.NodeClass.Variable:
#                 # If it's a Variable node (i.e., a tag), get its description and node ID
#                 description = child.get_description().Text.lower()
#                 if description:
#                     tags[description] = child.nodeid
#                     logging.info("Found tag: '%s', NodeID: %s", description, child.nodeid)
#             elif node_class == ua.NodeClass.Object:
#                 # If it's an Object node (folder), recursively fetch tags from it
#                 fetch_all_tags_recursive(child, tags)

#     except Exception as e:
#         logging.error("Error in fetching tags: %s", str(e))


# def get_all_opcua_tags(client: Client) -> Dict[str, ua.NodeId]:
#     """Get all tags from the OPC UA server by recursively traversing the folder hierarchy."""
#     tags = {}
#     try:
#         root = client.get_root_node()
#         objects_folder = root.get_child(["0:Objects"])  # Navigate to the "Objects" folder
#         fetch_all_tags_recursive(objects_folder, tags)
#         logging.info("All OPC UA tags fetched successfully.")
#     except Exception as e:
#         logging.error("Error fetching OPC UA tags: %s", str(e))
#     return tags


# def extract_value_from_answer(answer: str) -> Optional[float]:
#     """Extract numerical value from the AI-generated answer (basic regex)."""
#     match = re.search(r'\b\d+(\.\d+)?\b', answer)  # Match integer or decimal number
#     if match:
#         return float(match.group(0))
#     return None


# def advanced_text_matching(answer: str, tags: Dict[str, ua.NodeId]) -> Optional[ua.NodeId]:
#     """Match the answer with the tags based on advanced string matching (e.g., cosine similarity)."""
#     descriptions = list(tags.keys())
#     vectorizer = TfidfVectorizer().fit_transform([answer] + descriptions)

#     # Compute cosine similarity between the answer and each tag description
#     cosine_similarities = cosine_similarity(vectorizer[0:1], vectorizer[1:]).flatten()

#     # Find the tag with the highest similarity
#     max_similarity_idx = np.argmax(cosine_similarities)
#     if cosine_similarities[max_similarity_idx] > 0.5:  # Threshold for similarity
#         matched_description = descriptions[max_similarity_idx]
#         node_id = tags[matched_description]
#         logging.info("Advanced match found! Answer '%s' matches with tag: '%s'", answer, matched_description)
#         return node_id
#     else:
#         logging.info("No significant match found for answer: %s", answer)
#     return None


# def update_opcua_tag_value(client: Client, node_id: ua.NodeId, value: float) -> bool:
#     """Update the value of the OPC UA tag."""
#     try:
#         node = client.get_node(node_id)
#         node.set_value(value)
#         logging.info("Updated tag with Node ID '%s' with new value: %f", node_id, value)
#         return True
#     except Exception as e:
#         logging.error("Error in updating OPC UA tag value: %s", str(e))
#     return False


# def update_single_node_value(client: Client, answer: str, question: str) -> bool:
#     """
#     Match the AI-generated answer with the tag descriptions and update the corresponding OPC UA tag.
#     """
#     try:
#         logging.info("Processing question: '%s', with answer: '%s'", question, answer)

#         # Get all OPC UA tags from the server
#         tags = get_all_opcua_tags(client)

#         # Match the AI answer with the appropriate OPC UA tag
#         node_id = advanced_text_matching(answer, tags)

#         if node_id:
#             # Extract numerical value from the answer (if any)
#             value = extract_value_from_answer(answer)
#             if value is not None:
#                 return update_opcua_tag_value(client, node_id, value)

#         logging.error("No matching tag found or valid value in answer. Exiting.")
#         return False
#     except Exception as e:
#         logging.error("Error in update_single_node_value: %s", str(e))
#         return False


import logging
import re
from opcua import Client, Node, ua
from typing import Optional, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

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


def fetch_all_tags_recursive(node: Node, tags: Dict[str, ua.NodeId]) -> None:
    """Recursively fetch all tags (Variable nodes) and add them to the tags dictionary."""
    try:
        # Get all children of the current node
        children = node.get_children()

        for child in children:
            node_class = child.get_node_class()
            if node_class == ua.NodeClass.Variable:
                # If it's a Variable node (i.e., a tag), get its description and node ID
                description = child.get_description().Text.lower()
                if description:
                    tags[description] = child.nodeid
                    logging.info("Found tag: '%s', NodeID: %s", description, child.nodeid)
            elif node_class == ua.NodeClass.Object:
                # If it's an Object node (folder), recursively fetch tags from it
                fetch_all_tags_recursive(child, tags)

    except Exception as e:
        logging.error("Error in fetching tags: %s", str(e))


def get_all_opcua_tags(client: Client) -> Dict[str, ua.NodeId]:
    """Get all tags from the OPC UA server by recursively traversing the folder hierarchy."""
    tags = {}
    try:
        root = client.get_root_node()
        objects_folder = root.get_child(["0:Objects"])  # Navigate to the "Objects" folder
        fetch_all_tags_recursive(objects_folder, tags)
        logging.info("All OPC UA tags fetched successfully.")
    except Exception as e:
        logging.error("Error fetching OPC UA tags: %s", str(e))
    return tags


def extract_value_from_text(text: str) -> Optional[float]:
    """Extract numerical value from text (basic regex)."""
    match = re.search(r'\b\d+(\.\d+)?\b', text)  # Match integer or decimal number
    if match:
        return float(match.group(0))
    return None


def advanced_text_matching(text: str, tags: Dict[str, ua.NodeId]) -> Optional[ua.NodeId]:
    """Match text with the tags based on advanced string matching (e.g., cosine similarity)."""
    descriptions = list(tags.keys())
    vectorizer = TfidfVectorizer().fit_transform([text] + descriptions)

    # Compute cosine similarity between the text and each tag description
    cosine_similarities = cosine_similarity(vectorizer[0:1], vectorizer[1:]).flatten()

    # Find the tag with the highest similarity
    max_similarity_idx = np.argmax(cosine_similarities)
    if cosine_similarities[max_similarity_idx] > 0.5:  # Threshold for similarity
        matched_description = descriptions[max_similarity_idx]
        node_id = tags[matched_description]
        logging.info("Advanced match found! Text '%s' matches with tag: '%s'", text, matched_description)
        return node_id
    else:
        logging.info("No significant match found for text: %s", text)
    return None


def update_opcua_tag_value(client: Client, node_id: ua.NodeId, value: float) -> bool:
    """Update the value of the OPC UA tag."""
    try:
        node = client.get_node(node_id)
        node.set_value(value)
        logging.info("Updated tag with Node ID '%s' with new value: %f", node_id, value)
        return True
    except Exception as e:
        logging.error("Error in updating OPC UA tag value: %s", str(e))
    return False


def update_single_node_value(client: Client, answer: str, question: str) -> bool:
    """
    Match the AI-generated answer or the question with the tag descriptions
    and update the corresponding OPC UA tag.
    """
    try:
        logging.info("Processing question: '%s', with answer: '%s'", question, answer)

        # Get all OPC UA tags from the server
        tags = get_all_opcua_tags(client)

        # Match the AI answer or the question with the appropriate OPC UA tag
        node_id = advanced_text_matching(answer, tags) or advanced_text_matching(question, tags)

        if node_id:
            # Extract numerical value from the answer (if any)
            value = extract_value_from_text(answer) or extract_value_from_text(question)
            if value is not None:
                return update_opcua_tag_value(client, node_id, value)

        logging.error("No matching tag found or valid value in answer/question. Exiting.")
        return False
    except Exception as e:
        logging.error("Error in update_single_node_value: %s", str(e))
        return False
