import os
from dotenv import load_dotenv
# Mail server settings
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

# --- SECURITY SETTINGS ---
MAX_INPUT_LENGTH = 3000 # Preventing very long data inputs
RATE_LIMIT_WINDOW = 60 # Waiting time in seconds
MAX_REQUESTS_PER_WINDOW = 5 # Maximum requests per person
request_history = {} # Keeping request history here