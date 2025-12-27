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
    
    # הדפסת המבנה המלא של הנתונים
    try:
        import json
        print("DEBUG: Full data structure (JSON):")
        print(json.dumps(data, indent=2, default=str, ensure_ascii=False))
    except Exception as e:
        print(f"DEBUG: Could not print JSON: {e}")

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
    print(f"DEBUG: phone_number type: {type(phone_number)}")
    if phone_number:
        print(f"DEBUG: phone_number repr: {repr(phone_number)}")
        for idx, special_num in enumerate(SPECIAL_PHONE_NUMBERS):
            print(f"DEBUG: Comparing '{phone_number}' (type: {type(phone_number)}) with '{special_num}' (type: {type(special_num)}) - Match: {phone_number == special_num}")
    
    # בדיקה אם זו הודעת טקסט או רק status update
    has_message = False
    has_status = False
    try:
        print("DEBUG: Checking data structure...")
        print(f"DEBUG: data has 'body' key: {'body' in data}")
        if "body" in data:
            body = data["body"]
            print(f"DEBUG: body type: {type(body)}")
            print(f"DEBUG: body keys: {body.keys() if isinstance(body, dict) else 'not a dict'}")
            if "entry" in body and len(body["entry"]) > 0:
                entry = body["entry"][0]
                print(f"DEBUG: entry keys: {entry.keys() if isinstance(entry, dict) else 'not a dict'}")
                if "changes" in entry and len(entry["changes"]) > 0:
                    changes = entry["changes"][0]
                    print(f"DEBUG: changes keys: {changes.keys() if isinstance(changes, dict) else 'not a dict'}")
                    if "value" in changes:
                        value = changes["value"]
                        print(f"DEBUG: value type: {type(value)}")
                        print(f"DEBUG: value keys: {value.keys() if isinstance(value, dict) else 'not a dict'}")
                        
                        # הדפסת התוכן המלא של value
                        print("DEBUG: Full value content:")
                        try:
                            import json
                            print(json.dumps(value, indent=2, default=str, ensure_ascii=False))
                        except:
                            print(str(value))
                        
                        # בדיקה אם יש הודעת טקסט (לא רק status)
                        if "messages" in value and len(value["messages"]) > 0:
                            has_message = True
                            messages = value["messages"]
                            print(f"DEBUG: ✓✓✓ Found {len(messages)} message(s) in value")
                            # הדפסת פרטי ההודעה הראשונה
                            if len(messages) > 0:
                                first_msg = messages[0]
                                print(f"DEBUG: First message type: {first_msg.get('type', 'unknown')}")
                                print(f"DEBUG: First message keys: {first_msg.keys() if isinstance(first_msg, dict) else 'not a dict'}")
                                print(f"DEBUG: First message content:")
                                try:
                                    print(json.dumps(first_msg, indent=2, default=str, ensure_ascii=False))
                                except:
                                    print(str(first_msg))
                        else:
                            print("DEBUG: ✗ No 'messages' key in value or messages list is empty")
                        
                        # בדיקה אם יש status
                        if "statuses" in value and len(value["statuses"]) > 0:
                            has_status = True
                            print(f"DEBUG: Found statuses in value, count: {len(value['statuses'])}")
                        else:
                            print("DEBUG: ✗ No 'statuses' key in value or statuses list is empty")
                    else:
                        print("DEBUG: ✗ No 'value' key in changes")
                else:
                    print("DEBUG: ✗ No 'changes' in entry or changes list is empty")
            else:
                print("DEBUG: ✗ No 'entry' in body or entry list is empty")
        else:
            print("DEBUG: ✗ No 'body' key in data")
    except (KeyError, IndexError, TypeError) as e:
        print(f"DEBUG: Error checking has_message: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"DEBUG: has_message: {has_message}, has_status: {has_status}")
    
    # נורמליזציה של מספר הטלפון (הסרת רווחים, +, וכו')
    if phone_number and has_message:
        phone_number_normalized = phone_number.replace(" ", "").replace("-", "").replace("+", "")
        print(f"DEBUG: Normalized phone_number: '{phone_number_normalized}'")
        print(f"DEBUG: Checking if '{phone_number}' in SPECIAL_PHONE_NUMBERS: {phone_number in SPECIAL_PHONE_NUMBERS}")
        print(f"DEBUG: Checking if '{phone_number_normalized}' in SPECIAL_PHONE_NUMBERS: {phone_number_normalized in SPECIAL_PHONE_NUMBERS}")
        
        # בדיקה אם המספר ברשימה המיוחדת (גם עם וגם בלי נורמליזציה)
        if phone_number in SPECIAL_PHONE_NUMBERS or phone_number_normalized in SPECIAL_PHONE_NUMBERS:
            print(f"DEBUG: ✓✓✓ Phone number {phone_number} found in SPECIAL_PHONE_NUMBERS!")
            print(f"DEBUG: ✓✓✓ Starting choice process - will send interactive message with buttons")
            # התחלת תהליך בחירה בין האפשרויות
            _start_choice_process(phone_number)
        else:
            print(f"DEBUG: ✗ Phone number {phone_number} NOT in SPECIAL_PHONE_NUMBERS")
            print(f"DEBUG: Comparison details:")
            print(f"  - phone_number: '{phone_number}' (length: {len(phone_number)})")
            print(f"  - phone_number_normalized: '{phone_number_normalized}' (length: {len(phone_number_normalized)})")
            print(f"  - SPECIAL_PHONE_NUMBERS contains: {SPECIAL_PHONE_NUMBERS}")
    elif phone_number and not has_message:
        if has_status:
            print("DEBUG: ⚠️ Phone number found but this is a STATUS UPDATE (read/delivered), not a TEXT MESSAGE")
            print("DEBUG: ℹ️  To trigger the interactive message, please send a NEW TEXT MESSAGE (not just read a message)")
        else:
            print("DEBUG: ⚠️ Phone number found but has_message is False and has_status is False - this shouldn't happen!")
            print("DEBUG: Full data structure:")
            try:
                import json
                print(json.dumps(data, indent=2, default=str))
            except:
                print(str(data))
    else:
        print("DEBUG: No phone number found in message data")

    return {"status": "ok"}


def _start_choice_process(phone_number: str):
    """
    מתחיל תהליך בחירה בין 3 אפשרויות למספר טלפון מיוחד
    שולח הודעת Interactive Message עם 3 כפתורי בחירה
    """
    print(f"DEBUG: _start_choice_process called with phone_number: '{phone_number}'")
    body_text = "אנא בחר אחת מהאפשרויות:"
    
    # שליחת הודעת Interactive עם כפתורי בחירה
    print(f"DEBUG: Calling send_interactive_message...")
    result = whatsapp_service.send_interactive_message(
        phone_number=phone_number,
        body_text=body_text,
        options=[
            {"id": "option_a", "title": "א. אפשרות א"},
            {"id": "option_b", "title": "ב. אפשרות ב"},
            {"id": "option_c", "title": "ג. אפשרות ג"}
        ]
    )
    print(f"DEBUG: send_interactive_message result: {result}")
    print(f"Sent interactive message to {phone_number}, status: {result.get('status_code', 'N/A')}")
    if result.get('status') == 'error':
        print(f"ERROR: Failed to send interactive message: {result.get('error', 'Unknown error')}")


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

