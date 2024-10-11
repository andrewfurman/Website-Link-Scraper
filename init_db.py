import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from source_websites.source_website_model import Base, SourceWebsite

# Use the DATABASE_URL from environment variables
DATABASE_URL = os.environ['DATABASE_URL']

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    Base.metadata.create_all(bind=engine)

def drop_tables():
    Base.metadata.drop_all(bind=engine)

if __name__ == "__main__":
    print("Creating tables...")
    create_tables()
    print("Tables created successfully.")

    # Optionally, you can add some test data
    # session = SessionLocal()
    # test_website = SourceWebsite(
    #     title="Test Website",
    #     url="https://www.testwebsite.com",
    #     author="Jane Doe",
    #     full_text="This is a test website entry.",
    #     found_urls="https://testlink1.com,https://testlink2.com"
    # )
    # session.add(test_website)
    # session.commit()
    # session.close()
    # print("Test data added.")

    print("Database setup complete.")