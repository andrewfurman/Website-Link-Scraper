# this scrape website python file has a single function that uses the BeautifulSoup python library in order to scrape the content from a website that is already in the database. Dysfunctional receive the ID of a website in the source websites database table, and then it will update the title column. The author column the updated date column based on when this is called, and then it will save the full text found on that website in the full tax column, it will not update the found URLs column.

from bs4 import BeautifulSoup
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from source_websites.source_website_model import SourceWebsite
from datetime import datetime

def scrape_website(website_id):
    # Create engine and session
    engine = create_engine(os.environ['DATABASE_URL'])
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Fetch the website from the database
        website = session.query(SourceWebsite).filter_by(id=website_id).first()
        if not website:
            print(f"Website with id {website_id} not found.")
            return

        # Fetch the webpage content
        response = requests.get(website.url)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Update title
        website.title = soup.title.string if soup.title else "No title found"

        # Update author (this is a simplistic approach, might need adjustment based on site structure)
        author_tag = soup.find('meta', attrs={'name': 'author'})
        website.author = author_tag['content'] if author_tag else "Unknown"

        # Update full text
        website.full_text = soup.get_text(separator=' ', strip=True)

        # Update updated_date
        website.updated_date = datetime.utcnow()

        # Commit changes to the database
        session.commit()
        print(f"Successfully updated website with id {website_id}")

    except Exception as e:
        print(f"An error occurred while scraping website with id {website_id}: {str(e)}")
        session.rollback()

    finally:
        session.close()

# Example usage:
# scrape_website(1)  # Where 1 is the id of the website in the database