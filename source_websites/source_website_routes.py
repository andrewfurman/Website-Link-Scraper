from flask import Blueprint, render_template

source_website_bp = Blueprint('source_website', __name__, 
                              template_folder='templates')

@source_website_bp.route('/')
def index():
    return render_template('source_websites.html')