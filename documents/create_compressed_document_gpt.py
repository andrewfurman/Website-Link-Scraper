# the create_compressed_document_gpt(document_id int) function will use the OpenAI API to create a compressed document from the full text of the document.

# this function will use the full_contents field of the document table to create a compressed document using the OpenAI API. This function will send chunks of the full document in 100 page segments.  This will be done by scanning the full_contents field for the page delimiters shown as "🅿️ Start Page 1" "🅿️ Start Page 2" and so on.  It will use these delimiters to split the document into chunks of 100 page segements and request an updated summary of each page in the chunk. The chunk returned will keep the "🅿️ Page 1 Summary: " "🅿️Page 2 Summary: " and so on.

from sqlalchemy import create_engine, true
from sqlalchemy.orm import sessionmaker
import os
import re
import json
import sys
from openai import OpenAI

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from documents.documents_model import Document

client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

def split_into_pages(full_contents):
    if not full_contents:
        return []
    pages = re.split(r'🅿️ Start Page \d+', full_contents)
    if pages and not pages[0].strip():
        pages.pop(0)
    return pages

def create_segments(pages, segment_size=100):
    return [pages[i:i + segment_size] for i in range(0, len(pages), segment_size)]

def get_page_summaries(segment, base_page_num):
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "You are an AI assistant tasked with creating concise 100-word summaries for each page of a document."
            },
            {
                "role": "user",
                "content": f"Create a 100-word summary for each of these pages:\n\n{' '.join(segment)}"
            }
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "page_summaries",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "page_summaries": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "page_number": {"type": "integer"},
                                    "page_summary": {"type": "string"}
                                },
                                "required": ["page_number", "page_summary"],
                                "additionalProperties": False
                            }
                        }
                    },
                    "required": ["page_summaries"],
                    "additionalProperties": False
                }
            }
        }
    }
    
    print("\nSending this payload to OpenAI:")
    print(json.dumps(payload, default=str, indent=2))

    # Get the response from OpenAI
    response = client.chat.completions.create(**payload)

    print("\nRaw response from OpenAI:")
    print(f"Response type: {type(response)}")
    print(f"Response dir: {dir(response)}")
    print("\nResponse choices:")
    for choice in response.choices:
        print(f"\nChoice: {choice}")
        print(f"Choice type: {type(choice)}")
        print(f"Choice dir: {dir(choice)}")
        print(f"\nMessage content: {choice.message.content}")
        print(f"Content type: {type(choice.message.content)}")

    # Now try to parse the JSON
    print("\nAttempting to parse JSON from response...")
    parsed_response = json.loads(response.choices[0].message.content)

    return parsed_response

def create_compressed_document_gpt(document_id):
    engine = create_engine(os.environ['DATABASE_URL'])
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        document = session.query(Document).filter(Document.id == document_id).first()
        if not document or not document.full_contents:
            return "Error: Document not found or empty."

        pages = split_into_pages(document.full_contents)
        segments = create_segments(pages)
        compressed_content = []

        for segment_index, segment in enumerate(segments):
            base_page_num = segment_index * 100
            summaries = get_page_summaries(segment, base_page_num)
            
            for summary in summaries['page_summaries']:
                compressed_content.append(
                    f"🅿️ Page {summary['page_number']} Summary: {summary['page_summary']}"
                )

        document.compressed_document = "\n\n".join(compressed_content)
        session.commit()
        return f"Success: Created compressed document for ID {document_id}"

    except Exception as e:
        session.rollback()
        return f"Error: {str(e)}"
    finally:
        session.close()

# Add this at the end of your create_compressed_document_gpt.py file

if __name__ == "__main__":
    document_id = 22
    result = create_compressed_document_gpt(document_id)
    print(result)