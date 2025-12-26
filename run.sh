#!/bin/bash
# Run the WhatsApp Bot server in TEST mode with external access enabled

export ENVIRONMENT=test
uvicorn main:app --reload --host 0.0.0.0 --port 8000

