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
    print("=" * 50)
    print("Incoming WhatsApp message:")
    print(data)
    print("=" * 50)

    # חילוץ מספר הטלפון מהבקשה
    # המבנה של WhatsApp: body['entry'][0]['changes'][0]['value']['messages'][0]['from']
    phone_number = None
    
    # ניסיון לחלץ מהמבנה של WhatsApp Business API
    try:
        if "body" in data:
            body = data["body"]
            if "entry" in body and len(body["entry"]) > 0:
                entry = body["entry"][0]
                if "changes" in entry and len(entry["changes"]) > 0:
                    changes = entry["changes"][0]
                    if "value" in changes:
                        value = changes["value"]
                        # ניסיון מההודעות
                        if "messages" in value and len(value["messages"]) > 0:
                            phone_number = value["messages"][0].get("from")
                        # ניסיון מהקontacts
                        if not phone_number and "contacts" in value and len(value["contacts"]) > 0:
                            phone_number = value["contacts"][0].get("wa_id")
    except (KeyError, IndexError, TypeError) as e:
        print(f"DEBUG: Error extracting phone from WhatsApp structure: {e}")
    
    # ניסיון חילוץ מהשדות הישירים (למקרה שהמבנה שונה)
    if not phone_number:
        phone_number = data.get("from") or data.get("phone_number") or data.get("phone") or data.get("sender")
    
    print(f"DEBUG: Extracted phone_number: '{phone_number}'")
    print(f"DEBUG: SPECIAL_PHONE_NUMBERS list: {SPECIAL_PHONE_NUMBERS}")
    
    # נורמליזציה של מספר הטלפון (הסרת רווחים, +, וכו')
    if phone_number:
        phone_number_normalized = phone_number.replace(" ", "").replace("-", "").replace("+", "")
        print(f"DEBUG: Normalized phone_number: '{phone_number_normalized}'")
        
        # בדיקה אם המספר ברשימה המיוחדת (גם עם וגם בלי נורמליזציה)
        if phone_number in SPECIAL_PHONE_NUMBERS or phone_number_normalized in SPECIAL_PHONE_NUMBERS:
            print(f"DEBUG: Phone number {phone_number} found in SPECIAL_PHONE_NUMBERS!")
            # התחלת תהליך בחירה בין האפשרויות
            _start_choice_process(phone_number)
        else:
            print(f"DEBUG: Phone number {phone_number} NOT in SPECIAL_PHONE_NUMBERS")
    else:
        print("DEBUG: No phone number found in message data")

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
    
    print(f"DEBUG: Sending choice process message to {phone_number}")
    print(f"DEBUG: Payload: {payload}")
    print(f"DEBUG: N8N Webhook URL: {N8N_WEBHOOK_URL}")
    
    try:
        r = requests.post(N8N_WEBHOOK_URL, json=payload)
        print(f"DEBUG: Response status: {r.status_code}")
        print(f"DEBUG: Response text: {r.text}")
        print(f"Sent special response to {phone_number}, status: {r.status_code}")
    except Exception as e:
        print(f"ERROR: Error sending response: {e}")
        import traceback
        traceback.print_exc()


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



