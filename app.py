import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from pathlib import Path
import logging

from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import FlashrankRerank
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_qdrant import Qdrant
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_groq import ChatGroq
from llama_parse import LlamaParse

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Load API keys from environment variables
os.environ["GROQ_API_KEY"] = "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"  # Replace with your actual key
os.environ["LLAMA_PARSE"] = "llx-rmhI0mWxwbbF1Xef3wzyuDyWZroiok0dsoFRCfr1iiDOIZu0"  # Replace with your actual key

def ensure_directories_exist(directories):
    for directory in directories:
        path = Path(directory)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            logger.info("Directory created: %s", path)
        else:
            logger.info("Directory already exists: %s", path)

class SimpleDocument:
    def __init__(self, page_content, metadata=None):
        self.page_content = page_content
        self.metadata = metadata if metadata else {}

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Flask API!"})

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"message": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400

    file_path = os.path.join('uploads', file.filename)
    file.save(file_path)

    response_message = process_pdf(file_path)
    return jsonify({"message": response_message}), 200

def process_pdf(file_path):
    instruction = """The provided document is Meta First Quarter 2024 Results.
    This form provides detailed financial information about the company's performance for a specific quarter.
    It includes unaudited financial statements, management discussion and analysis, and other relevant disclosures required by the SEC.
    It contains many tables.
    Try to be precise while answering the questions"""
    
    parser = LlamaParse(
        api_key=os.getenv("LLAMA_PARSE"),
        result_type="markdown",
        parsing_instruction=instruction,
        max_timeout=5000,
    )

    try:
        logger.info(f"Sending file {file_path} to LlamaParse for processing.")
        llama_parse_documents = parser.load_data(file_path)
        logger.info(f"LlamaParse response received.")

        if not llama_parse_documents:
            logger.error("No documents returned from LlamaParse")
            return "Error processing file: No documents parsed"

        parsed_doc = llama_parse_documents[0]

        document_path = Path("data/parsed_document.md")
        with document_path.open("w") as f:
            f.write(parsed_doc.text)

        if not document_path.exists():
            logger.error("Parsed document file was not saved.")
            return "Error processing file: Parsed document file was not saved."

        logger.info("File processed successfully and saved to %s", document_path)
        return "File processed successfully!"
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        return f"Error processing file: {e}"

@app.route('/query', methods=['GET'])
def query():
    question = request.args.get('question', '')
    if not question:
        return jsonify({"answer": "No question provided"}), 400
    response = handle_query(question)
    return jsonify({"answer": response})

def handle_query(question):
    try:
        document_path = Path("data/parsed_document.md")
        if not document_path.exists():
            logger.error("Parsed document not found.")
            return "Parsed document not found. Please upload and process a document first."

        logger.info(f"Document path: {document_path}, Exists: {document_path.exists()}")
        
        # Read the document content directly
        logger.info("Loading document content...")
        try:
            with document_path.open("r") as f:
                content = f.read()  # Read the entire content for processing
                logger.info(f"Document content loaded. Content length: {len(content)}")
        except Exception as e:
            logger.error(f"Error reading document content: {e}")
            return f"Error reading document content: {e}"

        # Split the document into chunks manually
        logger.info("Splitting document into chunks...")
        try:
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=2048, chunk_overlap=128)
            chunks = text_splitter.split_text(content)
            docs = [SimpleDocument(chunk) for chunk in chunks]
            logger.info(f"Documents split into {len(docs)} chunks.")
        except Exception as e:
            logger.error(f"Error splitting documents: {e}")
            return f"Error splitting documents: {e}"

        # Generate embeddings
        logger.info("Generating embeddings...")
        try:
            embeddings = FastEmbedEmbeddings()
            qdrant = Qdrant.from_documents(
                docs,
                embeddings,
                path="./db",
                collection_name="document_embeddings",
            )
            logger.info("Embeddings created and stored in Qdrant.")
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return f"Error generating embeddings: {e}"

        # Create retriever with ContextualCompressionRetriever
        try:
            retriever = qdrant.as_retriever(search_kwargs={"k": 5})
            compressor = FlashrankRerank()
            compression_retriever = ContextualCompressionRetriever(base_retriever=retriever, base_compressor=compressor)
        except Exception as e:
            logger.error(f"Error creating compression retriever: {e}")
            return f"Error creating compression retriever: {e}"

        # Create PromptTemplate and RetrievalQA chain
        try:
            prompt_template = """
            Use the following pieces of information to answer the user's question.
            If you don't know the answer, just say that you don't know, don't try to make up an answer.

            Context: {context}
            Question: {question}

            Answer the question and provide additional helpful information,
            based on the pieces of information, if applicable. Be succinct.

            Responses should be properly formatted to be easily read.
            """

            prompt = PromptTemplate(
                template=prompt_template, input_variables=["context", "question"]
            )

            llm = ChatGroq(temperature=0, model_name="llama3-70b-8192")

            qa = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=compression_retriever,
                return_source_documents=True,
                chain_type_kwargs={"prompt": prompt, "verbose": True},
            )

            logger.info("QA chain created successfully.")

            # Generate response using the QA chain
            response = qa.invoke(question)
            logger.info(f"Response generated using QA chain: {response}")
            return response['result']
        except Exception as e:
            logger.error(f"Error creating QA chain or generating response: {e}")
            return f"Error creating QA chain or generating response: {e}"

    except Exception as e:
        logger.error(f"Error handling query: {e}")
        return f"Error handling query: {e}"

if __name__ == '__main__':
    # Ensure necessary directories exist
    ensure_directories_exist(['uploads', 'data', './db'])
    
    app.run(host='0.0.0.0', port=8000, debug=True)
