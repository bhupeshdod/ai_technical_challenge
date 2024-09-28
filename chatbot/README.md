# Airline Policy Chatbot - Technical Challenge Submission

I have developed an interactive chatbot application that allows users to inquire about airline policies using natural language. Using OpenAI's GPT-4o model and FAISS vector database, the chatbot delivers precise and contextually relevant answers based on official airline policy documents.

## Table of Contents

- [Features](#features)
- [Setup and Running Instructions](#setup-and-running-instructions)
- [Usage](#usage)
- [Data Ingestion](#data-ingestion)
- [Technologies and Design Choices](#technologies-and-design-choices)
- [Challenges Encountered and Solutions](#challenges-encountered-and-solutions)
- [Conclusion](#conclusion)

## Features

- **Interactive Chat Interface**: An interactive web interface built with Flask for user interaction with airline policies in natural language.
- **Advanced LLM Integration**: Leverages OpenAI's GPT-4o with Langchain's retrieval for natural language understanding and generation of human-like responses.
- **Comprehensive Document Processing**: Extracts text from PDF and Markdown formats, including OCR support for scanned PDFs using PyTesseract.
- **Efficient Vector Database**: Implements Langchain's vector store FAISS for storing and retrieving document embeddings, ensuring rapid and relevant similarity searches.
- **Suggested Follow-up Questions**: Dynamically generates related follow-up questions to enhance user engagement.
- **Session Management**: Uses Memcached to store user sessions and preserve chat history across interactions.
- **Dockerized Deployment**: Provides a Dockerfile and Docker Compose configuration for easy setup and consistent deployment.

## Setup and Running Instructions

### Prerequisites

- Install **Docker** and **Docker Compose** on your machine.

### Steps to Run the Application

1. **Clone the Repository**

    ```bash
    git clone https://github.com/bhupeshdod/ai_technical_challenge.git
    cd ai_technical_challenge/chatbot
    ```

2. **Configure Environment Variables**

    - Create a `.env` file in the root directory with your OpenAI API key:

      ```bash
      OPENAI_API_KEY="your_openai_api_key"
      ```

    - The FAISS index and associated data are stored in the `index` directory by default. You can change this by modifying the `STORAGE_PATH` in the Dockerfile.

3. **Build and Run the Application**

    - Build and start the Flask app and Memcached services using Docker Compose:

      ```bash
      docker-compose up --build
      ```

4. **Access the Application**

    - Open your browser and navigate to:

      ```bash
      http://localhost:5000
      ```

5. **Stopping the Application**

    - To stop the application and remove containers:

      ```bash
      docker-compose down
      ```

## Usage

Once the application is running, you can interact with the chatbot by asking questions related to airline policies,
The chatbot will provide context-aware responses based on the ingested policy documents and offer relevant follow-up questions.

## Data Ingestion

### Re-Ingesting Documents or Ingesting New Data

To update the policy documents or ingest new data, follow the steps below:

1. **Prepare Your Data**
    - Ensure your documents are in **Markdown (.md)** or **PDF (.pdf)** format.
    - Place your files in the `/policies` directory or any other directory you'd like to use.

2. **Trigger the Ingestion Process**
    - You can trigger the ingestion process by making a **POST** request to the `/ingest` endpoint.

    Example:

    ```bash
    curl -X POST http://localhost:5000/ingest -d "directory=policies"
    ```

    - If you don't specify a `directory`, it defaults to the `/policies` folder.

## Technologies and Design Choices

### Document Processing
- **Text Extraction**: To handle various policy documents, I used `pdfplumber` for extracting text from PDFs and incorporated `pytesseract` for OCR when dealing with scanned images or text-light PDFs. This ensured thorough extraction of data from diverse document formats.
- **Markdown Parsing**: Markdown files were processed using `markdown` and `BeautifulSoup`, converting them into HTML for easy text and link extraction.

### Suggested Follow-up Questions
- **Follow up Question**: Based on the previous user queries, the LLM will generate similar next 2-3 questions for user to select from the web interface.

### Vector Database and Search
- **FAISS**: I used Langchain's vectorstore FAISS for its speed and efficiency in handling large vector embeddings, along with Langchain's Runnable retrieval for relevant docuemnts extraction.

### Web Framework
- **Flask**: I used Flask for its simplicity and flexibility, allowing for rapid development of the web interface and back-end services.

### Session Management
- **Memcached**: I integrated Memcached to manage session data, ensuring efficient storage and retrieval of user sessions and preserving chat history for a smooth, contextual user experience.

## Challenges Encountered and Solutions

### 1. Extracting Text from PDFs and Link's from markdown
- **Challenge**: Pdfs documents contain images and the markdown contains tables, hyperlinks.
- **Solution**: By integrated OCR through `pytesseract` to handle image-based PDFs, using BeautifulSoup to extarct the links and passing it through the prompt to include these in answers if required.

### 2. Session Persistence
- **Challenge**: Certain user queries don't have any airline specified or there could be questions that are followed up on certain response, the model was giving general information for that.
- **Solution**: I extracted airines names extracted from the folders and stored them in metadata along with keywords, filenames. Memcached for session management, with the last 5 conversations passed along with relevant context and a good prompt to RAG chain.

### 3. Optimizing Vector Search
- **Challenge**: Quickly retrieving relevant document chunks based on user queries.
- **Solution**: Leveraged FAISS to optimize vector search, langchain's runnable chain and defining the prompt helped in retrieveing relevant information, and providing human-like, conversational answers to the user's questions.

### 4. User Interface Improvements
- **Challenge**: Aligning user messages, follow up suggestions, errors and chat history.
- **Solution**: I initially started building user interface using Gradio as it is easy to use and provides good interface. Considering my requirements, I thought of building a customised web interface using gpt and after few prompts I was able to get an interactive user interface to improve user experience.

## Conclusion

This submission reflects my enthusiasm for AI-driven solutions and my commitment to delivering high-quality results. I look forward to further opportunities to contribute to innovative initiatives within the Flight Center AI Center of Excellence.

Thank you for reviewing my submission!

---

Feel free to reach out with any questions or feedback. I'm excited to contribute to the Flight Center AI Center of Excellence!
