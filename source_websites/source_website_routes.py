from flask import Blueprint, render_template, request, redirect, url_for
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os
from source_websites.source_website_model import SourceWebsite
import pytz
from source_websites.scrape_website import scrape_website

source_website_bp = Blueprint('source_website', __name__, 
                              template_folder='templates')

# Create engine and session
engine = create_engine(os.environ['DATABASE_URL'])
Session = sessionmaker(bind=engine)

@source_website_bp.route('/')
def index():
    session = Session()
    websites = session.query(SourceWebsite).all()
    
    # Convert UTC times to Eastern Time
    eastern = pytz.timezone('US/Eastern')
    for website in websites:
        if website.created_date:
            website.created_date = website.created_date.replace(tzinfo=pytz.UTC).astimezone(eastern)
        if website.updated_date:
            website.updated_date = website.updated_date.replace(tzinfo=pytz.UTC).astimezone(eastern)
    
    session.close()
    return render_template('source_websites.html', websites=websites)

# ... (rest of the code remains the same)

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

@source_website_bp.route('/scrape/<int:id>', methods=['POST'])
def scrape_website_route(id):
    scrape_website(id)
    return redirect(url_for('source_website.index'))