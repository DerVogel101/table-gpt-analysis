# Überprüft, ob Python 3.11 installiert ist und im PATH vorhanden ist
$pythonVersion = python --version 2>&1
if ($pythonVersion -notlike "*Python 3.11*") {
    # Installiert Python 3.11 mit Winget, falls nicht vorhanden
    winget install -e --id Python.Python.3.11
}

# Überprüft, ob das Virtual Environment bereits existiert
if (-not (Test-Path ".\venv")) {
    # Erstellt ein Virtual Environment im aktuellen Verzeichnis
    python -m venv .\venv
}

# Aktiviert das Virtual Environment
.\venv\Scripts\Activate.ps1

# Installiert Abhängigkeiten aus der requirements.txt
pip install -r .\requirements.txt

# Startet die main.py
python .\main.py
