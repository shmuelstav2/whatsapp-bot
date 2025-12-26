import os
import requests
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Get environment mode (default to 'test' if not set)
env_raw = os.getenv("ENVIRONMENT", "test")
ENVIRONMENT = env_raw.strip().lower() if env_raw else "test"

# Debug: print raw environment variable
print(f"DEBUG: ENVIRONMENT raw value: '{env_raw}'")
print(f"DEBUG: ENVIRONMENT processed value: '{ENVIRONMENT}'")

# Set N8N webhook URL based on environment
if ENVIRONMENT == "prod":
    N8N_WEBHOOK_URL = "https://ninsights.app.n8n.cloud/webhook/whatsappout"
else:
    N8N_WEBHOOK_URL = "https://ninsights.app.n8n.cloud/webhook-test/whatsappout"

# Print environment info at startup
print(f"Starting WhatsApp Bot in '{ENVIRONMENT}' mode")
print(f"N8N Webhook URL: {N8N_WEBHOOK_URL}")

# רשימת מספרי טלפון לקבלת תשובה עם 3 אפשרויות
SPECIAL_PHONE_NUMBERS = [
    "972542202468",
    # הוסף כאן מספרי טלפון נוספים
]

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

@app.post("/whatsapp/get_message")
async def get_message(request: Request):
    """
    מקבל הודעת WhatsApp נכנסת ומטפל בה
    """
    data = await request.json()
    print("Incoming WhatsApp message:")
    print(data)

    # חילוץ מספר הטלפון מהבקשה
    phone_number = data.get("from") or data.get("phone_number") or data.get("phone") or data.get("sender")
    
    # בדיקה אם המספר ברשימה המיוחדת
    if phone_number and phone_number in SPECIAL_PHONE_NUMBERS:
        # התחלת תהליך בחירה בין האפשרויות
        _start_choice_process(phone_number)

    return {"status": "ok"}


def _start_choice_process(phone_number: str):
    """
    מתחיל תהליך בחירה בין 3 אפשרויות למספר טלפון מיוחד
    """
    response_text = "אנא בחר אחת מהאפשרויות:\nא. אפשרות א\nב. אפשרות ב\nג. אפשרות ג"
    
    # שליחת התשובה דרך N8N
    payload = {
        "to": phone_number,
        "text": response_text
    }
    
    try:
        r = requests.post(N8N_WEBHOOK_URL, json=payload)
        print(f"Sent special response to {phone_number}, status: {r.status_code}")
    except Exception as e:
        print(f"Error sending response: {e}")


@app.post("/whatsapp/send_message")
def send_message():
    """
    שולח הודעת WhatsApp דרך N8N
    """
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



