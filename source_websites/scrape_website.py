# this scrape website python file has a single function that uses the BeautifulSoup python library in order to scrape the content from a website that is already in the database. Dysfunctional receive the ID of a website in the source websites database table, and then it will update the title column. The author column the updated date column based on when this is called, and then it will save the full text found on that website in the full tax column, it will not update the found URLs column.

from bs4 import BeautifulSoup
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from source_websites.source_website_model import SourceWebsite
from datetime import datetime
import urllib.parse

def extract_urls(soup, base_url, patterns):
  urls = set()
  for a_tag in soup.find_all('a', href=True):
      url = a_tag['href']
      # Handle relative URLs
      full_url = urllib.parse.urljoin(base_url, url)
      if any(pattern in full_url for pattern in patterns):
          urls.add(full_url)
  return list(urls)

def scrape_website(website_id):
    engine = create_engine(os.environ['DATABASE_URL'])
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        website = session.query(SourceWebsite).filter_by(id=website_id).first()
        if not website:
            print(f"Website with id {website_id} not found.")
            return

        response = requests.get(website.url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        website.title = soup.title.string if soup.title else "No title found"

        author_tag = soup.find('meta', attrs={'name': 'author'})
        website.author = author_tag['content'] if author_tag else "Unknown"

        website.full_text = soup.get_text(separator=' ', strip=True)

        # Define multiple patterns to search for
        patterns = [
            "/dobi/division_insurance/solvency/annualstatements/",
            "/reports/",
            "/publications/",
            ".pdf"

        ]

        # Extract and store found URLs
        found_urls = extract_urls(soup, website.url, patterns)
        website.found_urls = ', '.join(found_urls)

        website.updated_date = datetime.utcnow()

        session.commit()
        print(f"Successfully updated website with id {website_id}")

    except Exception as e:
        print(f"An error occurred while scraping website with id {website_id}: {str(e)}")
        session.rollback()

    finally:
        session.close()