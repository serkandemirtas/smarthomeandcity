import os
import time
from config import MAX_INPUT_LENGTH
from security import SecurityManager, check_debugger_active, check_security, prevent_sql_injection
from models import CityRoutine, UserRecord, Resident, MailObserver

class CityController:
    _instance = None

    def __init__(self):
        """
        This is the city's management center.
        """
        self.observers = []
        self.current_command = None
        self.logs = []
        self.city_routine = CityRoutine()
        self.user_db_ref = {} 
        self.security_mgr = SecurityManager()

    @classmethod
    def get_instance(cls):
        """
        Ensuring there is a single manager with the Singleton pattern.
        """
        if cls._instance is None:
            if check_debugger_active():
                print("ERROR: Debugger detected.")
                return None
            cls._instance = CityController()
        return cls._instance

    def set_user_db(self, db): self.user_db_ref = db
    
    def _get_user_internal(self, user_id): 
        """
        Only for calling a user from within the system.
        """
        return self.user_db_ref.get(user_id)

    def get_all_users(self):
        """
        I use this function to list all users.
        """
        users_list = []
        for phone, record in self.user_db_ref.items():
            # Show all details including Honeypot accounts
            res = record.resident
            honeypot_status = " [HONEYPOT/FAKE]" if record.is_honeypot else ""
            
            info = (f"ID: {record.tc_no} | {res.name} {res.surname} | "
                    f"Phone: {phone} | Email: {res.email} | "
                    f"Address: {res.address} | Balance: {record.balance:.2f} TL{honeypot_status}")
            users_list.append(info)
        return users_list

    def search_users(self, query):
        """
        I wrote this here to search for users.
        """
        is_safe, msg = check_security(query)
        if not is_safe: return [f"ERROR: {msg}"]
        clean_query = prevent_sql_injection(query)
        results = []
        for phone, record in self.user_db_ref.items():
            if record.is_honeypot: continue 
            res = record.resident
            full_text = f"{res.name} {res.surname} {phone}".lower()
            if clean_query.lower() in full_text:
                results.append(f"{res.name} {res.surname} | Phone: {phone}")
        return results

    def add_observer(self, observer):
        """
        Adding those who want to receive announcements to the list.
        """
        if len(self.observers) > 5000: return
        self.observers.append(observer)

    def notify_observers(self, message):
        """
        Using this to send a mass message to everyone.
        """
        self.log(f"Broadcast: {message}")
        for obs in self.observers:
            try: obs.update(message)
            except: pass
    
    def broadcast_emergency(self, alert_type, description):
        """
        Warning everyone when there is an emergency.
        """
        if len(description) > MAX_INPUT_LENGTH: description = description[:MAX_INPUT_LENGTH]
        full_msg = f"EMERGENCY ({alert_type}): {description}"
        self.notify_observers(full_msg)
        return full_msg

    def set_command(self, command): self.current_command = command
    
    def execute_command(self):
        if self.current_command: return self.current_command.execute()
        return False, "No command"

    def log(self, message):
        """
        Recording what happens.
        """
        if len(self.logs) > 5000: self.logs = self.logs[-4000:]
        self.logs.append(message)

    def export_logs_to_txt(self):
        """
        Saving logs to a file and encrypting them.
        """
        secure_filename = ".secure_city_logs.dat" 
        try:
            with open(secure_filename, "w", encoding="utf-8") as f:
                for line in self.logs:
                    encrypted_line = self.security_mgr.encrypt_log(line)
                    f.write(encrypted_line + "\n")
            if os.name == 'nt':
                try:
                    import ctypes
                    ctypes.windll.kernel32.SetFileAttributesW(secure_filename, 2)
                except: pass
            return f"Logs encrypted: {secure_filename}"
        except Exception as e: return f"Error: {e}"

    def monitor_txt_folder(self): return "Folder is being monitored."


class Login:
    def __init__(self):
        """
        Initializing the class that manages login and registration operations.
        """
        self.authorized_users = {} 
        self.admin_creds = {"user": "admin", "pass": "1234"} 
        self.security_mgr = SecurityManager()
        
        CityController.get_instance().set_user_db(self.authorized_users)

        # HONEYPOT
        fake_resident = Resident("Admin", "Backup", "admin_backup@city.com", "Server Room", "999999")
        hashed_fake_pass = self.security_mgr.hash_password("123456")
        self.authorized_users["999999"] = UserRecord("00000000000", hashed_fake_pass, fake_resident, is_honeypot=True)

    def register(self, tc_no, name, surname, email, address, phone, password):
        """
        Doing new member registration here.
        """
        is_safe_tc, _ = check_security(tc_no)
        is_not_spam, _ = check_security("register", user_id=phone)

        if not (is_safe_tc and is_not_spam): return False

        clean_name = prevent_sql_injection(name)
        clean_surname = prevent_sql_injection(surname)

        for record in self.authorized_users.values():
            if record.tc_no == tc_no: return False 

        hashed_password = self.security_mgr.hash_password(password)

        resident = Resident(clean_name, clean_surname, email, address, phone)
        self.authorized_users[phone] = UserRecord(tc_no, hashed_password, resident)
        
        CityController.get_instance().add_observer(resident)
        if email and "@" in email: 
            mail_obs = MailObserver(email)
            CityController.get_instance().add_observer(mail_obs)
        
        return True

    def login(self, phone, password):
        """
        Checking user login.
        """
        start_time = time.time()
        is_safe, msg = check_security(phone, user_id=phone)
        if not is_safe: return None

        result = None
        clean_phone = prevent_sql_injection(phone)
        
        if clean_phone in self.authorized_users:
            record = self.authorized_users[clean_phone]
            
            # SECURITY: Honeypot Check
            if record.is_honeypot:
                print(f"!!! HONEYPOT TRIGGERED !!! IP: {clean_phone}")
                return None 

            if self.security_mgr.verify_password(record.password, password):
                result = CityController.get_instance()
            else:
                print("Incorrect password.")
        
        if (time.time() - start_time) > 2.0:
            print("Timing analysis detected.")

        return result
    
    def login_admin(self, username, password):
        """
        Check for admin login.
        """
        is_safe, _ = check_security("admin", user_id="ip")
        if not is_safe: return False
        clean_user = prevent_sql_injection(username)
        return clean_user == self.admin_creds["user"] and password == self.admin_creds["pass"]