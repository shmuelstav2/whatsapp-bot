"""
שירות לשליחת הודעות WhatsApp דרך N8N
"""
import os
import requests


class WhatsAppService:
    """
    שירות לניהול שליחת הודעות WhatsApp
    """
    
    def __init__(self):
        """אתחול השירות - קביעת URL של N8N לפי סביבת הריצה"""
        env_raw = os.getenv("ENVIRONMENT", "test")
        self.environment = env_raw.strip().lower() if env_raw else "test"
        
        # Set N8N webhook URL based on environment
        if self.environment == "prod":
            self.n8n_webhook_url = "https://ninsights.app.n8n.cloud/webhook/whatsappout"
        else:
            self.n8n_webhook_url = "https://ninsights.app.n8n.cloud/webhook-test/whatsappout"
        
        print(f"WhatsAppService initialized in '{self.environment}' mode")
        print(f"N8N Webhook URL: {self.n8n_webhook_url}")
    
    def send_message(self, phone_number: str, text: str) -> dict:
        """
        שולח הודעת WhatsApp טקסט רגילה
        
        Args:
            phone_number: מספר הטלפון של הנמען
            text: תוכן ההודעה
            
        Returns:
            dict עם פרטי התגובה מהשרת
        """
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "text": {
                "body": text
            }
        }
        
        print(f"DEBUG: Sending WhatsApp message to {phone_number}")
        print(f"DEBUG: Payload: {payload}")
        print(f"DEBUG: N8N Webhook URL: {self.n8n_webhook_url}")
        
        try:
            response = requests.post(self.n8n_webhook_url, json=payload)
            print(f"DEBUG: Response status: {response.status_code}")
            print(f"DEBUG: Response text: {response.text}")
            
            return {
                "status": "sent" if response.status_code == 200 else "error",
                "status_code": response.status_code,
                "response_text": response.text,
                "phone_number": phone_number,
                "message_text": text
            }
        except Exception as e:
            print(f"ERROR: Error sending WhatsApp message: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "error": str(e),
                "phone_number": phone_number,
                "message_text": text
            }
    
    def send_interactive_message(self, phone_number: str, body_text: str, 
                                 options=None, button_text="בחר אפשרות") -> dict:
        """
        שולח הודעת WhatsApp Interactive List עם רשימת אפשרויות
        
        Args:
            phone_number: מספר הטלפון של הנמען
            body_text: הטקסט הראשי של ההודעה
            options: רשימה של אפשרויות. כל אפשרות היא dict עם:
                    - "id": מזהים ייחודיים (למשל "proposal_for_discussion")
                    - "title": כותרת האפשרות (למשל "מצע לדיון")
                    - "description": תיאור אופציונלי (לא חובה)
                    אם לא מסופק, ישתמש ב-4 אפשרויות ברירת מחדל
            button_text: טקסט הכפתור (ברירת מחדל: "בחר אפשרות")
            
        Returns:
            dict עם פרטי התגובה מהשרת
        """
        # אפשרויות ברירת מחדל
        if options is None:
            options = [
                {"id": "proposal_for_discussion", "title": "מצע לדיון"},
                {"id": "new_reminder", "title": "תזכורת חדשה"},
                {"id": "control_and_monitoring", "title": "בקרה ומעקב"},
                {"id": "new_task", "title": "משימה חדשה"}
            ]
        
        # בניית rows (שורות) עבור List Message
        rows = []
        for option in options:
            row = {
                "id": option["id"],
                "title": option["title"]
            }
            # הוספת description אם קיים
            if "description" in option:
                row["description"] = option["description"]
            rows.append(row)
        
        # בניית payload ל-Interactive List Message
        # פורמט WhatsApp Business API - List Message
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {
                    "text": body_text
                },
                "action": {
                    "button": button_text,
                    "sections": [
                        {
                            "title": "אפשרויות",
                            "rows": rows
                        }
                    ]
                }
            }
        }
        
        print(f"DEBUG: Sending WhatsApp interactive message to {phone_number}")
        print(f"DEBUG: Payload: {payload}")
        print(f"DEBUG: N8N Webhook URL: {self.n8n_webhook_url}")
        
        try:
            response = requests.post(self.n8n_webhook_url, json=payload)
            print(f"DEBUG: Response status: {response.status_code}")
            print(f"DEBUG: Response text: {response.text}")
            
            return {
                "status": "sent" if response.status_code == 200 else "error",
                "status_code": response.status_code,
                "response_text": response.text,
                "phone_number": phone_number,
                "message_type": "interactive"
            }
        except Exception as e:
            print(f"ERROR: Error sending WhatsApp interactive message: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "error": str(e),
                "phone_number": phone_number,
                "message_type": "interactive"
            }
    
    def get_webhook_url(self) -> str:
        """מחזיר את ה-URL של ה-webhook"""
        return self.n8n_webhook_url
    
    def get_environment(self) -> str:
        """מחזיר את סביבת הריצה"""
        return self.environment


# יצירת instance גלובלי של השירות
whatsapp_service = WhatsAppService()

