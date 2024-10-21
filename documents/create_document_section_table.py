# create_document_section_table.py

# create_sample_document_section.py

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from documents.documents_model import Document, DocumentSection

def create_sample_section():
    # Set up database connection
    engine = create_engine(os.environ['DATABASE_URL'])
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Query for an existing document
        document = session.query(Document).first()

        if document:
            # Create a sample DocumentSection
            sample_section = DocumentSection(
                document_id=document.id,
                start_page=1,
                end_page=5,
                document_text="This is a sample section of the document. It contains important information about the topic at hand.",
                custom_prompt="Summarize the key points in this section."
            )

            # Add the section to the database and commit the changes
            session.add(sample_section)
            session.commit()

            print(f"Sample section created for document: {document.title}")
            print(f"Section ID: {sample_section.id}")
            print(f"Start Page: {sample_section.start_page}")
            print(f"End Page: {sample_section.end_page}")
        else:
            print("No documents found in the database. Please add a document first.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        session.rollback()

    finally:
        session.close()

if __name__ == "__main__":
    create_sample_section()