## NOTE: This script is intended to be run in a PowerShell environment.
## NOTE: This script only works for first-time setup of the RAG application.

# Create Python virtual environment as '.venv'
Write-Host "Creating Python virtual environment as '.venv'"
python -m venv .venv
if ($?) {
    Write-Host "Virtual environment created successfully."
} else {
    Write-Host "Error: Failed to create virtual environment."
    exit 1
}

# Activate the virtual environment
Write-Host "Activating virtual environment..."
& .venv\Scripts\Activate.ps1
if ($?) {
    Write-Host "Virtual environment activated successfully."
} else {
    Write-Host "Error: Failed to activate virtual environment."
    exit 1
}

# Install required packages from requirements.txt
Write-Host "Installing required packages from requirements.txt..."
pip install -r requirements.txt
if ($?) {
    Write-Host "Packages installed successfully."
} else {
    Write-Host "Error: Failed to install packages."
    exit 1
}

# Navigate to the RAG application directory
Write-Host "Directing to the RAG application"
cd app

# Run the scrape.py script
Write-Host "Running scrape.py..."
python scrape.py
if ($?) {
    Write-Host "scrape.py completed successfully."
} else {
    Write-Host "Error: scrape.py failed."
    exit 1
}

# Run the main.py script
Write-Host "Running main.py..."
python main.py
