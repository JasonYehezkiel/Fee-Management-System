# Fee Management System

[![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat&logo=javascript&logoColor=black)]()


A simple web-based application for managing membership registration, attendance tracking, and payment processing, designed for souvenir center membership management.

Built using **Python (Flask)**, **SQLite**, **HTML**, and **JavaScript**.

---

## 📑 Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Endpoints](#endpoints)
- [Usage](#usage)
- [Extensions](#extensions)

---

## 🌟 Features

- **Member Registration**: Register new users based on selected transport type
- **Attendance Tracking**: Logs member attendance with a simulated cooldown
- **Automated Payments**: Generates a payment request every 5 visits
- **Reports View**: Displays attendance and payment history
- **Auto Database Initialization**: Database and tables are created on launch

---

## 📂 Project Structure

```
.
├── data
│   └── backups
│   └── memberships.db
├── logs
│   └── app.log
│   └── models.log
├── services
│   ├── app.py
│   ├── config.py
│   ├── display_table.py
│   ├── logger_setup.py
│   └── models.py
├── static
│   ├── css
│   │   └── style.css
│   └── js
│       └── main.js
├── templates
│   ├── index.html
│   ├── table_attendance.html
│   └── table_payment.html
├── app_runner.py
├── README.md
└── requirements.txt
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8 (or higher)
- Flask
- SQLite3
- [Neccessary Extensions](#extensions)
- Optional: Virtual Enviroment 

### Installation

1. **Open Command Prompt in the project directory:** \
**Note:** Make sure you are in the root directory, where `app_runner.py` is located.

2. **Prepare Virtual environment**
```bash
python -m venv env
env\Scripts\activate # or env\Scripts\activate.bat
```

3. **Install dependencies**
```bash
pip install -r requirements.txt 
```

if errors occur, install manually:

```bash
pip install flask tabulate
```

4. **Run the Application**
```bash
python app_runner.py # or python -m app_runner
```
### 🗄️ Sqlite Configuration

#### Setup
This project uses SQLite3 as the default database for storing member, attendance, and payment data. This database is automatically created and initialized when the application is first run. You don't need to manually configure SQLite.

#### Database Layout:
- The Database is located at `data/memberships.db`.
- The Tables used include `members`, `attendanceLog`, `paymentLog`.

#### Cara Mengelola Database
- Make sure you have sqlite3 on your computer (the version I use is 3.47.0)

- **backup and restore**: To backup data, I do it with PowerShell, because it is easier to add timestamps.

```bash
$timestamp = Get-Date -Format "yyyyMMddHHmmss"
sqlite3 data\memberships.db ".backup data\backups\backup_$timestamp.db"
```

```bash
sqlite3 data\memberships.db ".restore data\backups\backup_filename.db" 
``` 

### 📋 Displaying Database Tables

#### Overview
To allow any user to view the database contents, I created the `display_table.py` script, which displays data from the tables in the SQLite database.

However, you can also use the [SQLite Viewer](#extensions) extension by Florian Klampfer to view the database contents.

#### How It Works

##### **Run the Script**
```bash
python -m services.display_table
```

### 📝 Logging Configuration

#### Overview
This program uses a logging system to track activity and errors. Logs are saved to the following files:
- `app.log`: Logs activity for `app.py` (endpoint access).
- `models.log`: Logs activity for `models.py` (database).

#### Viewing Log Files

```
logs/
└── app.log
└── models.log
```

## 🔗 Endpoints

### Register Member
- **POST** `/api/register`
- **Parameter**:
- `name`: Member's name
- `transport`: Type of Transportation (Bus/Travel)
- **Response**: JSON object containing the newly generated `memberCode`.

### Record Attendance
- **POST** `/api/attendance`
- **Parameter**:
- `code`: Member code
- **Response**: JSON message indicating success and whether payment is due.

### Attendance List
- **GET** `/api/attendance-list`
- **Response**: JSON array containing attendance data (ID, member name, visit number)

### Daftar Pembayaran
- **GET** `/api/payment-list`
- **Response**: JSON array containing payment data (ID, member name, amount, status)

### Pembayaran biaya
- **POST** `/api/pay`
- **Parameter**:
- `code`: Member code for payment processing
- **Response**: JSON message confirming the payment status.

## 🧪 Usage

1. **Register a New Member**
    - Go to the "Register Member" section, enter the member’s name and type of transportation, then submit. A unique member code will be generated.

2. **Record Attendance**
    - Go to the "Record Attendance" section, enter the member code, and submit. Every 5th attendance will trigger a payment request.

3. **View Reports**
    - In the "View Reports" section, use the Attendance List and Payment List buttons to display attendance and payment records.
    - In the Payment List table, click Pay Now to complete a payment.

## 🔌 Extensions

The following Visual Studio Code extensions were used in this project:

- [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
- [Pylance](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance)
- [Python Debugger](https://marketplace.visualstudio.com/items?itemName=ms-python.debugpy)
- [SQLite Viewer](https://marketplace.visualstudio.com/items?itemName=qwtel.sqlite-viewer) by Florian Klampfer
- [vscode-pdf](https://marketplace.visualstudio.com/items?itemName=tomoki1207.pdf) by tomoki1207

## 👤 Author

Name: Jason Yehezkiel  
NIM: 191900531  
University: Calvin Institute of Technology

