from flask import Blueprint, render_template

documents_bp = Blueprint('documents', __name__, template_folder='templates')

@documents_bp.route('/')
def index():
    return render_template('documents.html')