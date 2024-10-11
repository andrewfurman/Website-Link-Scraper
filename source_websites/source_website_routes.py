from flask import Blueprint, render_template
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