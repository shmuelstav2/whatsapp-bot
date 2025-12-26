# WhatsApp Bot

A FastAPI application for receiving and sending WhatsApp messages via n8n webhooks.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## Endpoints

### POST `/whatsapp`
Receives incoming WhatsApp messages and logs them.

### POST `/what6`
Sends a WhatsApp message via the n8n webhook.

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`



