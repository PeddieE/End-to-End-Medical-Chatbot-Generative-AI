import os
import nest_asyncio
from llama_parse import LlamaParse
from llama_index.core.schema import Document # For type hinting if needed

# Apply nest_asyncio if you're running this in an environment that has issues
# with nested event loops (like Jupyter notebooks or some IDEs)
nest_asyncio.apply()

# --- Option 1: Basic Parsing (Will try to parse the whole file) ---
# It's good to try this first, as the 750-page limit might have some buffer.
def parse_single_pdf(file_path: str, api_key: str = None) -> list[Document]:
    """Parses a single PDF file using LlamaParse."""
    if api_key:
        os.environ["LLAMA_CLOUD_API_KEY"] = api_key # Set if not already in env

    parser = LlamaParse(
        result_type="markdown",  # "markdown" is usually best for RAG
        verbose=True,            # See parsing progress
        language="en",           # Specify language for better OCR
        # Add num_workers for concurrent parsing if you split the file
        # num_workers=4, # Use if you pass a list of files or for 'partition_pages'
    )
    print(f"Parsing {file_path}...")
    documents = parser.load_data(file_path)
    print(f"Finished parsing. Got {len(documents)} documents (pages/chunks).")
    return documents

# --- Option 2: Parsing with Page Partitioning (Recommended for large files near limits) ---
# This explicitly tells LlamaParse to split the document into smaller jobs.
# You might need to adjust 'partition_pages' based on testing.
def parse_large_pdf_with_partitioning(file_path: str, api_key: str = None, page_limit: int = 100) -> list[Document]:
    """Parses a large PDF file by splitting it into smaller partitions for LlamaParse."""
    if api_key:
        os.environ["LLAMA_CLOUD_API_KEY"] = api_key

    parser = LlamaParse(
        result_type="markdown",
        verbose=True,
        language="en",
        num_workers=4, # Use multiple workers to process partitions concurrently
        partition_pages=page_limit # Split large documents into partitions of up to this many pages
    )
    print(f"Parsing {file_path} with page partitioning ({page_limit} pages per partition)...")
    documents = parser.load_data(file_path)
    print(f"Finished parsing. Got {len(documents)} documents (pages/chunks).")
    return documents

# --- Main execution block ---
if __name__ == "__main__":
    pdf_file_path = "Data/The_GALE_ENCYCLOPEDIA_of_MEDICINE_SECOND.pdf"  # Make sure your PDF is here
    # If you set LLAMA_CLOUD_API_KEY as an environment variable, you don't need to pass it here.
    # Otherwise, uncomment and replace with your key:
    # my_api_key = "llx-YOUR_ACTUAL_API_KEY_HERE"

    # Try Option 1 first to see if it handles 759 pages directly
    # documents = parse_single_pdf(pdf_file_path)

    # If Option 1 fails or for robustness, use Option 2
    # You might try page_limit=700 or even smaller like 100 or 200
    documents = parse_large_pdf_with_partitioning(pdf_file_path, page_limit=700)


    # Now 'documents' contains the parsed content, usually one LlamaIndex Document object per page/chunk
    # You can access the text content and other metadata
    for i, doc in enumerate(documents):
        print(f"--- Document/Page {i+1} ---")
        # The 'text' attribute contains the extracted content
        print(doc.text[:500]) # Print first 500 characters of each document/page
        print("\n" + "="*50 + "\n")

    # You can then save the extracted text to a file
    # Or integrate 'documents' directly into your LlamaIndex RAG pipeline
    with open("gale_encyclopedia_parsed.md", "w", encoding="utf-8") as f:
        for i, doc in enumerate(documents):
            f.write(f"# Page {i+1}\n\n") # Or other suitable separator
            f.write(doc.text + "\n\n")
            f.write("---\n\n") # Separator between pages/chunks

    print("\nParsed content saved to gale_encyclopedia_parsed.md")
