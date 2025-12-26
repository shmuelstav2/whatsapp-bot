#!/bin/bash
# Run the WhatsApp Bot server with external access enabled

uvicorn main:app --reload --host 0.0.0.0 --port 8000

