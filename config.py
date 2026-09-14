import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()


class Config:
    # PostgreSQL database connection
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

    # Disable unnecessary SQLAlchemy event notifications
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask secret key
    SECRET_KEY = os.getenv("SECRET_KEY")

    # Store owner's WhatsApp number
    STORE_WHATSAPP_NUMBER = os.getenv("STORE_WHATSAPP_NUMBER")

    # Maximum uploaded file size: 5 MB
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024