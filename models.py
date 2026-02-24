import datetime
from core_patterns import Observer
from config import MAX_INPUT_LENGTH
from security import prevent_sql_injection, send_real_email

class MailObserver(Observer):
    def __init__(self, email):
        self.email = email

    def update(self, message):
        """
        I wrote this so it sends an email when an announcement arrives.
        """
        subject = "City System Notification"
        safe_message = message[:MAX_INPUT_LENGTH] + "..." if len(message) > MAX_INPUT_LENGTH else message
        body = f"Dear User,\n\nYou have a notification from the city management system:\n\n{safe_message}\n\nBest regards,\nSmart City Management"
        send_real_email(self.email, subject, body)

class SmartHomeSystem:
    def __init__(self, owner_phone, log_callback=None):
        """
        Starting the home system here, registering the owner.
        """
        self.owner_phone = owner_phone 
        self.log_callback = log_callback
        self.__history_logs = [] # Keeping logs secret

    def _log(self, msg):
        """
        Adding performed operations to the list.
        """
        if len(self.__history_logs) > 1000:
            self.__history_logs.pop(0) 

        timestamp = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
        full_msg = f"[{timestamp}] {msg}"
        self.__history_logs.append(full_msg)
        
        if self.log_callback:
            self.log_callback(msg)
        else:
            print(f"[SmartHome - {self.owner_phone}] {msg}")

    def get_logs_secure(self, requester_phone):
        """
        Checking so only the owner can see the logs.
        """
        if requester_phone == self.owner_phone:
            return self.__history_logs
        else:
            print(f"!!! UNAUTHORIZED ACCESS: {requester_phone} tried to view {self.owner_phone}'s logs!")
            return ["Access Denied: Unauthorized Operation."]

    # Routines (These are example operations)
    def morning_routines(self): self._log("Morning routine started.")
    def evening_routines(self): self._log("Evening routine started.")
    def turn_on_lights(self): self._log("Lights turned on.")
    def turn_off_lights(self): self._log("Lights turned off.")
    def lock_door(self): self._log("Door locked.")


class Resident(Observer):
    def __init__(self, name, surname, email, address, phone):
        """
        Getting and saving the citizen's information here.
        """
        safe_name = prevent_sql_injection(name)
        safe_surname = prevent_sql_injection(surname)

        if len(safe_name) > MAX_INPUT_LENGTH or len(safe_surname) > MAX_INPUT_LENGTH:
             raise ValueError("Name or surname is invalid!")
             
        self.name = safe_name
        self.surname = safe_surname
        self.email = email
        self.address = address
        self.phone = phone
        # Notifying the home system of its owner
        self.home_system = SmartHomeSystem(owner_phone=phone)

    def manage_home(self):
        self.home_system.turn_on_lights()

    def send_logs_via_mail(self):
        """
        Person can request their own logs via email.
        """
        # Requesting logs with our own phone number
        logs = self.home_system.get_logs_secure(self.phone)
        
        if not logs or "Access Denied" in logs[0]:
            return False, "Access to logs denied."
        
        log_content = "\n".join(logs[-50:]) 
        mail_body = f"Dear {self.name},\n\nReport:\n\n{log_content}"
        return send_real_email(self.email, "Home Report", mail_body)

    def make_payment(self): print("Payment requested.")
    def get_payment_info(self, is_crypto): return "Crypto Wallet" if is_crypto else "IBAN"

    def update(self, message):
        """
        Printing the announcement from the city to the screen.
        """
        if self.home_system.log_callback:
            self.home_system.log_callback(f"⚠️ ANNOUNCEMENT: {message}")


class UserRecord:
    def __init__(self, tc_no, password_hash, resident, is_honeypot=False):
        """
        The user's record in the database.
        """
        self.tc_no = tc_no
        self.password = password_hash # Hashed Password
        self.resident = resident
        self.balance = 0.0
        self.history = []
        self.is_honeypot = is_honeypot # Is it a honeypot account?


class CityRoutine:
    def routines_daily(self): return "Daily routines applied."
    def check_sensors(self): return "Sensors active."
    def save_logs(self): return "Logs backed up."

class PublicSecurityAuthority(Observer):
    def update(self, message):
        """
        Notifying police and security units.
        """
        msg = message.upper()
        if "FIRE" in msg or "EARTHQUAKE" in msg: print(f" POLICE Emergency: {message}")
        elif "HONEYPOT" in msg: print(f"CYBERCRIME ALARM: System intrusion attempt! {message}")

class PublicUtilityService(Observer):
    def update(self, message):
        """
        If there is an electricity or water fault, I notify the teams.
        """
        if "ELECTRICITY" in message.upper(): print(f" ELECTRICITY Fault: {message}")