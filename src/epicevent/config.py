import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

if DATABASE_URL is None:
    raise RuntimeError("DATABASE_URL is not defined.")

if TEST_DATABASE_URL is None:
    raise RuntimeError("TEST_DATABASE_URL is not defined.")
