# summarize_document_gpt.py

# This function will call the OpenAI API to summarize a document using the gpt-4o-mini model.

# This function will first update the word_count and page_count fields in the document table for the given document_id by calculating the number of words and pages in the document full_contents field.

# we will add the chat_gpt functionality later (do not create this now)

# summarize_document_gpt.py

# summarize_document_gpt.py

import os
import sys
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from documents.documents_model import Document

def update_document_counts(session, document):
    if document.full_contents:
        # Update word count
        document.word_count = len(document.full_contents.split())
        
        # Calculate page count based on "🅿️ Start Page" markers
        page_markers = re.findall(r'🅿️ Start Page \d+', document.full_contents)
        document.page_count = len(page_markers)
        
        # If no page markers found, use the previous estimation method
        if document.page_count == 0:
            document.page_count = (document.word_count + 499) // 500
    
    session.commit()

def summarize_document_gpt(document_id):
    # Set up database connection
    engine = create_engine(os.environ['DATABASE_URL'])
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Query the document from the database
        document = session.query(Document).filter(Document.id == document_id).first()

        if not document:
            return f"Error: Document with ID {document_id} not found."

        # Update word count and page count
        update_document_counts(session, document)

        # Placeholder for future OpenAI API call
        # TODO: Implement OpenAI API call to summarize the document using gpt-4o-mini model

        return f"Success: Document counts updated for document ID {document_id}. Word count: {document.word_count}, Page count: {document.page_count}. Summary functionality to be implemented."

    except Exception as e:
        session.rollback()
        return f"Error: {str(e)}"

    finally:
        session.close()

# You can call the function like this if you want to run it directly:
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python summarize_document_gpt.py <document_id>")
    else:
        document_id = int(sys.argv[1])
        result = summarize_document_gpt(document_id)
        print(result)