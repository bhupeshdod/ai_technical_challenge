import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from langchain.text_splitter import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

def get_recognized_airlines(vector_store):
    if isinstance(vector_store, tuple):
        vector_store = vector_store[0]  # Unpack the first element
    recognized_airlines = set()
    for doc_id, doc in vector_store.docstore._dict.items():
        airline_name = doc.metadata.get('airline_name', None)
        if airline_name:
            recognized_airlines.add(airline_name)
    return list(recognized_airlines)

def split_content(text, chunk_size=500, chunk_overlap=50):
    if not text:
        return []

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
    )
    chunks = text_splitter.split_text(text)
    return chunks

def enrich_chunks(chunks, file_name, links, airline_name):
    if not chunks:
        return []
    enriched_chunks = []

    try:
        # Fit TfidfVectorizer on all chunks
        vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(chunks)
        feature_names = vectorizer.get_feature_names_out()
    except Exception as e:
        logger.error(f"Error fitting TfidfVectorizer: {e}")
        return enriched_chunks

    for i, chunk in enumerate(chunks):
        try:
            # Get the TF-IDF vector for the chunk
            tfidf_vector = tfidf_matrix[i]
            # Get top keywords based on TF-IDF score
            sorted_indices = tfidf_vector.toarray()[0].argsort()[::-1]
            top_n = 5
            top_indices = sorted_indices[:top_n]
            keywords = [feature_names[index] for index in top_indices if tfidf_vector[0, index] > 0]

            enriched_chunks.append({
                'text': chunk,
                'metadata': {
                    'file_name': file_name,
                    'keywords': keywords,
                    'links': links,
                    'airline_name': airline_name
                }
            })
        except Exception as e:
            logger.error(f"Error enriching chunk: {e}")

    return enriched_chunks

def process_chat_history(chat_history):
    processed_chat_history = []
    for entry in chat_history:
        sender = entry.get('sender')
        message = entry.get('message', '')
        if sender == 'user':
            processed_chat_history.append({'user': message, 'bot': ''})
        elif sender == 'bot':
            if processed_chat_history:
                processed_chat_history[-1]['bot'] = message
            else:
                processed_chat_history.append({'user': '', 'bot': message})
        else:
            logger.warning(f'Unexpected chat history entry: {entry}')
    return processed_chat_history
