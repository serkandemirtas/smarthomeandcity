import tkinter as tk
import os
from tkinter import ttk, messagebox, simpledialog
import datetime
import threading
import psutil  # Performans verilerini çekmek için

from core_patterns import Observer
from controller import CityController, Login
from services import FiatPayment, CryptoAdapter, PayBillCommand
from models import PublicSecurityAuthority, PublicUtilityService

class GUIObserver(Observer):
    """
    Observer Pattern implementation:
    Listens to events generated in the backend and reflects them instantly
    on the Listbox component on the GUI.
    """
    def __init__(self, listbox):
        self.listbox = listbox

    def update(self, message):
        # This runs when the notify from the backend is triggered.
        # Adding a timestamp to the message and printing it to the interface.
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.listbox.insert(0, f"[{timestamp}] {message}")

class SmartCityApp(tk.Tk):
    """
    Main Application Class (Main Entry Point).
    Manages all frames and transitions between pages.
    """
    def __init__(self):
        super().__init__()
        self.title("Smart City")
        self.geometry("1400x900") 
        self.configure(bg="#f0f2f5")

        # Returns the ID of the currently running code.
        # Creates an object that monitors data only for this ID.
        self.my_process = psutil.Process(os.getpid())

        # Creating instances of backend services here.
        self.login_system = Login()
        self.controller = CityController.get_instance()
        self.fiat_bank = FiatPayment()
        self.crypto_bank = CryptoAdapter() # Adapter Pattern usage
        
        # Adding authority services to the system as observers.
        self.controller.add_observer(PublicSecurityAuthority())
        self.controller.add_observer(PublicUtilityService())
        
        # Variables to hold active user session data
        self.current_user_record = None
        self.current_phone = None

        # Main container frame where pages will change
        self.container = tk.Frame(self, bg="#f0f2f5")
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.create_status_bar()

        self.frames = {}

        # Pre-creating all pages and loading them into memory for fast transitions.
        for F in (LoginPage, RegisterPage, DashboardPage, AdminDashboardPage, ProfilePage):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(LoginPage)

        self.update_app_monitor() # Start performance monitoring
    
    def create_status_bar(self):
        """App-specific performance bar."""
        self.statusbar = tk.Frame(self, bg="#2c3e50", height=35)
        self.statusbar.pack(side="bottom", fill="x")
        
        style = ttk.Style()
        style.theme_use('clam')
        # Let's choose an orange/yellow tone for app resources so the difference is clear
        style.configure("orange.Horizontal.TProgressbar", foreground='#f39c12', background='#f39c12')

        def add_metric(label_text, length=100):
            f = tk.Frame(self.statusbar, bg="#2c3e50")
            f.pack(side="left", padx=10)
            tk.Label(f, text=label_text, bg="#2c3e50", fg="white", font=("Bold", 8)).pack(side="left")
            p = ttk.Progressbar(f, orient="horizontal", length=length, mode="determinate", style="orange.Horizontal.TProgressbar")
            p.pack(side="left", padx=5)
            l = tk.Label(f, text="...", bg="#2c3e50", fg="#bdc3c7", font=("Consolas", 8))
            l.pack(side="left")
            return p, l

        # 1. APP CPU: App's processor usage
        self.prog_cpu, self.lbl_cpu_val = add_metric("CPU:")
        
        # 2. APP RAM: App's memory usage
        self.prog_ram, self.lbl_ram_val = add_metric("RAM:")
        
        # 3. THREADS: Number of threads running simultaneously
        # This will increase when the send mail button is pressed.
        self.lbl_threads = tk.Label(self.statusbar, text="Threads: 1", bg="#2c3e50", fg="#e74c3c", font=("Bold", 9))
        self.lbl_threads.pack(side="left", padx=20)

        # 4. USER COUNT
        self.lbl_users = tk.Label(self.statusbar, text="👥 Users: 0", bg="#2c3e50", fg="#f1c40f", font=("Bold", 9))
        self.lbl_users.pack(side="left", padx=20)

        # 5. UPTIME 
        self.lbl_uptime = tk.Label(self.statusbar, text="⏱ 00:00", bg="#2c3e50", fg="#3498db", font=("Bold", 9))
        self.lbl_uptime.pack(side="right", padx=10)

    def update_app_monitor(self):
        """Measures the resource consumption of this app only."""
        try:
            # APP CPU USAGE
            # If we don't say interval=None, the interface freezes.
            app_cpu = self.my_process.cpu_percent(interval=None)
            self.prog_cpu['value'] = app_cpu * 2 
            self.lbl_cpu_val.config(text=f"%{app_cpu:.1f}")

            # APP RAM USAGE (in MB)
            mem_info = self.my_process.memory_info()

            # Physical space occupied in RAM (Byte)
            ram_mb = mem_info.rss / 1024 / 1024 
            
            # For bar fullness: Let's assume this app should consume max 200MB.
            self.prog_ram['value'] = (ram_mb / 200) * 100 
            self.lbl_ram_val.config(text=f"{ram_mb:.1f} MB")
            
            # THREAD COUNT
            # Main loop + Mail sending etc.
            thread_count = self.my_process.num_threads()
            self.lbl_threads.config(text=f"Threads: {thread_count}")

            # APP LOGIC 
            total_users = len(self.login_system.authorized_users)
            self.lbl_users.config(text=f"👥 Members: {total_users}")

            # UPTIME
            create_time = datetime.datetime.fromtimestamp(self.my_process.create_time())
            uptime = datetime.datetime.now() - create_time
            # Let's drop the microseconds of the second
            uptime_str = str(uptime).split('.')[0] 
            self.lbl_uptime.config(text=f"⏱ {uptime_str}")
            
        except Exception as e:
            print(f"App Monitor Error: {e}")

        # Repeat after 1 second
        self.after(1000, self.update_app_monitor)

    def show_frame(self, cont):
        # Brings the desired page to the front (tkraise).
        frame = self.frames[cont]
        frame.tkraise()
        
        # Triggering init functions to keep data up-to-date during page transitions.
        if cont == DashboardPage and self.current_user_record:
            frame.initialize_dashboard()
        if cont == ProfilePage and self.current_user_record:
            frame.initialize_profile()
        if cont == AdminDashboardPage:
            frame.initialize_admin()

class LoginPage(tk.Frame):
    """
    User and Admin login screen.
    """
    def __init__(self, parent, app):
        super().__init__(parent, bg="#2c3e50")
        self.app = app
        
        card = tk.Frame(self, bg="white", padx=40, pady=40, relief="raised")
        card.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(card, text="SMART CITY LOGIN", font=("Segoe UI", 18, "bold"), bg="white").pack(pady=20)
        
        tk.Label(card, text="Login Type:", bg="white", font=("Bold", 10)).pack(anchor="w")
        self.type_combo = ttk.Combobox(card, values=["Citizen", "Admin"], state="readonly")
        self.type_combo.current(0)
        self.type_combo.pack(fill="x", pady=5)
        self.type_combo.bind("<<ComboboxSelected>>", self.update_label)

        self.lbl_user_input = tk.Label(card, text="Phone Number:", bg="white")
        self.lbl_user_input.pack(anchor="w")
        
        self.ent_user = tk.Entry(card, width=30)
        self.ent_user.pack(pady=5)
        self.ent_user.insert(0, "05551234567") # Default value for testing convenience

        tk.Label(card, text="Password:", bg="white").pack(anchor="w")
        self.ent_pass = tk.Entry(card, width=30, show="*")
        self.ent_pass.pack(pady=5)
        self.ent_pass.insert(0, "1234")

        tk.Button(card, text="LOGIN", bg="#27ae60", fg="white", font=("Bold", 10), 
                  command=self.do_login).pack(pady=20, fill="x")
        tk.Button(card, text="Register", bg="#2980b9", fg="white", 
                  command=lambda: app.show_frame(RegisterPage)).pack(fill="x")

    def update_label(self, event=None):
        # Dynamically updates the label based on Combobox selection (UX improvement).
        if self.type_combo.get() == "Admin":
            self.lbl_user_input.config(text="Username:")
        else:
            self.lbl_user_input.config(text="Phone Number:")

    def do_login(self):
        # Authentication process via backend.
        u_type = self.type_combo.get()
        user_in = self.ent_user.get()
        pass_in = self.ent_pass.get()

        if u_type == "Admin":
            if self.app.login_system.login_admin(user_in, pass_in):
                self.app.show_frame(AdminDashboardPage)
            else:
                messagebox.showerror("Error", "Incorrect admin credentials (admin/1234)")
        else:
            # Automatically creating a user for the demo presentation if one doesn't exist.
            self.app.login_system.register("12345678901", "Serkan", "Demirtaş", "mail@mail.com", "Istanbul", "05551234567", "1234")
            
            controller = self.app.login_system.login(user_in, pass_in)
            if controller:
                # Updating global user state on successful login.
                self.app.current_phone = user_in
                self.app.current_user_record = self.app.login_system.authorized_users[user_in]
                self.app.show_frame(DashboardPage)
            else:
                messagebox.showerror("Error", "User not found.")

class RegisterPage(tk.Frame):
    """
    New user registration screen.
    """
    def __init__(self, parent, app):
        super().__init__(parent, bg="#2c3e50")
        self.app = app
        card = tk.Frame(self, bg="white", padx=30, pady=30)
        card.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(card, text="Register", font=("Bold", 14), bg="white").pack(pady=10)
        self.entries = {}
        # Creating Entries with a loop and storing them in a dictionary.
        for f in ["ID Number", "Name", "Surname", "Email", "Address", "Phone", "Password"]:
            tk.Label(card, text=f, bg="white").pack(anchor="w")
            e = tk.Entry(card); e.pack(pady=2); self.entries[f] = e
            
        tk.Button(card, text="SAVE", bg="#27ae60", fg="white", command=self.register).pack(pady=10)
        tk.Button(card, text="Back", command=lambda: app.show_frame(LoginPage)).pack()

    def register(self):
        # Collecting form data and sending it to the backend.
        d = {k: v.get() for k, v in self.entries.items()}
        res = self.app.login_system.register(d["ID Number"], d["Name"], d["Surname"], d["Email"], d["Address"], d["Phone"], d["Password"])
        if res:
            messagebox.showinfo("Success", "Registration complete.")
            self.app.show_frame(LoginPage)
        else:
            messagebox.showerror("Error", "Registration failed. You are already registered.")

class ProfilePage(tk.Frame):
    """
    User profile information view and edit screen.
    """
    def __init__(self, parent, app):
        super().__init__(parent, bg="#ecf0f1")
        self.app = app
        
        header = tk.Frame(self, bg="#34495e", height=60)
        header.pack(fill="x")
        tk.Button(header, text="< Go Back", bg="#7f8c8d", fg="white", font=("Bold", 10),
                  command=lambda: app.show_frame(DashboardPage)).pack(side="left", padx=20, pady=15)
        tk.Label(header, text="MY PROFILE", bg="#34495e", fg="white", font=("Bold", 14)).pack(side="left", padx=20)
        tk.Button(header, text="Edit", bg="#f39c12", fg="white", font=("Bold", 10),
                  command=self.open_edit_modal).pack(side="right", padx=20, pady=15)

        content = tk.Frame(self, bg="#ecf0f1")
        content.pack(fill="both", expand=True, padx=50, pady=30)

        card = tk.Frame(content, bg="white", bd=1, relief="solid", padx=40, pady=40)
        card.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(card, text="Personal Information", font=("Segoe UI", 16, "bold"), bg="white", fg="#2c3e50").pack(pady=(0, 20))

        self.info_labels = {}
        fields = [("Full Name", "name_surname"), ("ID Number", "tc"), ("Phone", "phone"), ("Email", "email"), ("Address", "address")]

        for label_text, key in fields:
            row = tk.Frame(card, bg="white")
            row.pack(fill="x", pady=8)
            tk.Label(row, text=f"{label_text}:", font=("Bold", 11), bg="white", width=15, anchor="w", fg="#7f8c8d").pack(side="left")
            val_lbl = tk.Label(row, text="...", font=("Arial", 11), bg="white", anchor="w")
            val_lbl.pack(side="left")
            self.info_labels[key] = val_lbl

    def initialize_profile(self):
        # Fetches updated data from backend when the page opens.
        user_record = self.app.current_user_record
        resident = user_record.resident
        self.info_labels["name_surname"].config(text=f"{resident.name} {resident.surname}")
        self.info_labels["tc"].config(text=user_record.tc_no)
        self.info_labels["phone"].config(text=resident.phone)
        self.info_labels["email"].config(text=resident.email)
        self.info_labels["address"].config(text=resident.address)

    def open_edit_modal(self):
        # Opens a Toplevel (Modal) window for editing.
        resident = self.app.current_user_record.resident
        edit_win = tk.Toplevel(self)
        edit_win.title("Edit Profile"); edit_win.geometry("400x450"); edit_win.grab_set()

        entries = {}
        fields = [("Name", "name", resident.name), ("Surname", "surname", resident.surname), 
                  ("Email", "email", resident.email), ("Address", "address", resident.address), ("Phone", "phone", resident.phone)]

        for label_text, key, val in fields:
            tk.Label(edit_win, text=label_text, font=("Bold", 10)).pack(anchor="w", padx=20, pady=(10, 0))
            e = tk.Entry(edit_win, width=40); e.pack(padx=20, pady=5); e.insert(0, val)
            entries[key] = e

        def save():
            # Profile update logic. If the phone changes, the DB is also updated since the ID changes.
            resident.name = entries["name"].get()
            resident.surname = entries["surname"].get()
            resident.email = entries["email"].get()
            resident.address = entries["address"].get()
            new_phone = entries["phone"].get()
            
            if new_phone != resident.phone:
                old_phone = resident.phone
                users_db = self.app.login_system.authorized_users
                if old_phone in users_db:
                    record = users_db.pop(old_phone)
                    record.resident.phone = new_phone
                    users_db[new_phone] = record
                    self.app.current_phone = new_phone
            
            resident.phone = new_phone
            messagebox.showinfo("Success", "Profile updated.")
            self.initialize_profile()
            edit_win.destroy()

        tk.Button(edit_win, text="SAVE", bg="#27ae60", fg="white", font=("Bold", 10), command=save).pack(pady=20)

class DashboardPage(tk.Frame):
    """
    Citizen Main Dashboard.
    Contains Smart Home, Bank, and Log monitoring operations.
    """
    def __init__(self, parent, app):
        super().__init__(parent, bg="#ecf0f1")
        self.app = app
        
        # Left Sidebar Menu
        sidebar = tk.Frame(self, bg="#34495e", width=220)
        sidebar.pack(side="left", fill="y")
        tk.Label(sidebar, text="DASHBOARD", bg="#34495e", fg="white", font=("Bold", 14)).pack(pady=30)
        self.lbl_user = tk.Label(sidebar, text="", bg="#34495e", fg="#bdc3c7")
        self.lbl_user.pack()
        tk.Button(sidebar, text="My Profile", bg="#2980b9", fg="white", font=("Bold", 10), command=lambda: app.show_frame(ProfilePage)).pack(fill="x", padx=10, pady=5)
        tk.Button(sidebar, text="Logout", bg="#c0392b", fg="white", command=lambda: app.show_frame(LoginPage)).pack(side="bottom", fill="x", padx=10, pady=20)

        # Main Content Area
        content = tk.Frame(self, bg="#ecf0f1")
        content.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        content.columnconfigure(0, weight=3); content.columnconfigure(1, weight=2); content.rowconfigure(0, weight=1)
        
        left_area = tk.Frame(content, bg="#ecf0f1"); left_area.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        right_area = tk.Frame(content, bg="white", bd=1, relief="solid"); right_area.grid(row=0, column=1, sticky="nsew")

        # Smart Home Section
        hf = tk.LabelFrame(left_area, text="🏠 Smart Home Management", bg="white", font=("Bold", 11))
        hf.pack(fill="x", pady=(0, 10))
        btn_f = tk.Frame(hf, bg="white"); btn_f.pack(fill="x", pady=10, padx=10)
        self.mk_btn(btn_f, "☀️ Morning", "#f1c40f", lambda: self.home.morning_routines())
        self.mk_btn(btn_f, "🌙 Evening", "#8e44ad", lambda: self.home.evening_routines())
        self.mk_btn(btn_f, "💡 Turn On Lights", "#e67e22", lambda: self.home.turn_on_lights())
        self.mk_btn(btn_f, "🌑 Turn Off Lights", "#7f8c8d", lambda: self.home.turn_off_lights())
        self.mk_btn(btn_f, "🔒 Lock", "#c0392b", lambda: self.home.lock_door())
        
        # Button for sending mail with Threading
        tk.Button(btn_f, text="📧 Email Report", bg="#3498db", fg="white", font=("Bold", 9), relief="flat", height=2,
                  command=self.send_mail_report_threaded).pack(side="left", padx=2)

        # DigiBank Section
        bf = tk.LabelFrame(left_area, text="💳 DigiBank", bg="white", font=("Bold", 11))
        bf.pack(fill="both", expand=True)
        top_b = tk.Frame(bf, bg="white"); top_b.pack(fill="x", padx=10, pady=10)
        self.lbl_bal = tk.Label(top_b, text="Balance: 0.0 TL", font=("Arial", 20, "bold"), fg="#27ae60", bg="white")
        self.lbl_bal.pack(side="left")
        
        self.pay_var = tk.StringVar(value="FIAT")
        
        act_b = tk.Frame(bf, bg="white"); act_b.pack(fill="x", padx=10, pady=10)
        self.mk_btn(act_b, "➕ Add Money", "#2ecc71", self.popup_load)
        self.mk_btn(act_b, "⚡ Pay Electricity", "#34495e", lambda: self.popup_pay("Electricity", 200))
        self.mk_btn(act_b, "💧 Pay Water", "#3498db", lambda: self.popup_pay("Water", 100))
        self.mk_btn(act_b, "🅿️ Pay Parking", "#95a5a6", self.popup_park)

        # Log Monitoring (Observer Output)
        tk.Label(right_area, text="System Logs", font=("Bold", 12), bg="white").pack(pady=10)
        log_container = tk.Frame(right_area, bg="white")
        log_container.pack(fill="both", expand=True, padx=5, pady=5)
        sb_v = tk.Scrollbar(log_container, orient="vertical"); sb_h = tk.Scrollbar(log_container, orient="horizontal")
        self.log_list = tk.Listbox(log_container, bd=0, bg="#f9f9f9", font=("Consolas", 10), yscrollcommand=sb_v.set, xscrollcommand=sb_h.set)
        sb_v.config(command=self.log_list.yview); sb_h.config(command=self.log_list.xview)
        sb_v.pack(side="right", fill="y"); sb_h.pack(side="bottom", fill="x"); self.log_list.pack(side="left", fill="both", expand=True)

    def mk_btn(self, parent, text, color, cmd):
        # Button creator helper function (to prevent code repetition)
        tk.Button(parent, text=text, bg=color, fg="white", font=("Bold", 9), relief="flat", padx=5, pady=5, command=cmd).pack(side="left", padx=2)

    def initialize_dashboard(self):
        # Establishes observer connections when the user logs in.
        user = self.app.current_user_record.resident
        self.lbl_user.config(text=f"{user.name} {user.surname}")
        self.home = user.home_system
        # Catching backend logs with callback function.
        self.home.log_callback = self.log_to_gui
        self.app.controller.observers = [GUIObserver(self.log_list)]
        self.update_ui()

    def log_to_gui(self, msg):
        self.app.controller.notify_observers(f"HOME: {msg}")

    def update_ui(self):
        # Updates dynamic data in the UI like balance.
        uid = self.app.current_phone
        bal = self.app.fiat_bank.get_balance(uid)
        self.lbl_bal.config(text=f"Balance: {bal:.2f} TL")
    
    def send_mail_report_threaded(self):
        """
        Multithreading Implementation:
        Since the mailing process can cause network latency, to prevent the GUI from freezing
        we run this process on a separate thread.
        """
        def task():
            resident = self.app.current_user_record.resident
            success, msg = resident.send_logs_via_mail()
            if success:
                messagebox.showinfo("Success", msg)
            else:
                messagebox.showwarning("Warning", msg)
        
        threading.Thread(target=task).start()

    def get_payment_details(self, method):
        # Helper modal that takes details based on payment type selection.
        dialog = tk.Toplevel(self); dialog.title("Details"); dialog.geometry("300x350"); dialog.grab_set() 
        details = {}
        if method == "FIAT":
            tk.Label(dialog, text="Credit Card No:", font=("Bold", 10)).pack(pady=10); e_card = tk.Entry(dialog, width=25); e_card.pack(pady=5); e_card.insert(0, "1234567812345678")
            tk.Label(dialog, text="CVV:", font=("Bold", 10)).pack(pady=5); e_cvv = tk.Entry(dialog, width=5); e_cvv.pack(pady=5)
            def submit():
                if len(e_card.get()) < 16: messagebox.showerror("Error", "Invalid Card"); return
                details["card_no"] = e_card.get(); details["cvv"] = e_cvv.get(); dialog.destroy()
        elif method == "CRYPTO":
            tk.Label(dialog, text="Crypto Wallet ID:", font=("Bold", 10)).pack(pady=5); e_wallet = tk.Entry(dialog, width=30); e_wallet.pack(pady=5)
            tk.Label(dialog, text="Name:", font=("Bold", 10)).pack(pady=5); e_name = tk.Entry(dialog, width=30); e_name.pack(pady=5)
            tk.Label(dialog, text="Surname:", font=("Bold", 10)).pack(pady=5); e_surname = tk.Entry(dialog, width=30); e_surname.pack(pady=5)
            def submit():
                if not e_wallet.get(): messagebox.showerror("Error", "Missing information!"); return
                details["wallet_id"] = e_wallet.get(); details["owner_name"] = e_name.get(); details["owner_surname"] = e_surname.get(); dialog.destroy()
        tk.Button(dialog, text="Confirm", bg="#27ae60", fg="white", command=submit).pack(pady=20)
        self.wait_window(dialog)
        return details if details else None

    def popup_load(self):
        # Money loading interface
        choice_win = tk.Toplevel(self); choice_win.title("Add Money"); choice_win.geometry("350x250")
        tk.Label(choice_win, text="Amount (TL):").pack(pady=5); ent_amt = tk.Entry(choice_win); ent_amt.pack(pady=5)
        tk.Label(choice_win, text="Source:", font=("Bold", 10)).pack(pady=10); load_source = tk.StringVar(value="CARD")
        tk.Radiobutton(choice_win, text="Credit Card", variable=load_source, value="CARD").pack(anchor="w", padx=40)
        tk.Radiobutton(choice_win, text="Crypto Wallet", variable=load_source, value="CRYPTO").pack(anchor="w", padx=40)
        def on_confirm():
            try: amt = float(ent_amt.get())
            except: return
            source = load_source.get(); choice_win.destroy()
            method = "FIAT" if source == "CARD" else "CRYPTO"
            details = self.get_payment_details(method)
            if details:
                service = self.app.fiat_bank if source == "CARD" else self.app.crypto_bank
                res, msg = service.load_money(self.app.current_phone, amt, details)
                self.app.controller.notify_observers(f"BANK: {msg}"); self.update_ui(); messagebox.showinfo("Info", msg)
        tk.Button(choice_win, text="Continue", command=on_confirm).pack(pady=15)

    def popup_pay(self, type_, amount):
        # Bill payment interface (Command Pattern trigger)
        choice_win = tk.Toplevel(self); choice_win.title("Payment Method"); choice_win.geometry("350x250")
        tk.Label(choice_win, text=f"{type_} ({amount} TL)", font=("Bold", 12)).pack(pady=10)
        pay_source = tk.StringVar(value="BALANCE")
        tk.Radiobutton(choice_win, text="Deduct from DigiBank Balance", variable=pay_source, value="BALANCE").pack(anchor="w", padx=20)
        tk.Radiobutton(choice_win, text="Pay with Credit Card", variable=pay_source, value="CARD").pack(anchor="w", padx=20)
        tk.Radiobutton(choice_win, text="Pay with Crypto Wallet", variable=pay_source, value="CRYPTO").pack(anchor="w", padx=20)
        def on_confirm():
            source = pay_source.get(); choice_win.destroy()
            details = {}
            service = self.app.fiat_bank
            if source == "CARD":
                details = self.get_payment_details("FIAT"); 
                if not details: return
            elif source == "CRYPTO":
                details = self.get_payment_details("CRYPTO"); 
                if not details: return
                service = self.app.crypto_bank
            # Command Pattern: We convert the request into an object and send it.
            cmd = PayBillCommand(service, amount, type_, self.app.current_phone, details)
            self.app.controller.set_command(cmd)
            success, msg = self.app.controller.execute_command()
            self.app.controller.notify_observers(f"PAYMENT ({source}): {msg}")
            self.update_ui(); messagebox.showinfo("Info", msg)
        tk.Button(choice_win, text="Continue", command=on_confirm, bg="#3498db", fg="white").pack(pady=20)

    def popup_park(self):
        loc = simpledialog.askstring("Parking", "Location / License Plate:")
        if loc: self.popup_pay(f"Parking ({loc})", 50)

class AdminDashboardPage(tk.Frame):
    """
    Admin Panel.
    Provides full system monitoring, emergency broadcasting, and log management.
    """
    def __init__(self, parent, app):
        super().__init__(parent, bg="#34495e")
        self.app = app
        sidebar = tk.Frame(self, bg="#2c3e50", width=200); sidebar.pack(side="left", fill="y")
        tk.Label(sidebar, text="ADMIN", bg="#2c3e50", fg="white", font=("Bold", 14)).pack(pady=30)

        tk.Button(sidebar, text="Logout", bg="red", fg="white", command=lambda: app.show_frame(LoginPage)).pack(side="bottom", fill="x", padx=10, pady=20)
        content = tk.Frame(self, bg="#34495e"); content.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        controls = tk.Frame(content, bg="#34495e"); controls.pack(fill="x", pady=5)

        rf = tk.LabelFrame(controls, text="City Routines", bg="#ecf0f1"); rf.pack(side="left", padx=5)
        tk.Button(rf, text="Daily", command=lambda: self.log_adm(self.app.controller.city_routine.routines_daily())).pack(side="left", padx=5)
        tk.Button(rf, text="Sensor", command=lambda: self.log_adm(self.app.controller.city_routine.check_sensors())).pack(side="left", padx=5)
        tk.Button(rf, text="Export", bg="orange", command=self.export).pack(side="right", padx=5)

        uf = tk.LabelFrame(controls, text="Users", bg="#ecf0f1"); uf.pack(side="left", padx=5)
        self.ent_search = tk.Entry(uf); self.ent_search.pack(side="left", padx=5)
        tk.Button(uf, text="Search", command=self.search_user).pack(side="left")
        tk.Button(uf, text="List", command=self.list_users).pack(side="right", padx=5)

        ef = tk.LabelFrame(controls, text="Emergency", bg="#ffcccc"); ef.pack(side="left", padx=5)
        tk.Button(ef, text="FIRE", bg="red", fg="white", command=lambda: self.broadcast("FIRE", "Fire!")).pack(side="left", padx=5)
        tk.Button(ef, text="ANNOUNCEMENT", bg="#27ae60", fg="white", command=self.custom_broadcast).pack(side="right", padx=5)

        # Bottom Panel: Split View (Lists)
        split_view = tk.Frame(content, bg="#34495e"); split_view.pack(fill="both", expand=True)
        split_view.columnconfigure(0, weight=1); split_view.columnconfigure(1, weight=1)

        # User List & Results (Left)
        ulf = tk.LabelFrame(split_view, text="User List & Results", bg="#ecf0f1")
        ulf.grid(row=0, column=0, sticky="nsew", padx=5)
        sb_u = tk.Scrollbar(ulf, orient="horizontal"); sb_u.pack(side="bottom", fill="x")
        self.ulst = tk.Listbox(ulf, font=("Consolas", 9), xscrollcommand=sb_u.set); self.ulst.pack(fill="both", expand=True)
        sb_u.config(command=self.ulst.xview)

        lf = tk.LabelFrame(split_view, text="System Logs", bg="#ecf0f1")
        lf.grid(row=0, column=1, sticky="nsew", padx=5)

        # Vertical Scrollbar (Y Axis)
        sb_l_y = tk.Scrollbar(lf, orient="vertical")
        sb_l_y.pack(side="right", fill="y")

        # Horizontal Scrollbar (X Axis) - NEWLY ADDED PART
        sb_l_x = tk.Scrollbar(lf, orient="horizontal")
        sb_l_x.pack(side="bottom", fill="x")

        # Listbox (Connected both scrollbars)
        self.llst = tk.Listbox(
            lf, 
            bg="white", 
            fg="black", 
            font=("Consolas", 10), 
            yscrollcommand=sb_l_y.set,  # Vertical connection
            xscrollcommand=sb_l_x.set   # Horizontal connection
        )
        self.llst.pack(fill="both", expand=True)

        # Connecting scrollbar commands to listbox's view functions
        sb_l_y.config(command=self.llst.yview)
        sb_l_x.config(command=self.llst.xview) # Horizontal movement command

    def initialize_admin(self):
        # Connects admin logs to the system and loads past logs.
        self.app.controller.add_observer(GUIObserver(self.llst))
        self.llst.delete(0, tk.END); [self.llst.insert(tk.END, l) for l in self.app.controller.logs]
        self.ulst.delete(0, tk.END)


    def log_adm(self, m): self.app.controller.notify_observers(f"ADMIN: {m}")
    def export(self): res = self.app.controller.export_logs_to_txt(); messagebox.showinfo("Export", res)
    
    def list_users(self):  # Lists users.
        users = self.app.controller.get_all_users()
        self.ulst.delete(0, tk.END); self.ulst.insert(0, "--- REGISTERED USERS ---"); [self.ulst.insert(tk.END, u) for u in users]
    
    def search_user(self): # Used for searching users.
        q = self.ent_search.get(); 
        if not q: return
        res = self.app.controller.search_users(q)
        self.ulst.delete(0, tk.END); self.ulst.insert(0, f"--- SEARCH: {q} ---"); [self.ulst.insert(tk.END, r) for r in res]
    
    def broadcast(self, t, m): 
        # Observer Pattern: Broadcasts emergency notification to all system components.
        self.app.controller.broadcast_emergency(t, m); messagebox.showwarning("Alarm", m)
    
    def custom_broadcast(self): m = simpledialog.askstring("Announcement", "Message"); self.app.controller.broadcast_emergency("GENERAL", m) if m else None