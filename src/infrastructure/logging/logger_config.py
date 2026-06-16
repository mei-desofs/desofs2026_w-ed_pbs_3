import logging
from logging.handlers import RotatingFileHandler
import os
import time

# ================= LOG DIRECTORY =================
if not os.path.exists("logs"):
    os.makedirs("logs", mode=0o750)

# ================= LOG SANITIZATION =================
def sanitize_log(value):
    if value is None:
        return "null"
    return str(value).replace("\n", " ").replace("\r", " ").replace("|", " ")

# ================= FILE HANDLER =================
file_handler = RotatingFileHandler(
    "logs/app.log",
    maxBytes=10_000_000,
    backupCount=5
)

# ================= LOG FORMAT =================
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ"
)

file_handler.setFormatter(formatter)

# ================= LOGGER CONFIG =================
logger = logging.getLogger("app_logger")
logger.setLevel(logging.INFO)

logger.addHandler(file_handler)
logger.addHandler(logging.StreamHandler())

logger.propagate = False