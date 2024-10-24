# summarize_document_gpt.py

# This function will call the OpenAI API to summarize a document using the gpt-4o-mini model.

# This function will first update the word_count and page_count fields in the document table for the given document_id by calculating the number of words and pages in the document full_contents field.

# This function will then call the OpenAI API to update these fields for the document ID: summary, extended_summary, chapter, title, and author.

import os
import sys
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from openai import OpenAI
import json

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from documents.documents_model import Document

client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

def update_document_counts(session, document):
    if document.full_contents:
        document.word_count = len(document.full_contents.split())
        page_markers = re.findall(r'🅿️ Start Page \d+', document.full_contents)
        document.page_count = len(page_markers)
        if document.page_count == 0:
            document.page_count = (document.word_count + 499) // 500
    session.commit()

def summarize_document_gpt(document_id):
    engine = create_engine(os.environ['DATABASE_URL'])
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        document = session.query(Document).filter(Document.id == document_id).first()
        if not document:
            return f"Error: Document with ID {document_id} not found."
        update_document_counts(session, document)
        
        # Prepare document content with truncation if needed
        content = document.full_contents
        word_count = document.word_count
        truncation_notice = ""
        
        if word_count > 80000:
            words = content.split()
            content = " ".join(words[:80000])
            truncation_notice = f"Note: This is the first 80,000 words of a {word_count} word document. Please provide the best possible summary based on this limited information."
        
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an AI assistant tasked with analyzing and summarizing documents. Please provide a concise summary, an extended summary, identify the main chapter topics, suggest a title if not present, and identify the author if possible." + 
                    (" " + truncation_notice if truncation_notice else "")
                },
                {
                    "role": "user",
                    "content": f"Please analyze the following document:\n\n{content}"
                }
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "DocumentSummary",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "summary": {
                                "type": "string",
                                "description": "A brief overview of the document's main content in 3 bullet points. each bullet point should begin with an emoji representing the bullet, a bolded title followed by a colon, and then a detailed one sentance description, including applicable examples, and free of filler words, format this summary as Markdown Text."
                            },
                            "extended_summary": {
                                "type": "string",
                                "description": "A more detailed summary of the document, covering major topics format this as approximately 20 bullet points grouped by multiple topic headings, each topic heading should begin with an emoji representing the topic, a bolded topic title, and then a detailed one sentance description, including applicable examples, and free of filler words, format this summary as Markdown Text."
                            },
                            "chapter": {
                                "type": "string",
                                "description": "The chapter that this document is about. Example: 'Chapter 15'"
                            },
                            "title": {
                                "type": "string",
                                "description": "A descriptive title of the document. This should not include just the title, but should also be descriptive of what the document contnts are. Example: Medicare Ambulance Claims Processing Guide: Chapter 15 - Comprehensive Payment, Billing, and Documentation Guidelines (Rev. 12414, Issued 12-19-23)"
                            },
                            "author": {
                                "type": "string",
                                "description": "The author(s) of the document. Example: 'Centers for Medicare & Medicaid Services (CMS)'"
                            }
                        },
                        "required": ["summary", "extended_summary", "chapter", "title", "author"],
                        "additionalProperties": False
                    }
                }
            }
        }
        
        response = client.chat.completions.create(**payload)
        generated_fields = json.loads(response.choices[0].message.content)
        document.summary = generated_fields['summary']
        document.extended_summary = generated_fields['extended_summary']
        document.chapter = generated_fields['chapter']
        document.title = generated_fields['title']
        document.author = generated_fields['author']
        session.commit()
        return f"Success: Document ID {document_id} has been summarized and updated."
    except Exception as e:
        session.rollback()
        return f"Error: {str(e)}"
    finally:
        session.close()