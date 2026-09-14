import os

from dotenv import load_dotenv

load_dotenv()


class Config:

    # =========================================================
    # DATABASE
    # =========================================================

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False


    # =========================================================
    # FLASK SECURITY
    # =========================================================

    SECRET_KEY = os.getenv("SECRET_KEY")


    # =========================================================
    # WHATSAPP
    # =========================================================

    STORE_WHATSAPP_NUMBER = os.getenv(
        "STORE_WHATSAPP_NUMBER"
    )


    # =========================================================
    # FILE UPLOAD LIMIT
    # =========================================================

    MAX_CONTENT_LENGTH = 5 * 1024 * 1024


    # =========================================================
    # CLOUDINARY
    # =========================================================

    CLOUDINARY_CLOUD_NAME = os.getenv(
        "CLOUDINARY_CLOUD_NAME"
    )

    CLOUDINARY_API_KEY = os.getenv(
        "CLOUDINARY_API_KEY"
    )

    CLOUDINARY_API_SECRET = os.getenv(
        "CLOUDINARY_API_SECRET"
    )