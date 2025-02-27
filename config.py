import os
from dotenv import load_dotenv

load_dotenv()

DEBUG = os.getenv("DEBUG", "True") == "True"
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 5000))
