# app.py

# --- IMPORTS ---
from flask import Flask, render_template, jsonify, request
from src.helper import download_hugging_face_embeddings
from langchain_pinecone import PineconeVectorStore
from langchain_openai import ChatOpenAI # Use ChatOpenAI for chat models
# REMOVED: These older chain imports are not used with LCEL
# from langchain.chains import create_retrieval_chain
# from langchain.chains.combine_documents import create_stuff_documents_chain

# Import necessary LCEL prompt components
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser # To parse LLM output to string

from dotenv import load_dotenv
from src.prompt import system_message_content # Ensure system_message_content is correctly imported
import os
import datetime
# NEW IMPORT: Required for itemgetter
from operator import itemgetter
import traceback # For detailed error logging

# --- FLASK APP INITIALIZATION ---
app = Flask(__name__)

# --- ENVIRONMENT VARIABLES & API KEYS ---
load_dotenv()
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# --- EMBEDDINGS & VECTORSTORE ---
embeddings = download_hugging_face_embeddings()
index_name = "medicalbot"
docsearch = PineconeVectorStore.from_existing_index(
    index_name = index_name,
    embedding = embeddings
)

# --- LLM & RAG CHAIN SETUP (LCEL IMPLEMENTATION) ---
retriever = docsearch.as_retriever(search_type="similarity", search_kwargs={"k":10})

#llm = ChatOpenAI(temperature=0.4, max_tokens=500)
llm = ChatOpenAI(temperature=0.3, max_tokens=500)

# Define the content for the human (user) message
# This now contains the context, input, AND the crucial output formatting instruction
human_message_content = (
    "**Context:**\n{context}\n\n"  # Context is explicitly here
    "**Question:** {input}\n\n"    # The user's question
    "**Provide the answer directly, starting immediately with the first word of the answer. Do not include any prefixes, labels, or conversational intros like 'Bot:', 'Answer:', 'AI:', 'System:', 'Here is the answer:', or similar.**"
)

# Create the System and Human message templates using the content strings
system_message_prompt = SystemMessagePromptTemplate.from_template(system_message_content)
human_message_prompt = HumanMessagePromptTemplate.from_template(human_message_content)

# Build the final chat prompt template from these structured messages
prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

# --- LCEL RAG Chain Definition ---
# THIS IS THE CRUCIAL CHANGE TO FIX THE EMBEDDING ERROR
rag_chain = (
    {
        "context": itemgetter("input") | retriever, # Pass only 'input' (user_text) to the retriever
        "input": RunnablePassthrough(),              # Pass the original 'input' (user_text) through
    }
    | prompt
    | llm
    | StrOutputParser()
)


# --- WEB APPLICATION ROUTES ---

@app.route("/")
def index():
    current_year = datetime.datetime.now().year
    return render_template('chat.html', year=current_year)

@app.route("/get", methods=["POST"])
# app.py

# ... (all your imports and initial setup code, including the new 'from operator import itemgetter' and 'import traceback') ...

@app.route("/get", methods=["POST"])
def get_bot_response():
    user_text = request.json.get("query")
    print(f"DEBUG: Received message from user: '{user_text}' (via JSON)")

    if not user_text:
        print("DEBUG: User text (from JSON) is empty.")
        return jsonify({"response": "Please enter a message."})

    try:
        # --- START DEBUGGING MODIFICATION ---
        # Step 1: Explicitly invoke the retriever to see its output
        retrieved_docs = retriever.invoke(user_text)

        print(f"\nDEBUG: Retrieved {len(retrieved_docs)} documents for query: '{user_text}'")
        if not retrieved_docs:
            print("DEBUG: Retriever returned no documents.")
        for i, doc in enumerate(retrieved_docs):
            print(f"DEBUG: Doc {i+1} (Source: {doc.metadata.get('source', 'N/A')}, Score: {doc.metadata.get('score', 'N/A')}): {doc.page_content[:400]}...\n") # Print more characters and score
        # --- END DEBUGGING MODIFICATION ---

        # Step 2: Join the retrieved documents to form the context string for the prompt
        # Ensure the chain's input format matches what's expected: {"context": ..., "input": ...}
        context_for_llm = "\n\n".join([doc.page_content for doc in retrieved_docs])

        # Step 3: Invoke the rag_chain with the explicit context and input
        # Note: We're temporarily bypassing the itemgetter in rag_chain for this manual debugging.
        # This will be reverted later.
        raw_response_from_chain = rag_chain.invoke({"input": user_text, "context": context_for_llm})


        # --- Existing robust type checking for bot_response ---
        if isinstance(raw_response_from_chain, str):
            bot_response = raw_response_from_chain
        elif isinstance(raw_response_from_chain, dict) and "answer" in raw_response_from_chain:
            bot_response = str(raw_response_from_chain["answer"])
        else:
            print(f"ERROR: Unexpected raw_response_from_chain type: {type(raw_response_from_chain)}. Value: {raw_response_from_chain}")
            bot_response = "I encountered an unexpected response format. Please try again."
        # --- End of robust type checking ---

        print(f"DEBUG: Final bot_response before sending: '{bot_response}'")

        if not bot_response or bot_response.strip() == "I'm sorry, I cannot answer this question based on the provided medical documents. Please ask me about medical topics.":
            print("DEBUG: bot_response is empty or is the fallback message. This means the RAG chain couldn't find/infer an answer.")
            return jsonify({"response": bot_response if bot_response else "I couldn't find a relevant answer in the documents."})

        return jsonify({"response": bot_response})

    except Exception as e:
        import traceback
        print(f"ERROR: Exception in /get route: {e}")
        traceback.print_exc()
        return jsonify({"response": "I'm sorry, I encountered a critical error. Please try again."})

# ... (rest of your app.py code) ...f


# --- NEW: ABOUT PAGE ROUTE ---
@app.route('/about')
def about():
    """Renders the about page."""
    current_year = datetime.datetime.now().year # Pass year to about.html too
    return render_template('about.html', year=current_year) # Make sure you have about.html!

# --- RUN APP ---
if __name__ == '__main__':
    app.run(debug=True, port=8080)