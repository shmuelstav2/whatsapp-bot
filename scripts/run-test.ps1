# Run the WhatsApp Bot server in TEST mode (PowerShell script for Windows)

$env:ENVIRONMENT = "test"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

