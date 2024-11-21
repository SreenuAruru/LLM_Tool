from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware 
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
import os
import uuid
import logging
from pydantic import BaseModel
from dotenv import load_dotenv
import mysql.connector
from typing import List, Dict, Optional

from opcua_client import connect_to_opcua_server, update_single_node_value

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
app = FastAPI()

# OPC_UA_SERVER_ENDPOINT = os.getenv("OPC_UA_SERVER_ENDPOINT")
OPC_UA_SERVER_ENDPOINT = "opc.tcp://127.0.0.1:4841/llmtool/server/"

# Setup logging
logging.basicConfig(level=logging.INFO)

# Define a model for the database credentials
class DBCredentials(BaseModel):
    host: Optional[str] = "localhost"
    user: str
    password: str
    database: Optional[str] = "iadb"

class ModelSelection(BaseModel):
    ai_model: str
    api_key_model: str

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

VECTORSTORE_DIR = "vectorstores"
os.makedirs(VECTORSTORE_DIR, exist_ok=True)

async def update_opcua_node(user_question, answer):
    """API endpoint to update the OPC UA node based on the question and its answer."""
    try:
        # Step 1: Fetch answer by invoking ask_question function
        if not answer:
            return {"message": "Failed to retrieve answer for the provided question."}

        # Step 2: Connect to the OPC UA server
        client = connect_to_opcua_server(OPC_UA_SERVER_ENDPOINT)
        print("_______________________________--------------->")
        if client is None:
            raise HTTPException(status_code=500, detail="Failed to connect to OPC UA Server")

        # Step 3: Find node by display name (or other identifier) and update based on the answer
        update_success = update_single_node_value(client, answer, user_question)
        client.disconnect()
        
        if update_success:
            logging.info("Disconnected from OPC UA Server.")
            return {"message": "Node updated successfully based on the question and answer."}
        else:
            return {"message": "No matching node found for the provided question."}

    except Exception as e:
        logging.error(f"Error during OPC UA node update: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating OPC UA node: {str(e)}")


db_credentials = None

# Function to establish a database connection using provided credentials
def get_db_connection(credentials: DBCredentials):
    try:
        print(f"Connecting to MySQL server: {credentials.host}")
        conn = mysql.connector.connect(
            host=credentials.host,
            user=credentials.user,
            password=credentials.password,
        )
        print("Connection established successfully.")
        return conn
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to MySQL server: {str(e)}")

# Endpoint to set database credentials and create database if it doesn't exist
@app.post("/set-database-credentials/")
async def set_database_credentials(credentials: DBCredentials):
    global db_credentials
    db_credentials = credentials  # Store the credentials for future use

    # Connect to MySQL to create database if it doesn't exist
    try:
        conn = get_db_connection(credentials)
        cursor = conn.cursor()

        # Check if database exists, create if it doesn't
        print(f"Checking if database '{credentials.database}' exists.")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {credentials.database}")
        print(f"Database '{credentials.database}' checked/created.")

        # Switch to the created database
        cursor.execute(f"USE {credentials.database}")
        print(f"Using database '{credentials.database}'.")

        # Check if table exists, create if it doesn't
        table_name = "model_selection"
        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ai_model VARCHAR(255) NOT NULL,
            api_key_model VARCHAR(255) NOT NULL
        )
        """)
        print(f"Table '{table_name}' checked/created.")

        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "Database and table setup completed successfully"}
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Error setting up database: {str(e)}")

@app.post("/store-model-selection/")
async def store_model_selection(model_selection: ModelSelection):
    if not db_credentials:
        raise HTTPException(status_code=400, detail="Database credentials are not set")

    try:
        # Connect to the database and insert data
        conn = get_db_connection(db_credentials)
        cursor = conn.cursor()
        cursor.execute(f"USE {db_credentials.database}")
        
        # Insert the model selection into the table
        cursor.execute(
            "INSERT INTO model_selection (ai_model, api_key_model) VALUES (%s, %s)",
            (model_selection.ai_model, model_selection.api_key_model)  # Use model_selection attributes
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"message": "Model selection stored successfully"}
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Error storing model selection: {str(e)}")


# Endpoint to retrieve stored model selections
@app.get("/fetch-model-selection/")
async def fetch_model_selection():
    if not db_credentials:
        raise HTTPException(status_code=400, detail="Database credentials are not set")

    try:
        # Connect to the database and fetch data
        conn = get_db_connection(db_credentials)
        cursor = conn.cursor()
        cursor.execute(f"USE {db_credentials.database}")
        
        cursor.execute("SELECT * FROM model_selection")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return {"model_selections": [{"id": row[0], "ai_model": row[1], "api_key_model": row[2]} for row in rows]}
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Error fetching model selection: {str(e)}")

# Endpoint to clear database credentials (optional)
@app.post("/clear-database-credentials/")
async def clear_database_credentials():
    global db_credentials
    db_credentials = None
    return {"message": "Database credentials cleared successfully"}

async def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        try:
            await pdf.seek(0)
            pdf_reader = PdfReader(pdf.file)
            for page in pdf_reader.pages:
                page_text = page.extract_text() or ""
                text += page_text
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error reading PDF file: {pdf.filename}, {str(e)}")
    return text

def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    return text_splitter.split_text(text)

def create_and_save_vectorstore(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(api_key=GOOGLE_API_KEY, model="models/embedding-001")
    vectorstore = FAISS.from_texts(text_chunks, embedding=embeddings)
    unique_id = str(uuid.uuid4())
    vectorstore.save_local(os.path.join(VECTORSTORE_DIR, unique_id))
    return unique_id

def load_vectorstore(store_id, user_api_key, ai_model_name):
    vectorstore_path = os.path.join(VECTORSTORE_DIR, store_id)
    if not os.path.exists(vectorstore_path):
        raise HTTPException(status_code=404, detail="Vectorstore not found for this ID")

    if "gemini" in ai_model_name.lower():
        embeddings = GoogleGenerativeAIEmbeddings(api_key=user_api_key, model="models/embedding-001")
    else:
        embeddings = OpenAIEmbeddings(api_key=user_api_key)
    
    vectorstore = FAISS.load_local(vectorstore_path, embeddings, allow_dangerous_deserialization=True)
    return vectorstore

@app.post("/process-pdfs/")
async def process_pdfs(files: List[UploadFile] = File(...)):
    try:
        raw_text = await get_pdf_text(files)
        text_chunks = get_text_chunks(raw_text)
        store_id = create_and_save_vectorstore(text_chunks)
        return {"message": "PDFs processed and stored successfully", "store_id": store_id}
    except Exception as e:
        logging.error(f"Error during PDF processing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing PDFs: {str(e)}")

@app.post("/ask-question/")
async def ask_question(
    store_id: str = Form(None),
    user_question: str = Form(...),
    user_api_key: str = Form(...),
    ai_model_name: str = Form(...)
):
    try:
        if store_id:
            vectorstore = load_vectorstore(store_id, user_api_key, ai_model_name)
            retriever = vectorstore.as_retriever()
            docs = retriever.get_relevant_documents(user_question)

            if not docs:
                return {"response": "No relevant documents found for your question."}

            context = "\n".join([doc.page_content for doc in docs])
            prompt = f"Context:\n{context}\n\nQuestion: {user_question}\n\nAnswer:"
        else:
            prompt = f"Question: {user_question}\n\nAnswer:"
        
        if "gemini" in ai_model_name.lower():
            model = ChatGoogleGenerativeAI(model=ai_model_name, api_key=user_api_key)
            chain = load_qa_chain(model, chain_type="stuff")
            response = chain.invoke({"input_documents": docs if store_id else [], "question": user_question})
            answer = response["output_text"]
            await update_opcua_node(user_question, answer)
        else:
            model = ChatOpenAI(ai_model_name=ai_model_name, api_key=user_api_key)
            response = model.invoke(prompt)
            answer = response if isinstance(response, str) else response.get("output_text", "No answer found.")
            await update_opcua_node(user_question, answer)

        return {"response": answer}
        
    except Exception as e:
        logging.error(f"Error during query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error running query: {str(e)}")

@app.post("/validate-api-key/")
async def validate_api_key(api_key: str = Form(...)):
    try:
        OpenAIEmbeddings(api_key=api_key).embed_documents(["test"])
        return {"message": "API Key is valid"}
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid API Key")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
