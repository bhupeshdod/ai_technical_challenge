from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from pathlib import Path
from langchain_core.output_parsers import StrOutputParser
from langchain.schema.runnable import RunnableLambda, RunnableMap
import logging
import re

# Set up logging to debug issues
logger = logging.getLogger(__name__)

llm = ChatOpenAI(model_name="gpt-4o", temperature=0)

def get_query_answer(question, vector_store, chat_history, recognized_airlines):
    # Prepare the conversation context
    conversation_history = "\n".join(
        [f"User: {entry['user']}\nBot: {entry['bot']}" for entry in chat_history]
    ) if chat_history else ""

    # Define the retriever
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})

    # Define the function to format documents
    def format_docs(documents):
        formatted_docs = []
        for doc in documents:
            content = doc.page_content
            formatted_docs.append(content)
        return "\n\n".join(formatted_docs)

    # Create the custom prompt template
    prompt_template = """You are a friendly and knowledgeable airline expert specializing in policies for the following airlines: {airlines}.
            Your task is to provide human-like, conversational answers to the user's questions, summarizing important details and making sure the response is easy to understand.
            Ensure that you refer to the previous conversation when answering, especially if no airline is mentioned.
            You should give clear and concise information with a warm, approachable tone.
            The answer should be from the relevant context; do not generate information that is not present in the documents.
            Whenever relevant, you can point to external links or additional resources.
            Remember to clarify when needed, but do so naturally, and avoid repeating information unnecessarily.
            If the user asks for more details, provide them in small, digestible sections, but don't overwhelm them with too much information at once.
            Structure your response so that it feels like a real conversation rather than a factual dump.
            After providing your answer, suggest 2-3 relevant follow-up short questions the user might ask next, under a heading 'Suggested Questions', formatted as a bullet list.

            {conversation_history}

            Context:
            {context}

            Question:
            {question}

            Answer:"""

    custom_rag_prompt = PromptTemplate(
        input_variables=["airlines", "conversation_history", "context", "question"],
        template=prompt_template
    )

    rag_chain = (
        RunnableMap({
            "context": RunnableLambda(lambda x: retriever.get_relevant_documents(x["question"])) | format_docs,
            "airlines": RunnableLambda(lambda x: x["airlines"]),
            "conversation_history": RunnableLambda(lambda x: x["conversation_history"]),
            "question": RunnableLambda(lambda x: x["question"])
        })
        | custom_rag_prompt
        | llm
        | StrOutputParser()
    )

    # Prepare inputs
    inputs = {
        "airlines": ', '.join(recognized_airlines),
        "conversation_history": conversation_history,
        "question": question
    }

    # Invoke the chain
    try:
        answer = rag_chain.invoke(inputs)
    except Exception as e:
        logger.error(f"Error invoking the chain: {e}")
        return "I'm sorry, but I couldn't process your request at this time.", [], []

    # Get the source documents
    source_documents = retriever.get_relevant_documents(question)

    if 'Suggested Questions' in answer:
        answer_text, suggested_questions_section = answer.split('Suggested Questions', 1)
        # Extract the quick replies from the bullet list
        quick_replies = re.findall(r"-\s*(.*)", suggested_questions_section)
    else:
        answer_text = answer
        quick_replies = []

    # Serialize metadata for JSON compatibility
    def serialize_metadata(metadata):
        serialized_metadata = {}
        for key, value in metadata.items():
            if isinstance(value, Path):
                logging.debug(f"Converting PosixPath to string: {value}")
                serialized_metadata[key] = str(value)
            else:
                serialized_metadata[key] = str(value)
        return serialized_metadata

    processed_source_documents = []
    links_section = ""

    for doc in source_documents:
        serialized_metadata = serialize_metadata(doc.metadata)

        # Format the hyperlinks in markdown
        if 'links' in serialized_metadata:
            links = serialized_metadata['links']
            if isinstance(links, list):
                if not links_section:
                    links_section = "\n\n**Additional Resources**\n\nHere are some helpful links:\n"
                for link in links:
                    if isinstance(link, tuple) and len(link) == 2:
                        title, url = link
                        links_section += f"- [{title}]({url})\n"
                    elif isinstance(link, str):
                        links_section += f"- {link}\n"
                    else:
                        logging.warning(f"Unrecognized link format: {link}")

        processed_source_documents.append({
            'content': doc.page_content,
            'metadata': serialized_metadata
        })

    # Append links to the answer if any
    if links_section:
        answer += links_section

    return answer_text.strip(), processed_source_documents, quick_replies
