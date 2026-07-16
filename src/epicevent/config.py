import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Environment config
######################
DATABASE_URL = os.getenv("DATABASE_URL")
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")

if DATABASE_URL is None:
    raise RuntimeError("DATABASE_URL is not defined.")

if TEST_DATABASE_URL is None:
    raise RuntimeError("TEST_DATABASE_URL is not defined.")

if SECRET_KEY is None:
    raise RuntimeError("SECRET_KEY is not configured")


# App config
######################
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 10
ALGORITHM = "HS256"

# Cli config
######################
PROJECT_ROOT = Path(__file__).resolve().parents[2]
APP_DIR = PROJECT_ROOT / ".epicevent"
# APP_DIR = Path.home() / ".epicevent" PROD
TOKEN_PATH = APP_DIR / "tokens.json"
