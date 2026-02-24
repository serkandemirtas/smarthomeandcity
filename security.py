import sys
import base64
import re
import hashlib
import secrets
import time
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from config import SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD, MAX_INPUT_LENGTH, RATE_LIMIT_WINDOW, MAX_REQUESTS_PER_WINDOW, request_history

class SecurityManager:
    """
    I do all encryption tasks here.
    """
    def __init__(self, key="SUPER_SECRET_CITY_KEY_2024"):
        self.key = key # My encryption key

    def encrypt_log(self, raw_data):
        """
        Scrambling logs so no one can read them.
        """
        encrypted = []
        for i, char in enumerate(raw_data):
            key_char = self.key[i % len(self.key)]
            encrypted_char = chr(ord(char) ^ ord(key_char))
            encrypted.append(encrypted_char)
        return base64.b64encode("".join(encrypted).encode()).decode()

    def hash_password(self, plain_password, salt=None):
        """
        Hiding passwords to not store them in plain text in the database.
        """
        if salt is None:
            salt = secrets.token_hex(16) # Generating random salt
        salted_input = salt + plain_password
        hash_obj = hashlib.sha256(salted_input.encode())
        hashed_password = hash_obj.hexdigest()
        return f"{salt}:{hashed_password}" # Returning combined salt and password

    def verify_password(self, stored_password, provided_password):
        """
        Checking if the password entered by the user is correct.
        """
        try:
            salt, stored_hash = stored_password.split(':')
            new_hash_entry = self.hash_password(provided_password, salt)
            _, new_hash = new_hash_entry.split(':')
            return new_hash == stored_hash
        except ValueError:
            return False

def check_debugger_active():
    """
    Checking if someone is trying to inspect my code.
    """
    gettrace = getattr(sys, 'gettrace', None)
    if gettrace is None: return False
    return gettrace() is not None

def prevent_sql_injection(input_val):
    """
    Cleaning malicious database commands. There is no SQL in the system, but I wanted to show what could happen in a potential SQL attack.
    """
    if not isinstance(input_val, str):
        return str(input_val)
    sql_patterns = [r";", r"--", r"/\*", r"\*/", r"xp_", r"UNION", r"SELECT", r"DROP", r"INSERT", r"DELETE", r"UPDATE"]
    cleaned_val = input_val
    for pattern in sql_patterns:
        if re.search(pattern, cleaned_val, re.IGNORECASE):
            print(f"!!!SQL Injection attempt detected: {pattern}")
            cleaned_val = re.sub(pattern, "", cleaned_val, flags=re.IGNORECASE)
    cleaned_val = cleaned_val.replace("'", "''") 
    return cleaned_val

def check_security(input_str, user_id="guest"):
    """
    Doing general security checks here.
    """
    if check_debugger_active():
        print(f"!!!Debugger detected! System is being monitored.")
        return False, "System cannot be run in debug mode."

    if input_str and len(str(input_str)) > MAX_INPUT_LENGTH:
        return False, "Data size is too large."
    
    if isinstance(input_str, str):
        safe_str = prevent_sql_injection(input_str)
        if safe_str != input_str.replace("'", "''"):
             return False, "Invalid characters detected."

    # DDoS Protection (Rate Limiting)
    current_time = time.time()
    if user_id not in request_history:
        request_history[user_id] = []
    
    request_history[user_id] = [t for t in request_history[user_id] if current_time - t < RATE_LIMIT_WINDOW]
    
    if len(request_history[user_id]) >= MAX_REQUESTS_PER_WINDOW:
        print(f"!!! Too many requests for user {user_id}.")
        return False, "You have sent too many requests. Please wait."
    
    request_history[user_id].append(current_time)
    return True, "Safe"

def send_real_email(to_email, subject, body):
    """
    I wrote this function to actually send emails.
    """
    is_safe, msg = check_security(body, user_id=to_email)
    if not is_safe: return False, msg

    try:
        message = MIMEMultipart()
        message["From"] = SENDER_EMAIL
        message["To"] = to_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(message)
        
        print(f"✅ Email successfully sent: {to_email}")
        return True, "Email successfully sent."
    except Exception as e:
        print(f"❌ Email sending error: {e}")
        return False, f"Mail Could Not Be Sent: {e}"