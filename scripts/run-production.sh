#!/bin/bash
# Run the WhatsApp Bot server in PRODUCTION mode (no reload)

export ENVIRONMENT=prod
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

