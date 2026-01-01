from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.services.whatsapp_service import whatsapp_service
from app.services.flow_manager import flow_manager

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
    
    # בדיקה מה webhook URL שמגיע
    webhook_url = data.get("webhookUrl", "N/A")
    print(f"DEBUG: webhookUrl from data: {webhook_url}")
    print(f"DEBUG: This webhook should receive INCOMING messages")
    
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
                                
                                # טיפול בהודעה דרך flow_manager (רק אם המספר ברשימה המיוחדת)
                                phone_number_normalized = phone_number.replace(" ", "").replace("-", "").replace("+", "")
                                if phone_number in SPECIAL_PHONE_NUMBERS or phone_number_normalized in SPECIAL_PHONE_NUMBERS:
                                    _handle_user_message(phone_number, first_msg)
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
        # הערה: הטיפול בהודעות מתבצע ב-_handle_user_message
        if phone_number in SPECIAL_PHONE_NUMBERS or phone_number_normalized in SPECIAL_PHONE_NUMBERS:
            print(f"DEBUG: ✓✓✓ Phone number {phone_number} found in SPECIAL_PHONE_NUMBERS!")
            # הטיפול מתבצע ב-_handle_user_message
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


def _handle_user_message(phone_number: str, message: dict):
    """
    מטפל בהודעה מהמשתמש - חילוץ choice_id או text ושימוש ב-flow_manager
    """
    from app.services.flow_manager import FlowState
    
    message_type = message.get("type", "")
    choice_id = None
    message_text = ""
    
    # חילוץ choice_id אם זו בחירה מ-interactive message
    if message_type == "interactive":
        interactive = message.get("interactive", {})
        interactive_type = interactive.get("type", "")
        if interactive_type == "list_reply":
            choice_id = interactive.get("list_reply", {}).get("id")
        elif interactive_type == "button_reply":
            choice_id = interactive.get("button_reply", {}).get("id")
        print(f"DEBUG: Interactive message detected, choice_id: {choice_id}")
    
    # חילוץ טקסט אם זו הודעת טקסט רגילה
    elif message_type == "text":
        message_text = message.get("text", {}).get("body", "")
        print(f"DEBUG: Text message detected, text: '{message_text}'")
    
    # בדיקה אם צריך להתחיל flow חדש (אם המשתמש במצב IDLE וזו הודעה חדשה)
    current_state = flow_manager.get_user_state(phone_number)
    print(f"DEBUG: Current user state: {current_state}, message_type: {message_type}, has_text: {bool(message_text)}")
    
    if current_state == FlowState.IDLE and message_type == "text" and message_text:
        # אם המשתמש במצב IDLE ושולח הודעה, נשלח לו את הרשימה הראשונית
        print(f"DEBUG: User in IDLE state, sending initial choices")
        _start_choice_process(phone_number)
        return
    
    # אם המשתמש במצב IDLE ובחר אפשרות מה-List, זה יטופל ב-process_message
    if current_state == FlowState.IDLE and choice_id:
        print(f"DEBUG: User in IDLE state, processing choice: {choice_id}")
        # ימשיך ל-process_message למטה
    
    # עיבוד ההודעה דרך flow_manager
    print(f"DEBUG: Processing message through flow_manager: choice_id={choice_id}, text='{message_text}'")
    response_text, next_payload = flow_manager.process_message(phone_number, choice_id, message_text)
    
    # שליחת תשובה למשתמש
    if response_text:
        print(f"DEBUG: Sending response to user: '{response_text}'")
        whatsapp_service.send_message(phone_number, response_text)
    
    # אם יש next_payload (למשל interactive message נוסף), לשלוח אותו
    if next_payload:
        print(f"DEBUG: Sending next interactive message")
        # כאן אפשר לשלוח interactive message נוסף אם צריך


def _start_choice_process(phone_number: str):
    """
    מתחיל תהליך בחירה בין אפשרויות למספר טלפון מיוחד
    שולח הודעת Interactive List Message עם רשימת אפשרויות
    """
    print(f"DEBUG: _start_choice_process called with phone_number: '{phone_number}'")
    body_text = "בחר אחת מהאפשרויות הבאות:"
    
    # שליחת הודעת Interactive List עם כל האפשרויות
    print(f"DEBUG: Calling send_interactive_message...")
    result = whatsapp_service.send_interactive_message(
        phone_number=phone_number,
        body_text=body_text,
        options=[
            {"id": "proposal_for_discussion", "title": "מצע לדיון"},
            {"id": "new_reminder", "title": "תזכורת חדשה"},
            {"id": "control_and_monitoring", "title": "בקרה ומעקב"},
            {"id": "new_task", "title": "משימה חדשה"}
        ],
        button_text="בחר אפשרות"
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

