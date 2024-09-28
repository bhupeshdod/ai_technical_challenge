from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from langchain_community.docstore import InMemoryDocstore
import faiss
import os
import pickle
from config import FAISS_INDEX_PATH, DOCUMENTS_PATH, DOCSTORE_MAPPING_PATH, STORAGE_PATH
import logging
from utils.utils import get_recognized_airlines

logger = logging.getLogger(__name__)

def setup_faiss_vector_store(documents):
    embedding_model = OpenAIEmbeddings(model="text-embedding-ada-002")
    
    # Convert documents into LangChain-compatible format with airline name and other metadata
    langchain_documents = [
        Document(page_content=doc['text'], metadata=doc['metadata'])
        for doc in documents
    ]
    
    # Create the FAISS vector store
    vector_store = FAISS.from_documents(langchain_documents, embedding_model)
    
    # Save the vector store, documents, and index_to_docstore_id to disk
    save_faiss_vector_store(vector_store)
    
    return vector_store

def save_faiss_vector_store(vector_store):
    if not os.path.exists(STORAGE_PATH):
        os.makedirs(STORAGE_PATH) 
    
    # Save FAISS index to disk
    faiss.write_index(vector_store.index, FAISS_INDEX_PATH)
    
    # Save the docstore to disk
    with open(DOCUMENTS_PATH, 'wb') as f:
        # Save the internal dictionary of the docstore
        pickle.dump(vector_store.docstore._dict, f)

    # Save the index_to_docstore_id mapping to disk
    with open(DOCSTORE_MAPPING_PATH, 'wb') as f:
        pickle.dump(vector_store.index_to_docstore_id, f)

def load_faiss_vector_store():
    if not os.path.exists(FAISS_INDEX_PATH) or not os.path.exists(DOCUMENTS_PATH) or not os.path.exists(DOCSTORE_MAPPING_PATH):
        return None, []

    # Load FAISS index from disk
    faiss_index = faiss.read_index(FAISS_INDEX_PATH)

    # Load the index_to_docstore_id mapping
    with open(DOCSTORE_MAPPING_PATH, 'rb') as f:
        index_to_docstore_id = pickle.load(f)

    # Load the docstore data
    with open(DOCUMENTS_PATH, 'rb') as f:
        docstore_dict = pickle.load(f)

    # Reconstruct the docstore
    docstore = InMemoryDocstore(docstore_dict)

    # Recreate the FAISS vector store
    embedding_function = OpenAIEmbeddings(model="text-embedding-ada-002")
    vector_store = FAISS(embedding_function, index=faiss_index, docstore=docstore, index_to_docstore_id=index_to_docstore_id)
    recognized_airlines = get_recognized_airlines(vector_store)
    return vector_store, recognized_airlines
