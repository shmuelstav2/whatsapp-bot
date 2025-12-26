import os
import requests
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Get environment mode (default to 'test' if not set)
ENVIRONMENT = os.getenv("ENVIRONMENT", "test").lower()

# Set N8N webhook URL based on environment
if ENVIRONMENT == "prod":
    N8N_WEBHOOK_URL = "https://ninsights.app.n8n.cloud/webhook/whatsappout"
else:
    N8N_WEBHOOK_URL = "https://ninsights.app.n8n.cloud/webhook-test/whatsappout"

# Enable CORS to allow external requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok", "message": "WhatsApp Bot is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "environment": ENVIRONMENT}

@app.get("/info")
def get_info():
    return {
        "status": "ok",
        "environment": ENVIRONMENT,
        "n8n_webhook_url": N8N_WEBHOOK_URL
    }

@app.post("/whatsapp")
async def receive_whatsapp(request: Request):
    data = await request.json()
    print("Incoming WhatsApp message:")
    print(data)

    return {"status": "ok"}

@app.post("/what6")
def send_whatsapp():
    payload = {
        "to": "972542202468",
        "text": "הודעה ישירות דרך n8n"
    }

    r = requests.post(N8N_WEBHOOK_URL, json=payload)

    return {
        "status": "sent",
        "environment": ENVIRONMENT,
        "n8n_webhook_url": N8N_WEBHOOK_URL,
        "n8n_status": r.status_code,
        "n8n_response": r.text
    }



