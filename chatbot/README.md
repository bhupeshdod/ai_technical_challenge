## Technical Challenge: LLM Airline Policy App

# Airline Policy App

This project is a Flask-based web application that leverages OpenAI's GPT-4o and FAISS for answering questions about airline policies. Users can submit queries, and the system retrieves the most relevant documents from stored policies and uses an LLM to answer them.

## Table of Contents
- [Technologies Used](#technologies-used)
- [Setup and Running Instructions](#setup-and-running-instructions)
- [Design Choices](#design-choices)
- [Challenges and Resolutions](#challenges-and-resolutions)

## Technologies Used

1. **Flask**: For building the web application.
2. **OpenAI GPT-4**: Used for generating answers to user queries.
3. **FAISS**: For storing and retrieving vector embeddings of the policy documents.
4. **Memcached**: For session management.
5. **Docker**: For containerizing the application and ensuring it runs consistently.
6. **Docker Compose**: For orchestrating the application and its services.

## Setup and Running Instructions

### Prerequisites:
- Ensure **Docker** and **Docker Compose** are installed on your machine.

### Steps to run the app:

1. **Clone the Repository**:
    ```bash
    gh repo clone bhupeshdod/ai_technical_challenge
    cd chatbot_app
    ```

2. **Configure Your OpenAI API Key**:
   Replace `openai_api_key` in the `docker-compose.yaml` file with actual OpenAI API key. Alternatively, you can pass it as an environment variable when running Docker Compose.

3. **Build and Run the Application**:
    Run the following command to build and start both the Flask app and Memcached services:
    ```bash
    docker-compose up --build
    ```

4. **Access the Application**:
    Once the app is running, open your browser and go to:
    ```
    http://localhost:5000
    ```

5. **Stopping the Application**:
    To stop the application and remove containers:
    ```bash
    docker-compose down
    ```

### Other Useful Docker Commands:
- **Rebuild and Restart**: If you make changes to the code and want to rebuild:
    ```bash
    docker-compose up --build
    ```
- **View Logs**: Check logs from the running containers:
    ```bash
    docker-compose logs
    ```

## Design Choices

1. **Use of OpenAI GPT-4**: The LLM is a key component, enabling the system to answer user questions based on the retrieved policy documents. GPT-4 was chosen for its ability to handle complex natural language queries.
   
2. **FAISS Vector Store**: FAISS was used for document retrieval because it offers fast, efficient similarity searches, crucial for quickly finding the most relevant policy documents.

3. **Memcached for Session Management**: Memcached was chosen to handle session data efficiently, allowing the app to maintain user state and query history.

4. **Dockerization**: Docker was used to package the app, ensuring that it can run consistently across different environments. Docker Compose simplifies the process by orchestrating the Flask app and Memcached services together.

5. **Modular Code Design**: The application is designed in a modular way, with separate components for document ingestion, embeddings, querying, and retrieval. This improves maintainability and allows for easier scaling in the future.

## Challenges and Resolutions

1. **Handling Large Policy Documents**:
    - **Challenge**: Many policy documents are large, and embedding them as a whole is inefficient.
    - **Solution**: The documents are split into smaller chunks during ingestion, making it easier to process them in manageable portions while retaining contextual information.

2. **PDF Text Extraction**:
    - **Challenge**: Some PDFs contain images instead of text, which made text extraction difficult.
    - **Solution**: We implemented OCR using **PyTesseract** to extract text from image-based PDFs.

3. **Session Persistence**:
    - **Challenge**: Ensuring user session persistence across interactions.
    - **Solution**: We integrated **Memcached** to store session data, allowing user history to persist between queries.

4. **Rate Limits with OpenAI API**:
    - **Challenge**: Encountered rate limits when generating embeddings or querying the LLM.
    - **Solution**: Implemented retries with backoff for handling rate limits when interacting with the OpenAI API.

5. **Vector Search Optimization**:
    - **Challenge**: Finding the most relevant documents quickly.
    - **Solution**: We optimized vector searches using FAISS, which allows fast retrieval of similar document chunks based on user queries.

---

### Conclusion
This application leverages modern technologies such as **OpenAI's GPT-4o**, **FAISS**, and **Memcached** to provide a robust, efficient platform for querying airline policies. The use of **Docker** ensures that the app runs consistently across environments, while **Docker Compose** simplifies the setup by orchestrating the necessary services.

Feel free to reach out with any questions or suggestions for improvements!



### Re-Ingesting Documents or Ingesting New Data

The system allows you to re-ingest documents (for example, if you’ve updated the policy documents or added new ones) through a dedicated ingestion process. Follow the steps below to re-ingest or ingest new documents:

#### 1. Prepare Your Data

- Ensure that your policy documents are either in **Markdown (.md)** or **PDF (.pdf)** format.
- Organize your documents in a directory (for example, `/new_policies` or update the existing `/policies` directory).
- The system will ingest all documents in the specified directory recursively, including any subdirectories.

#### 2. Trigger the Ingestion Process

You can trigger the ingestion either via an API call or directly through the UI (if you've added a button). The system will process the documents, split them into chunks, generate embeddings, and store them in the FAISS vector store.

##### Option 1: Triggering Ingestion via API

You can trigger the ingestion process by making a **POST** request to the `/ingest` endpoint. The default directory is `/policies`, but you can specify any other directory as a parameter.

- **Endpoint**: `/ingest`
- **Method**: `POST`
- **Parameters**:
  - `directory`: The directory containing the policy documents (default: `policies`).

For example:

```bash
curl -X POST http://localhost:5000/ingest -d "directory=policies"
curl -X POST http://localhost:5000/ingest
