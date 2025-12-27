@echo off
REM Run the WhatsApp Bot server in TEST mode (Windows CMD batch file)

set ENVIRONMENT=test
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

