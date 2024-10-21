from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from documents.documents_model import Document
from datetime import datetime
from flask import jsonify
from .add_documents_from_source import add_documents_from_source_websites
from .extract_missing_full_text import extract_missing_full_text

documents_bp = Blueprint('documents', __name__, template_folder='templates')

# Create database connection
engine = create_engine(os.environ['DATABASE_URL'])
Session = sessionmaker(bind=engine)

@documents_bp.route('/')
def index():
    session = Session()
    documents = session.query(Document).all()
    session.close()
    return render_template('documents.html', documents=documents)

@documents_bp.route('/add_document', methods=['POST'])
def add_document():
    session = Session()
    new_document = Document(
        title=request.form['title'],
        created_date=datetime.utcnow()
    )
    session.add(new_document)
    session.commit()
    session.close()
    return redirect(url_for('documents.index'))

@documents_bp.route('/edit_document/<int:id>', methods=['POST'])
def edit_document(id):
    session = Session()
    document = session.query(Document).get(id)
    
    if document:
        document.title = request.json['title']
        document.author = request.json['author']
        document.url = request.json['url']
        document.summary = request.json['summary']
        document.updated_date = datetime.utcnow()
        session.commit()
        session.close()
        return jsonify({"success": True, "message": "Document updated successfully"}), 200
    else:
        session.close()
        return jsonify({"success": False, "message": "Document not found"}), 404

@documents_bp.route('/delete_document/<int:id>', methods=['POST'])
def delete_document(id):
    session = Session()
    document = session.query(Document).get(id)
    session.delete(document)
    session.commit()
    session.close()
    return redirect(url_for('documents.index'))

@documents_bp.route('/add_docs_from_sources', methods=['POST'])
def add_docs_from_sources():
    result = add_documents_from_source_websites()
    return jsonify({"message": result})

@documents_bp.route('/extract_missing_full_text', methods=['POST'])
def extract_missing_full_text_route():
    result = extract_missing_full_text()
    return jsonify({"message": result})

@documents_bp.route('/view/<int:id>')
def view_document(id):
    session = Session()
    try:
        document = session.query(Document).filter(Document.id == id).first()
        if document is None:
            return "Document not found", 404
        return render_template('view_document.html', document=document)
    finally:
        session.close()