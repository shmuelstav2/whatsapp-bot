# WhatsApp Bot

A FastAPI application for receiving and sending WhatsApp messages via n8n webhooks.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
# For local access only:
uvicorn main:app --reload

# For external access (accessible from outside):
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- Local: `http://localhost:8000`
- External: `http://YOUR_IP:8000` (when using --host 0.0.0.0)

## Endpoints

### GET `/`
Health check endpoint - returns server status.

### GET `/health`
Health check endpoint.

### POST `/whatsapp`
Receives incoming WhatsApp messages and logs them.

### POST `/what6`
Sends a WhatsApp message via the n8n webhook.

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`



