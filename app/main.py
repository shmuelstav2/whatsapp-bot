from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.services.whatsapp_service import whatsapp_service

app = FastAPI()

# Get environment from service
ENVIRONMENT = whatsapp_service.get_environment()

# Print environment info at startup
print(f"Starting WhatsApp Bot in '{ENVIRONMENT}' mode")

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
        "n8n_webhook_url": whatsapp_service.get_webhook_url()
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
                        # ניסיון מההודעות (incoming messages)
                        if "messages" in value and len(value["messages"]) > 0:
                            phone_number = value["messages"][0].get("from")
                        # ניסיון מ-statuses (read/delivered status)
                        if not phone_number and "statuses" in value and len(value["statuses"]) > 0:
                            phone_number = value["statuses"][0].get("recipient_id")
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
    
    # בדיקה אם זו הודעת טקסט או רק status update
    has_message = False
    try:
        if "body" in data:
            body = data["body"]
            if "entry" in body and len(body["entry"]) > 0:
                entry = body["entry"][0]
                if "changes" in entry and len(entry["changes"]) > 0:
                    changes = entry["changes"][0]
                    if "value" in changes:
                        value = changes["value"]
                        # בדיקה אם יש הודעת טקסט (לא רק status)
                        if "messages" in value and len(value["messages"]) > 0:
                            has_message = True
    except (KeyError, IndexError, TypeError):
        pass
    
    print(f"DEBUG: has_message: {has_message}")
    
    # נורמליזציה של מספר הטלפון (הסרת רווחים, +, וכו')
    if phone_number and has_message:
        phone_number_normalized = phone_number.replace(" ", "").replace("-", "").replace("+", "")
        print(f"DEBUG: Normalized phone_number: '{phone_number_normalized}'")
        
        # בדיקה אם המספר ברשימה המיוחדת (גם עם וגם בלי נורמליזציה)
        if phone_number in SPECIAL_PHONE_NUMBERS or phone_number_normalized in SPECIAL_PHONE_NUMBERS:
            print(f"DEBUG: Phone number {phone_number} found in SPECIAL_PHONE_NUMBERS!")
            # התחלת תהליך בחירה בין האפשרויות
            _start_choice_process(phone_number)
        else:
            print(f"DEBUG: Phone number {phone_number} NOT in SPECIAL_PHONE_NUMBERS")
    elif phone_number and not has_message:
        print("DEBUG: Phone number found but this is a status update, not a text message - skipping")
    else:
        print("DEBUG: No phone number found in message data")

    return {"status": "ok"}


def _start_choice_process(phone_number: str):
    """
    מתחיל תהליך בחירה בין 3 אפשרויות למספר טלפון מיוחד
    """
    response_text = "אנא בחר אחת מהאפשרויות:\nא. אפשרות א\nב. אפשרות ב\nג. אפשרות ג"
    
    # שליחת התשובה דרך שירות WhatsApp
    result = whatsapp_service.send_message(phone_number, response_text)
    print(f"Sent special response to {phone_number}, status: {result.get('status_code', 'N/A')}")


@app.post("/whatsapp/send_message")
def send_message():
    """
    שולח הודעת WhatsApp דרך שירות WhatsApp
    """
    result = whatsapp_service.send_message("972542202468", "הודעה ישירות דרך n8n")
    
    return {
        "status": result.get("status", "error"),
        "environment": ENVIRONMENT,
        "n8n_webhook_url": whatsapp_service.get_webhook_url(),
        "n8n_status": result.get("status_code"),
        "n8n_response": result.get("response_text")
    }

