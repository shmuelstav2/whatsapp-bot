@echo off
REM Run the WhatsApp Bot server in PRODUCTION mode (Windows CMD batch file)

set ENVIRONMENT=prod
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

