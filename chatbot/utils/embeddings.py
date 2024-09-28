from openai import OpenAI
import time
from concurrent.futures import ThreadPoolExecutor
from openai import OpenAIError, RateLimitError
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

# Function to generate embeddings for a batch of documents
def generate_embeddings(texts, batch_size=100):
    embeddings = []
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(generate_batch_embeddings, texts[i:i+batch_size]) for i in range(0, len(texts), batch_size)]
        for future in futures:
            embeddings.extend(future.result())
    return embeddings

# Helper function to generate embeddings for a batch with retry on failure
def generate_batch_embeddings(batch):
    try:
        response = client.embeddings.create(input=batch, model="text-embedding-ada-002")
        return [item.embedding for item in response.data]
    except RateLimitError:  # Correct exception class
        time.sleep(5)
        return generate_batch_embeddings(batch)
    except OpenAIError as e:  # Catch any other OpenAI-related errors
        print(f"OpenAI API error: {e}")
        return []