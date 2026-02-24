# 🏙️ Smart City Management System

Welcome to the **Smart City Management System**!  
This project is a comprehensive desktop application built with **Python** and **Tkinter**. It demonstrates advanced software engineering practices including Clean Architecture, Object-Oriented Programming (OOP), Design Patterns, and fundamental Cybersecurity mechanisms.

This project showcases how to build a modular, secure, scalable, and production-style desktop application using pure Python.

---
# Mockup

<img width="1916" height="986" alt="16Yöneticipaneliçalışıyor" src="https://github.com/user-attachments/assets/fd216d45-c4fb-454c-9d8d-192195a2515f" />

<img width="1914" height="987" alt="14loglarıepostayolla" src="https://github.com/user-attachments/assets/300d46e2-0286-4abb-9ef2-3071bd0b97c2" />

<img width="1909" height="979" alt="13işlemonayı" src="https://github.com/user-attachments/assets/5deb83b9-8b38-492e-8521-7dd3e68850b9" />

<img width="1904" height="986" alt="12parködemeyönetmi" src="https://github.com/user-attachments/assets/f56a05e9-f2a5-4e63-81c8-9efa7446314f" />

<img width="1908" height="982" alt="11parködemesi" src="https://github.com/user-attachments/assets/2f657037-af7e-4819-bd88-88b5831b55bd" />

<img width="1919" height="987" alt="10işlemonayı" src="https://github.com/user-attachments/assets/ad7f3cc2-1551-4e77-a909-158b79f81dae" />

<img width="1919" height="985" alt="9elektriksuödemeleritetikle" src="https://github.com/user-attachments/assets/13b2e59f-33df-4255-bd55-742ffe32ced1" />

<img width="1912" height="988" alt="8işlemonayı" src="https://github.com/user-attachments/assets/bc458ce3-6a7f-4e33-9698-95d50c8b09fb" />

<img width="1917" height="988" alt="7cüzdanbilgilerial" src="https://github.com/user-attachments/assets/ae7ab4a8-f743-4e89-82ba-0b87b70743ea" />

<img width="1914" height="985" alt="6kriptoParayükle" src="https://github.com/user-attachments/assets/61dc82e0-7645-4625-ac35-d11c6e026bce" />

<img width="1914" height="980" alt="5işlemonayı" src="https://github.com/user-attachments/assets/fc4874c6-7cb4-4d7d-b4ca-2988eb8188bb" />

<img width="1916" height="986" alt="4Kredikartıbilgileri" src="https://github.com/user-attachments/assets/0acb69e9-38d3-4cf7-9c2b-2fc9ed3ad582" />

<img width="1916" height="990" alt="3KredikartıParayükle" src="https://github.com/user-attachments/assets/9185e723-2865-4b32-b8e0-df276ba5f6aa" />

<img width="1911" height="988" alt="2Giriş Aşaması" src="https://github.com/user-attachments/assets/6169162a-1dd5-4a61-ac5a-369c840e85ab" />

<img width="1914" height="992" alt="1Kayıt aşaması" src="https://github.com/user-attachments/assets/317b0308-682a-4c80-9078-08b45e8017d3" />

# UML & USECASE
<img width="1201" height="943" alt="image" src="https://github.com/user-attachments/assets/50f2b5ec-97e4-4318-8a42-afb5184d3642" />

<img width="1204" height="940" alt="image" src="https://github.com/user-attachments/assets/a3b5587b-c4b1-40a0-833f-78bfccfc2e42" />

# 🚀 Key Features

## 🛡️ Cybersecurity & Data Protection

- **Password Hashing**  
  SHA-256 hashing with dynamic salt generation for secure credential storage.

- **Encrypted Logging System**  
  Logs are encrypted using a custom XOR-based algorithm combined with Base64 encoding before being written to disk.

- **Anti-Debugging Mechanisms**  
  Prevents execution under debugger environments to reduce reverse engineering risks.

- **Input Sanitization**  
  Built-in SQL injection prevention logic demonstrating secure coding principles.

- **DDoS Protection (Rate Limiting)**  
  Limits request frequency per user/IP to prevent abuse and brute-force attempts.

- **Honeypot Security Layer**  
  A decoy “Admin” account detects intrusion attempts.  
  If triggered:
  - IP/Phone is logged
  - Attempt is encrypted and stored
  - Cybercrime alert simulation is activated

---

## 🏠 Smart Home Integration

- Routine Automation (Morning & Evening)
- Remote Light Control
- Door Lock/Unlock System
- Secure action logging tied to user accounts

---

## 💳 DigiBank & Crypto Payments

- Credit Card Balance Top-Up
- Electricity / Water / Parking Bill Payments
- Simulated BTC transactions via Adapter Pattern
- External Crypto Wallet integration structure

---

## 📧 Real-Time Email Notifications

- SMTP-based email notification system
- Multithreaded email dispatch
- Non-blocking GUI performance

---

## 📊 Live System Monitor

Real-time monitoring using `psutil`:

- CPU Usage
- RAM Usage
- Active Threads
- Registered Users
- Application Uptime

---

# 🛠️ Tech Stack

**Language:** Python 3.x  
**GUI Framework:** Tkinter  
**System Monitoring:** psutil  
**Environment Management:** python-dotenv  

### Built-in Libraries

- hashlib
- secrets
- smtplib
- ssl
- threading
- abc
- base64
- re
- datetime

---

# 🧩 Project Architecture

The project follows strict Separation of Concerns principles and modular structure.

```
smart-city-management/
│
├── main.py
├── config.py
├── security.py
├── core_patterns.py
├── models.py
├── controller.py
├── services.py
├── gui.py
├── .env.example
└── README.md
```

### Module Responsibilities

- **main.py** → Application entry point  
- **config.py** → Global configuration & environment variables  
- **security.py** → Encryption, firewall, rate limiting, SMTP engine  
- **core_patterns.py** → Abstract Base Classes for design patterns  
- **models.py** → Core domain entities  
- **controller.py** → Singleton state manager & authentication  
- **services.py** → Banking logic & crypto adapter  
- **gui.py** → Tkinter interface & multithreading logic  

---

# 📐 Implemented Design Patterns

## 🔹 Singleton
CityController ensures only one central management instance exists.

## 🔹 Observer
Backend events notify:
- GUI
- Email Service
- Security System

## 🔹 Command
PayBillCommand encapsulates billing transactions as executable objects.

## 🔹 Adapter
CryptoAdapter integrates third-party crypto structure into BankingService.

---

# ⚙️ Installation & Setup

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/smart-city-management.git
cd smart-city-management
```

## 2️⃣ Create Virtual Environment (Recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

## 3️⃣ Install Dependencies

```bash
pip install psutil python-dotenv
```

## 4️⃣ Configure Environment Variables (Required for Email System)

Rename `.env.example` to `.env` and configure:

```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=465
SENDER_EMAIL=your_email_address@gmail.com
SENDER_PASSWORD=your_16_digit_app_password
```

⚠ Gmail users must:
- Enable 2-Step Verification
- Generate an App Password
- Use the 16-digit app password (not your main password)

## 5️⃣ Run the Application

```bash
python main.py
```

---

# 🎮 Default Testing Credentials

| Role      | Username / Phone | Password | Description |
|-----------|------------------|----------|-------------|
| Citizen   | 05551234567      | 1234     | Standard user dashboard |
| Admin     | admin            | 1234     | System administrator panel |
| Honeypot  | 999999           | 123456   | ⚠ Triggers cyber alert |

---

# 🔮 Future Improvements

- AI-based anomaly detection system
- JWT-based authentication
- Role-Based Authorization (RBAC)
- REST API version (FastAPI backend)
- PostgreSQL migration
- Docker containerization
- Cloud deployment (AWS / Azure integration)

---

# 🧠 What This Project Demonstrates

✔ Advanced OOP Architecture  
✔ Clean Code Principles  
✔ Real-world Cybersecurity Concepts  
✔ Thread-safe GUI Programming  
✔ Practical Design Pattern Implementation  
✔ Modular & Scalable Software Design  

Ideal for:
- Computer Engineering portfolios  
- Software Engineering showcases  
- Cybersecurity demonstrations  
- Internship & job applications  

---


# 👨‍💻 Developer

Serkan Demirtaş  
Computer Engineering Project  
