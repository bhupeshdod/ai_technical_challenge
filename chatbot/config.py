import os
from dotenv import load_dotenv

load_dotenv()

# Define any additional configuration here, e.g., file paths or API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

STORAGE_PATH = os.getenv("STORAGE_PATH")
if not os.path.exists(STORAGE_PATH):
    os.makedirs(STORAGE_PATH) 

# File path for saving the FAISS index and documents
FAISS_INDEX_PATH = STORAGE_PATH + '/faiss_index.index'
DOCUMENTS_PATH = STORAGE_PATH + '/documents.pkl'
DOCSTORE_MAPPING_PATH = STORAGE_PATH + '/index_to_docstore_id.pkl'