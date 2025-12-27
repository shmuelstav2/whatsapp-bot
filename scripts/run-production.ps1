# Run the WhatsApp Bot server in PRODUCTION mode (PowerShell script for Windows)

$env:ENVIRONMENT = "prod"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

