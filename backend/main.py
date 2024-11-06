from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.chains import ConversationalRetrievalChain
from langchain.chains.question_answering import load_qa_chain
import os
import uuid
import logging
from pydantic import BaseModel
from dotenv import load_dotenv
import mysql.connector
from typing import List, Dict

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

app = FastAPI()

# Setup logging
logging.basicConfig(level=logging.INFO)

# db_config = {
#     "host": "localhost",
#     "user": "root",
#     "password": "SreenuAruru@2640",
#     "database": "iadb"
# }

# conn = mysql.connector.connect(**db_config)
# cursor = conn.cursor()

class DBCredentials(BaseModel):
    host: str
    user: str
    password: str
    database: str
    
# Define a model for POST request body
class ModelSelection(BaseModel):
    ai_model: str
    model_api_key: str


# Allow CORS for React frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

VECTORSTORE_DIR = "vectorstores"
os.makedirs(VECTORSTORE_DIR, exist_ok=True)

# @app.post("/set-database-credentials/")
# async def set_database_credentials(db_credential: DBCredentials):
#     try:
#         # Take only the first object from the provided credentials
#         first_credential = db_credential
#         # Database configuration from the first object
#         db_config = {
#             "host": first_credential.host,
#             "user": first_credential.user,
#             "password": first_credential.password,
#             "database": first_credential.database
#         }
       
#         # Connect to the database with the dynamic credentials
#         conn = mysql.connector.connect(**db_config)
#         cursor = conn.cursor()
        

#         # Return success response if connection works
#         return {"message": "Database connection established successfully", "db_config": db_config}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error connecting to database: {str(e)}")


# # POST endpoint to store model selection
# @app.post("/store-model-selection/")
# async def store_model_selection(model_selection: ModelSelection):
#     try:
#         # Insert into MySQL table
#         sql = "INSERT INTO model_selection (ai_model, model_api_key) VALUES (%s, %s)"
#         values = (model_selection.ai_model, model_selection.model_api_key)
#         cursor.execute(sql, values)
#         conn.commit()
#         return {"message": "Model selection stored successfully"}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error storing model selection: {str(e)}")


db_credentials = None

# Helper function to connect to the database using stored credentials
def get_db_connection():
    if db_credentials is None:
        raise HTTPException(status_code=400, detail="Database credentials are not set")
    try:
        conn = mysql.connector.connect(
            host=db_credentials.host,
            user=db_credentials.user,
            password=db_credentials.password,
            database=db_credentials.database
        )
        return conn
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to database: {str(e)}")

# POST endpoint to set the database credentials
@app.post("/set-database-credentials/")
async def set_database_credentials(db_credential: DBCredentials):
    global db_credentials
    db_credentials = db_credential  # Store the credentials for future use
    try:
        # Establish a connection to test the credentials
        conn = mysql.connector.connect(
            host=db_credentials.host,
            user=db_credentials.user,
            password=db_credentials.password,
            database=db_credentials.database
        )
        
        return {"message": "Database connection established successfully", "db_config": db_credentials.dict()}
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to database: {str(e)}")


@app.post("/clear-database-credentials/")
async def clear_database_credentials():
    global db_credentials
    db_credentials = None  # Clear the stored credentials
    return {"message": "Database credentials cleared successfully"}


# POST endpoint to store model selection in the database
@app.post("/store-model-selection/")
async def store_model_selection(model_selection: ModelSelection):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert into MySQL table
        sql = "INSERT INTO model_selection (ai_model, model_api_key) VALUES (%s, %s)"
        values = (model_selection.ai_model, model_selection.model_api_key)
        cursor.execute(sql, values)
        conn.commit()
        return {"message": "Model selection stored successfully"}
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Error storing model selection: {str(e)}")

# GET endpoint to fetch model selection
@app.get("/fetch-model-selection/")
async def fetch_model_selection():
    try:
        # Fetch from MySQL table
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM model_selection")
        rows = cursor.fetchall()
        if not rows:
            return {"message": "No model selection data found"}
        return {"model_selections": [{"id":row[0],"ai_model": row[1], "model_api_key": row[2]} for row in rows]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching model selection: {str(e)}")


# Function to read PDF files and extract text
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

# Function to split text into chunks
def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    return text_splitter.split_text(text)

# Function to create and persist a vector store using Google Gemini embeddings
def create_and_save_vectorstore(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(api_key=GOOGLE_API_KEY, model="models/embedding-001")
    vectorstore = FAISS.from_texts(text_chunks, embedding=embeddings)
    unique_id = str(uuid.uuid4())
    vectorstore.save_local(os.path.join(VECTORSTORE_DIR, unique_id))
    return unique_id

# Function to load an existing vector store
def load_vectorstore(store_id, user_api_key, model_name):
    vectorstore_path = os.path.join(VECTORSTORE_DIR, store_id)
    if not os.path.exists(vectorstore_path):
        raise HTTPException(status_code=404, detail="Vectorstore not found for this ID")

    # Use the appropriate embeddings model based on the user's selection
    if "gemini" in model_name.lower():
        embeddings = GoogleGenerativeAIEmbeddings(api_key=user_api_key, model="models/embedding-001")
    else:
        embeddings = OpenAIEmbeddings(api_key=user_api_key)
    
    vectorstore = FAISS.load_local(vectorstore_path, embeddings, allow_dangerous_deserialization=True)
    return vectorstore

# API to handle file upload and processing using Gemini for embeddings
@app.post("/process-pdfs/")
async def process_pdfs(files: list[UploadFile] = File(...)):
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
    store_id: str = Form(None),  # Allow store_id to be optional for general questions
    user_question: str = Form(...),
    user_api_key: str = Form(...),
    model_name: str = Form(...)
):
    try:
        if store_id:  # If store_id is provided, load the vector store
            vectorstore = load_vectorstore(store_id, user_api_key, model_name)
            retriever = vectorstore.as_retriever()
            logging.info(f"Loaded vector store for store_id: {store_id} using model: {model_name}")

            # Retrieve documents
            docs = retriever.get_relevant_documents(user_question)
            logging.info(f"Retrieved documents: {docs}")
            logging.info(f"Number of retrieved documents: {len(docs)}")

            if not docs:
                return {"response": "No relevant documents found for your question."}

            context = "\n".join([doc.page_content for doc in docs])
            prompt = f"""
            Based on the context below, answer the following question:
            Context:
            {context}

            Question: {user_question}

            Answer:
            """
        else:  # For general questions, just use the AI model without retrieving documents
            prompt = f"""
            Answer the following question:
            Question: {user_question}

            Answer:
            """
        
        logging.info(f"Generated prompt: {prompt}")

        # Handle different models based on user's choice
        if "gemini" in model_name.lower():
            model = ChatGoogleGenerativeAI(model=model_name, api_key=user_api_key)
            chain = load_qa_chain(model, chain_type="stuff")
            response = chain.invoke({"input_documents": [] if not store_id else docs, "question": user_question})
            answer = response["output_text"]
        else:
            model = ChatOpenAI(model_name=model_name, api_key=user_api_key)
            response = model.invoke(prompt)
            answer = response if isinstance(response, str) else response.get("output_text", "No answer found.")

        logging.info(f"Answer generated: {answer}")
        return {"response": answer}

    except Exception as e:
        logging.error(f"Error during query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error running query: {str(e)}")


# Validation endpoint for checking the API key
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