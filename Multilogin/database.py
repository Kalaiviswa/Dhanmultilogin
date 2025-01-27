from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base  # Replace with the actual import path of your Base

# Adjust the connection string to match your database configuration
DATABASE_URL = "sqlite:///./test.db"  # Replace with your actual database URL
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Create the tables
def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully.")

if __name__ == "__main__":
    init_db()
