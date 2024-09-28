import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.file_loader import extract_text_from_pdf, extract_text_from_markdown
from utils.utils import split_content, enrich_chunks
from utils.embeddings import generate_embeddings
from utils.vector_search import setup_faiss_vector_store
from utils.utils import get_recognized_airlines

logger = logging.getLogger(__name__)

def process_file(file_path, airline_name):
    try:
        if file_path.suffix.lower() == '.pdf':
            text, links = extract_text_from_pdf(file_path)
        elif file_path.suffix.lower() == '.md':
            text, links = extract_text_from_markdown(file_path)
        else:
            logger.warning(f"Unsupported file type: {file_path}")
            return []

        chunks = split_content(text)
        enriched_chunks = enrich_chunks(chunks, file_path.name, links, airline_name)
        return enriched_chunks

    except Exception as e:
        logger.error(f"Error processing file {file_path}: {e}")
        return []

def ingest_documents(directory):
    all_chunks = []
    directory_path = Path(directory)

    with ThreadPoolExecutor() as executor:
        futures = []
        for airline_folder in directory_path.iterdir():
            if airline_folder.is_dir():
                airline_name = airline_folder.stem
                for file_path in airline_folder.rglob("*"):
                    futures.append(executor.submit(process_file, file_path, airline_name))

        for future in as_completed(futures):
            result = future.result()
            if result:
                all_chunks.extend(result)

    # Generate embeddings and setup FAISS vector store
    texts = [chunk['text'] for chunk in all_chunks]
    embeddings = generate_embeddings(texts)
    vector_store = setup_faiss_vector_store(all_chunks)
    recognized_airlines = get_recognized_airlines(vector_store)
    return vector_store, recognized_airlines

