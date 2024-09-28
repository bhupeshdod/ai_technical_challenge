from flask import Flask, request, jsonify, render_template, session, g
from utils.ingestion import ingest_documents
from utils.query_handler import get_query_answer
from flask_caching import Cache
from flask_session import Session
from utils.vector_search import load_faiss_vector_store
from utils.utils import process_chat_history
import bmemcached
import secrets
import logging
from utils.logging_config import setup_logging
import os

# Set the logging level to INFO or WARNING to reduce verbosity
setup_logging(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure Memcached for session management
app.config['SECRET_KEY'] = secrets.token_hex(16)  # Generates a 32-character hexadecimal string
app.config['SESSION_TYPE'] = 'memcached'  # Use Memcached for session management
app.config['SESSION_PERMANENT'] = False  # Session will not be permanent
app.config['SESSION_USE_SIGNER'] = True  # Sign session to prevent tampering
app.config['SESSION_KEY_PREFIX'] = 'chatbot_'  # Prefix to prevent key collisions

# Configure Memcached server
memcached_server = os.environ.get('MEMCACHED_SERVER', '127.0.0.1:11211')
app.config['SESSION_MEMCACHED'] = bmemcached.Client([memcached_server])

# Initialize session with Flask
Session(app)

# Cache configuration (optional, using simple cache here for quick access)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Load the FAISS vector store when the application starts
with app.app_context():
    vector_store, recognized_airlines  = load_faiss_vector_store()
    if vector_store is None:
        logger.warning('Vector store not found. Please ingest documents.')
    else:
        g.vector_store = vector_store
        g.recognized_airlines = recognized_airlines

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ingest', methods=['POST'])
def ingest():
    try:
        directory = request.form.get('directory', 'policies')  # Default to 'policies' directory
        vector_store, recognized_airlines = ingest_documents(directory)
        # Store in application context
        g.vector_store = vector_store
        g.recognized_airlines = recognized_airlines
        return jsonify({'message': 'Documents ingested and embeddings generated successfully.'})
    except Exception as e:
        logger.error(f'Error during ingestion: {e}')
        return jsonify({'error': 'Error during ingestion.'}), 500

@app.route('/query', methods=['POST'])
def query():
    vector_store, recognized_airlines = load_faiss_vector_store()
    if vector_store is None:
        logger.warning('Vector store not found. Please ingest documents.')
        return jsonify({'error': 'No documents ingested. Please run ingestion first.'}), 400
    else:
        g.vector_store = vector_store
        g.recognized_airlines = recognized_airlines

    data = request.json
    query_text = data.get('question')
    chat_history = data.get('chat_history', [])

    try:
        # Retrieve the session's chat history or initialize an empty list
        session_chat_history = session.get('chat_history', [])

        # Process chat history
        processed_chat_history = process_chat_history(chat_history)
        # Merge session chat history with the incoming one
        processed_chat_history = session_chat_history + processed_chat_history

        # Get the bot's answer
        answer, source_documents, quick_replies = get_query_answer(
            query_text, vector_store, processed_chat_history, recognized_airlines
        )

        # Update session chat history
        processed_chat_history.append({'user': query_text, 'bot': answer})
        session['chat_history'] = processed_chat_history[-5:]

        # Return the answer and quick replies
        return jsonify({'answer': answer, 'quickReplies': quick_replies})
    except Exception as e:
        logger.error(f'Error processing query: {e}')
        return jsonify({'error': 'Error processing query.'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)