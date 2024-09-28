## Technical Challenge: LLM Airline Policy App

As part of the Flight Center AI Center of Excellence technical challenge, I have developed an interactive chatbot application that enables users to ask questions about airline policies. Leveraging advanced language models and efficient vector search techniques, the application provides accurate and contextually relevant answers based on official policy documents of various airlines.

## Table of Contents

- [Features](#features)
- [Technologies and Design Choices](#technologies-and-design-choices)
- [Setup and Installation](#setup-and-installation)
- [Running the Application](#running-the-application)
- [Usage](#usage)
- [Data Ingestion](#data-ingestion)
- [Challenges Encountered and Solutions](#challenges-encountered-and-solutions)
- [Conclusion](#conclusion)

## Features

- **Interactive Chat Interface**: A user-friendly web interface built with Flask, allowing users to ask natural language questions about airline policies.
- **LLM Integration**: Utilizes OpenAI's GPT-4 model for understanding queries and generating human-like responses.
- **Document Processing**: Extracts and preprocesses text from airline policy documents in PDF and Markdown formats, including OCR support for scanned PDFs.
- **Vector Database**: Implements FAISS for efficient storage and retrieval of document embeddings, enabling quick similarity searches.
- **Contextual Awareness**: Maintains conversation history to provide contextually relevant answers.
- **Suggested Follow-up Questions**: Enhances user engagement by offering relevant follow-up questions based on the conversation.
- **Session Management**: Uses Memcached for managing user sessions and preserving chat history across interactions.
- **Dockerized Deployment**: Provides a Dockerfile and `docker-compose.yaml` for easy setup and deployment of the application.

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
