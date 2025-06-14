# RAG Application for TDS Course

This is a **RAG (Retrieve and Generate)** application designed to assist students in their **TDS (Tools in Data Science)** course. The application accepts **POST requests** and interacts with a custom AI proxy to provide valuable responses, all hosted locally at `127.0.0.1/api`.

### Features:

* **RAG System**: Retrieves relevant documents from a vector database based on a student's query and uses that information to generate answers.
* **Student-Friendly**: Aimed at aiding students with their course materials in real-time.
* **API**: Runs on `127.0.0.1/api` for POST requests.

## Prerequisites

Before running the application, ensure the following dependencies are installed:

* **Python 3.12 or higher**
* **pip**
* **Windows PowerShell** (If you're on Windows)
* **.env**
    1. **Cookies**
        * Log into the IIT Madras BS Program Discourse forum using your regular browser
        * Open Developer Tools:
        * Chrome/Edge: Press F12 or Right-click → Inspect
        * Firefox: Press F12 or Right-click → Inspect Element
        * Navigate to the “Application” tab (Chrome/Edge) or “Storage” tab (Firefox)
        * In the sidebar, expand “Cookies” and select discourse.onlinedegree.iitm.ac.in
        * Look for the following key cookies:
        * _t: The main authentication token
        * _forum_session: Session cookies
    2. **API_KEY**
        * Go to https://aipipe.org/login to get your api key


Make sure you have **`requirements.txt`** in the project folder, which contains all the necessary Python libraries for the app.

## Getting Started

### On Windows

If you're using Windows, there's a `run.ps1` script provided that will automate the setup and start the application. Follow the instructions below:

1. **Run the PowerShell Script**:

   * Open PowerShell in the project folder.
   * Run the following command to start the application:

     ```powershell
     .\run.ps1
     ```

This will automatically:

* Create a Python virtual environment
* Install the dependencies
* Run `scrape.py` and `main.py` scripts to start the application

### Manual Setup (For All Operating Systems)

If you're not using the provided PowerShell script, or you're on a non-Windows environment, follow these steps:

Here's the **manual setup** for non-Windows (Linux/macOS) environments using **Bash**. This will guide users to set up the environment, install dependencies, run the scraping script, and finally start the main application.

---

## Manual Setup (For Linux/macOS)

If you're not using the provided PowerShell script or you're on a non-Windows environment, follow these steps:

### Step 1: Create a Virtual Environment

1. Open a terminal and navigate to your project folder.
2. Run the following command to create a Python virtual environment named `.venv`:

   ```bash
   echo "Creating Python virtual environment as '.venv'"
   python3 -m venv .venv

   if [ $? -eq 0 ]; then
       echo "Virtual environment created successfully."
   else
       echo "Error: Failed to create virtual environment."
       exit 1
   fi
   ```

### Step 2: Activate the Virtual Environment

To activate the virtual environment:

1. Run the following command:

   ```bash
   echo "Activating virtual environment..."
   source .venv/bin/activate

   if [ $? -eq 0 ]; then
       echo "Virtual environment activated successfully."
   else
       echo "Error: Failed to activate virtual environment."
       exit 1
   fi
   ```

### Step 3: Install Required Packages

Now that the virtual environment is active, install the dependencies from `requirements.txt`:

1. Run the following command to install the required packages:

   ```bash
   echo "Installing required packages from requirements.txt..."
   pip install -r requirements.txt

   if [ $? -eq 0 ]; then
       echo "Packages installed successfully."
   else
       echo "Error: Failed to install packages."
       exit 1
   fi
   ```

### Step 4: Run the Scraping Script (`scrape.py`)

1. Navigate to the `app` folder where the scraping script (`scrape.py`) is located:

   ```bash
   echo "Navigating to the RAG application"
   cd app
   ```

2. Run the `scrape.py` script to initialize the data:

   ```bash
   echo "Running scrape.py..."
   python scrape.py

   if [ $? -eq 0 ]; then
       echo "scrape.py completed successfully."
   else
       echo "Error: scrape.py failed."
       exit 1
   fi
   ```

### Step 5: Run the Main Application (`main.py`)

After `scrape.py` completes successfully, run the main application (`main.py`):

1. Run the following command:

   ```bash
   echo "Running main.py..."
   python main.py
   ```

This will start the FastAPI server locally, and the application will be available at `http://127.0.0.1:8000/api`.

---
