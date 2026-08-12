# EUREKA! Pitching & Startup Registration Platform

A premium, interactive web application and registration platform designed for entrepreneurship club pitching competitions. Built with a decoupled **Modular Monolith Architecture** supporting multiple frontends and future events.

## Features

- **Vibrant Landing Page**: An actual event experience landing page with a glassmorphic dark theme, interactive cards, and a dynamic schedule timeline.
- **Dynamic Stepper Form**: Multi-step registration form (Team Lead info -> Startup pitch details -> Dynamic team sizing -> PDF pitch deck uploads).
- **Conditional Layout Rendering**: Automatically shows/hides business fields based on whether the startup is existing, and handles optional PDF attachments.
- **Robust Field Validation**: Frontend immediate checking (email syntax, 10-digit phone number, PDF sizes up to 10MB) paired with backend Pydantic validation.
- **Excel Spreadsheet Exporter**: Club organizers can download matching student records into a stylized Excel workbook using `openpyxl`.
- **Admin Dashboard**: Complete panel to review registration summaries, toggle statuses (Pending/Approved/Rejected), download pitch deck PDFs, and search or filter records.

---

## Tech Stack

- **Frontend**: Vanilla HTML5, CSS3 (custom CSS variables, glassmorphic blur layers, responsive grids), and Vanilla JS (stepper routes, dynamic nodes).
- **Backend**: FastAPI (Asynchronous REST API, static files mounting), SQLAlchemy ORM, and Pydantic (data parsing).
- **Database**: SQLite (easy development database file).
- **Spreadsheets**: openpyxl.

---

## 🛠️ Terminal & Activation Manual

This guide explains how to set up your environment and activate the **Backend** and **Frontend** services using the terminal.

### 📋 Prerequisites & Setup
First, open your terminal (PowerShell, Command Prompt, or terminal) and navigate to the project directory:
```bash
cd "d:\Entreprenuership club\Eureka"
```

#### 1. Create & Activate Virtual Environment (Recommended)
Creating a virtual environment ensures Python packages are isolated.
* **Windows (PowerShell)**:
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
* **Windows (CMD)**:
  ```cmd
  python -m venv venv
  .\venv\Scripts\activate.bat
  ```
* **macOS / Linux**:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

#### 2. Install Project Dependencies
Make sure your virtual environment is active (you should see `(venv)` in your terminal prompt) and run:
```bash
pip install -r requirements.txt
```

---

### 🚀 Option A: Integrated Activation (Recommended)
In this mode, the **FastAPI backend serves both the API endpoints and the frontend static assets** (HTML, CSS, JS). This is the easiest and most seamless setup.

#### 1. Run the FastAPI Server
Start the server using `uvicorn`:
```bash
uvicorn backend.main:app --reload
```
* The `--reload` flag tells the server to watch for code modifications and auto-reload.

#### 2. Access the Application
Open your browser and navigate to:
* **Landing Page / Frontend**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
* **Registration Form**: [http://127.0.0.1:8000/register](http://127.0.0.1:8000/register)
* **Admin Dashboard**: [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)

If you are using the separate static frontend server on port 3000, use the HTML files directly instead:
* **Landing Page / Frontend**: [http://127.0.0.1:3000/index.html](http://127.0.0.1:3000/index.html)
* **Registration Form**: [http://127.0.0.1:3000/register.html](http://127.0.0.1:3000/register.html)
* **Admin Dashboard**: [http://127.0.0.1:3000/admin.html](http://127.0.0.1:3000/admin.html)

---

### 🔀 Option B: Separate Terminal Activation (Decoupled Frontend & Backend)
If you are modifying frontend UI templates or want to serve the files using separate processes in independent terminal windows:

#### 📦 Terminal 1: Backend API Server
1. Navigate to the project root directory and activate the virtual environment.
2. Start the FastAPI server:
   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```
3. The interactive API documentation will be available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

#### 🎨 Terminal 2: Frontend Web Server
1. Open a **second terminal** and navigate to the project directory.
2. Run a local web server pointing directly to the `frontend` directory:
   * **Using Python**:
     ```bash
     python -m http.server 3000 --directory frontend
     ```
   * **Using Node.js**:
     ```bash
     npx serve -l 3000 frontend
     ```
3. Open your browser to [http://127.0.0.1:3000/](http://127.0.0.1:3000/) to access the frontend application.

> [!NOTE]
> When hosting frontend pages separately (e.g., on port 3000) and backend APIs on port 8000, relative fetch requests to `/api/eureka/...` in the JavaScript files will attempt to request port 3000 instead of port 8000. For local testing with separate terminals, Option A is the recommended method.
>
> The frontend pages also work on the static server through `index.html`, `register.html`, and `admin.html`, but the API calls still require the FastAPI backend to be running in a separate terminal.

---

### 🔑 Default Admin Credentials
Use these details to access the dashboard on [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin):
- **Username**: `admin`
- **Password**: `EurekaAdmin2026`

---

## 🔍 Troubleshooting & Common Issues

If you run into any issues while activating the application, please review these troubleshooting steps:

### 1. "Page Not Found" / `404 Not Found` (JSON / FastAPI output)
If the browser opens but shows `{"detail":"Not Found"}` or a blank page with a `404` status, check which server you are actually using.
* **Cause 1**: FastAPI is running, but you opened a path that only exists on the static frontend server, or vice versa.
* **Cause 2**: You ran the backend from the wrong folder or it is not running at all.
* **Fix**: If you want the FastAPI-served routes, make sure your terminal path is at the project root (`d:\Entreprenuership club\Eureka`) and run the server using `python -m uvicorn`:
  ```bash
  # Go back to the root folder (if you are inside backend/)
  cd ..
  
  # Start the server using the python module path
  python -m uvicorn backend.main:app --reload
  ```
* **Fix for static frontend mode**: If you are using `python -m http.server 3000 --directory frontend`, open the page by file name, for example [http://127.0.0.1:3000/admin.html](http://127.0.0.1:3000/admin.html), not [http://127.0.0.1:3000/admin](http://127.0.0.1:3000/admin).

### 2. "This site can’t be reached" / Connection Refused
If the browser fails to load anything at `http://127.0.0.1:8000/`:
* **Cause 1**: The server process did not start or crashed. Look at your terminal and make sure you see logs showing:
  ```text
  INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
  ```
* **Cause 2**: The port `8000` is already in use by another application.
* **Fix**: Start the server on a different port:
  ```bash
  python -m uvicorn backend.main:app --reload --port 8080
  ```
  Then access the site at [http://127.0.0.1:8080/](http://127.0.0.1:8080/).

### 3. `ModuleNotFoundError: No module named 'backend'`
If you get this error message in your terminal:
* **Cause**: Python cannot locate the `backend` package because you are in a different directory or your Python path is not configured.
* **Fix**: Make sure you are in the project root directory (`Eureka`) and run:
  ```bash
  python -m uvicorn backend.main:app --reload
  ```
  Using `python -m uvicorn` instead of just `uvicorn` automatically adds the current working directory to Python's search path.

### 4. Windows PowerShell: "Script Execution is Disabled"
If you get an error when running `.\venv\Scripts\Activate.ps1`:
> *Activate.ps1 cannot be loaded because running scripts is disabled on this system.*
* **Fix**: You need to grant script execution permission to your current PowerShell window session. Run this command, then try activating the virtual environment again:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
  ```
  *Alternatively*, you can bypass activating the environment in the terminal and run the server directly using the environment's Python interpreter:
  ```powershell
  .\venv\Scripts\python.exe -m uvicorn backend.main:app --reload
  ```

---

## Folder Structure

```
d:/Entreprenuership club/Eureka/
├── backend/
│   ├── app/
│   │   ├── core/                  # Reusable global configurations
│   │   │   ├── config.py          # Port bindings and keys
│   │   │   ├── database.py        # SQLAlchemy session settings
│   │   │   └── security.py        # Hashing and JWT token verification
│   │   │
│   │   └── eureka/                # Independent Eureka event module
│   │       ├── models.py          # Event database tables (Registration, Team)
│   │       ├── schemas.py         # Pydantic schemas (validations)
│   │       ├── crud.py            # SQLite operations
│   │       ├── routes.py          # API endpoints (register, status, export)
│   │       └── services/
│   │           └── excel.py       # Excel generation script
│   │
│   ├── main.py                    # Entry point mapping static files
│   └── tests/
│       └── test_api.py            # API testing scripts
│
├── frontend/
│   ├── index.html                 # Landing page
│   ├── register.html              # Multi-step form
│   ├── admin.html                 # Dashboard panel
│   ├── css/
│   │   └── style.css              # Glassmorphic dark styling
│   └── js/
│       ├── registration.js        # Form validation and dynamic fields
│       └── admin.js               # Status edits, token login, and excel blobs
│
├── uploads/                       # Pitch deck PDFs and graphics
│
├── requirements.txt               # Dependencies
└── README.md                      # Documentation
```

---

## Development & Testing

Run backend tests using pytest:

```bash
pytest backend/tests/test_api.py
```
