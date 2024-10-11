from flask import Blueprint, render_template, request, redirect, url_for
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os
from source_websites.source_website_model import SourceWebsite

source_website_bp = Blueprint('source_website', __name__, 
                              template_folder='templates')

# Create engine and session
engine = create_engine(os.environ['DATABASE_URL'])
Session = sessionmaker(bind=engine)

@source_website_bp.route('/')
def index():
    session = Session()
    websites = session.query(SourceWebsite).all()
    session.close()
    return render_template('source_websites.html', websites=websites)

# Add this new route to handle form submission
@source_website_bp.route('/add_url', methods=['POST'])
def add_url():
    url = request.form['url']
    session = Session()
    new_website = SourceWebsite(url=url)
    session.add(new_website)
    session.commit()
    session.close()
    return redirect(url_for('source_website.index'))

@source_website_bp.route('/delete/<int:id>', methods=['POST'])
def delete_website(id):
    session = Session()
    website = session.query(SourceWebsite).get(id)
    if website:
        session.delete(website)
        session.commit()
    session.close()
    return redirect(url_for('source_website.index'))