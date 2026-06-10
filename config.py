import os

# Read config from environment variables (recommended) with sane defaults for local dev

MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DB = os.getenv("MYSQL_DB", "koleksi_novel")

SECRET_KEY = os.getenv("SECRET_KEY", "dev-change-me")

# Upload folders (inside project)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
COVERS_DIR = os.path.join(STATIC_DIR, "covers")
PDFS_DIR = os.path.join(STATIC_DIR, "pdfs")

# Web paths to store in DB
COVER_WEB_PREFIX = "/static/covers"
PDF_WEB_PREFIX = "/static/pdfs"

