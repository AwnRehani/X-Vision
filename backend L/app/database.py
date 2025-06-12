from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# This tells SQLAlchemy to create a SQLite database file called xvision.db
DATABASE_URL = "sqlite:///./xvision.db"

# Create a database engine
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create a session to interact with the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our database models (tables)
Base = declarative_base()