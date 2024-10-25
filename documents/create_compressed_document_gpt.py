# the create_compressed_document_gpt(document_id int) function will use the OpenAI API to create a compressed document from the full text of the document.

# this function will use the full_contents field of the document table to create a compressed document using the OpenAI API. This function will send chunks of the full document in 20 page segments.  This will be done by scanning the full_contents field for the page delimiters shown as "🅿️ Start Page 1" "🅿️ Start Page 2" and so on.  It will use these delimiters to split the document into chunks of 20 page segements and request an updated summary of each page in the chunk. The chunk returned will keep the "🅿️ Page 1 Summary: " "🅿️Page 2 Summary: " and so on.

from sqlalchemy import create_engine, true
from sqlalchemy.orm import sessionmaker
import os
import re
import json
import sys
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from documents.documents_model import Document

client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

def split_into_pages(full_contents):
    if not full_contents:
        return []
    # Use positive lookbehind to keep the page markers
    pages = re.split(r'(?=🅿️ Start Page \d+)', full_contents)
    # Remove empty first element if it exists
    if pages and not pages[0].strip():
        pages.pop(0)
    return pages

def create_segments(pages, segment_size):
    return [pages[i:i + segment_size] for i in range(0, len(pages), segment_size)]

def get_page_summaries(segment, base_page_num):
    # Extract page numbers from the segment text to use in the summary
    page_numbers = [int(num) for num in re.findall(r'🅿️ Start Page (\d+)', ''.join(segment))]
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "You are a dilligent document research expert tasked with creating concise 50-word summaries for each page of a document."
            },
            {
                "role": "user",
                "content": f"Create a 50-word summary for each of these pages, This is an exerpt from a larger document that needs to be summarized. Please preserve the origianl page numbers found in this document text:\n\n{' '.join(segment)}"
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
                                    "page_number": {
                                        "type": "integer",
                                        "description": "The page number being summarized, please refer to the page number in the original text sent indicated by '🅿️ Start Page 20' '🅿️ Start Page 21' and so on. do not indicate the number of pages in this request, but instead use the original document."
                                    },
                                    "page_summary": {
                                        "type":"string",
                                        "description": "Always start the description with either '⤵️ CONTENT CONTINUED FROM PREVIOUS PAGE' or '🎉 START OF NEW SECTION' depending on the page content. Following that text, it should state TABLE OF CONTENTS or TITLE PAGE if one of those accuratly summarizes what's on the page. Following those remarks, there should be a 50 word detailed summary of the content on the page free of filler words."
                                    }
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

def create_compressed_document_gpt(document_id, pages_per_segment=5):
    engine = create_engine(os.environ['DATABASE_URL'])
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        document = session.query(Document).filter(Document.id == document_id).first()
        if not document or not document.full_contents:
            return "Error: Document not found or empty."

        pages = split_into_pages(document.full_contents)
        segments = create_segments(pages, pages_per_segment)
        with ThreadPoolExecutor(max_workers=5) as executor:
            # Calculate base page number using configurable segment size
            futures = [
                executor.submit(get_page_summaries, segment, segment_index * pages_per_segment)
                for segment_index, segment in enumerate(segments)
            ]
            compressed_content = []
            for future in futures:
                summaries = future.result()
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