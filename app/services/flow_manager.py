"""
מנהל זרימת השיחה (Conversation Flow Manager)
מנהל את התהליכים והמדינות של המשתמש לפי בחירותיו
"""
from typing import Dict, Optional, Callable
from enum import Enum


class FlowState(Enum):
    """מצבים שונים בזרימת השיחה"""
    IDLE = "idle"  # מצב מנוחה - מחכה לבחירה ראשונית
    PROPOSAL_CHOICE = "proposal_choice"  # בחירה בין מצע חדש/קיים
    PROPOSAL_NEW_NAME = "proposal_new_name"  # שאלת שם הדיון
    PROPOSAL_NEW_PARTICIPANTS = "proposal_new_participants"  # שאלת משתתפים
    PROPOSAL_NEW_CONTENT = "proposal_new_content"  # שאלת תוכן הדיון
    PROPOSAL_COMPLETE = "proposal_complete"  # סיום - הצגת סיכום


class FlowManager:
    """מנהל את זרימת השיחה של המשתמש"""
    
    def __init__(self):
        # Dictionary: phone_number -> current_state
        self.user_states: Dict[str, FlowState] = {}
        # Dictionary: phone_number -> collected_data
        self.user_data: Dict[str, Dict] = {}
    
    def reset_user_flow(self, phone_number: str):
        """מאפס את הזרימה של משתמש"""
        self.user_states[phone_number] = FlowState.IDLE
        self.user_data[phone_number] = {}
    
    def get_user_state(self, phone_number: str) -> FlowState:
        """מחזיר את המצב הנוכחי של המשתמש"""
        return self.user_states.get(phone_number, FlowState.IDLE)
    
    def set_user_state(self, phone_number: str, state: FlowState):
        """מגדיר מצב חדש למשתמש"""
        self.user_states[phone_number] = state
        print(f"DEBUG flow_manager: Set state for {phone_number} to {state}")
    
    def get_user_data(self, phone_number: str) -> Dict:
        """מחזיר את הנתונים שנאספו מהמשתמש"""
        return self.user_data.get(phone_number, {})
    
    def set_user_data(self, phone_number: str, key: str, value: str):
        """שומר נתון של המשתמש"""
        if phone_number not in self.user_data:
            self.user_data[phone_number] = {}
        self.user_data[phone_number][key] = value
    
    def handle_initial_choice(self, phone_number: str, choice_id: str) -> tuple[str, Optional[Dict]]:
        """
        מטפל בבחירה הראשונית (מצע לדיון, תזכורת חדשה, וכו')
        Returns: (response_text, next_message_payload)
        """
        if choice_id == "proposal_for_discussion":
            # התחלת flow של מצע לדיון
            self.set_user_state(phone_number, FlowState.PROPOSAL_CHOICE)
            self.user_data[phone_number] = {"type": "proposal"}
            
            # שליחת הודעת בחירה בין חדש/קיים
            from app.services.whatsapp_service import whatsapp_service
            
            whatsapp_service.send_interactive_message(
                phone_number=phone_number,
                body_text="מה תרצה לעשות?",
                options=[
                    {"id": "proposal_new", "title": "מצע חדש"},
                    {"id": "proposal_existing", "title": "מצע קיים"}
                ],
                button_text="בחר אפשרות"
            )
            
            return "", None  # ההודעה נשלחה כבר, אין צורך בתגובה נוספת
            
        elif choice_id == "new_reminder":
            return "תזכורת חדשה - עדיין בפיתוח", None
        elif choice_id == "control_and_monitoring":
            return "בקרה ומעקב - עדיין בפיתוח", None
        elif choice_id == "new_task":
            return "משימה חדשה - עדיין בפיתוח", None
        else:
            return "אני לא מבין את הבחירה שלך", None
    
    def handle_proposal_choice(self, phone_number: str, choice_id: str, message_text: str) -> tuple[str, Optional[Dict]]:
        """
        מטפל בבחירה בין מצע חדש/קיים
        """
        if choice_id == "proposal_new":
            # התחלת תהליך מצע חדש
            self.set_user_state(phone_number, FlowState.PROPOSAL_NEW_NAME)
            return "מה שם הדיון?", None
        elif choice_id == "proposal_existing":
            # מצע קיים - עדיין לא מיושם
            self.reset_user_flow(phone_number)
            return "מצע קיים - עדיין בפיתוח", None
        elif message_text.lower() in ["סיים", "סיום", "ביטול", "exit", "cancel"]:
            # המשתמש רוצה לסיים
            self.reset_user_flow(phone_number)
            return "התהליך בוטל. תודה!", None
        else:
            return "אנא בחר אחת מהאפשרויות או הקלד 'סיום' כדי לסיים", None
    
    def handle_proposal_name(self, phone_number: str, message_text: str) -> tuple[str, Optional[Dict]]:
        """
        מטפל בשם הדיון
        """
        if message_text.lower() in ["סיים", "סיום", "ביטול", "exit", "cancel"]:
            self.reset_user_flow(phone_number)
            return "התהליך בוטל. תודה!", None
        
        # שמירת שם הדיון
        self.set_user_data(phone_number, "name", message_text)
        self.set_user_state(phone_number, FlowState.PROPOSAL_NEW_PARTICIPANTS)
        return "מי המשתתפים בדיון? (הקלד את שמות המשתתפים מופרדים בפסיקים)", None
    
    def handle_proposal_participants(self, phone_number: str, message_text: str) -> tuple[str, Optional[Dict]]:
        """
        מטפל ברשימת המשתתפים
        """
        if message_text.lower() in ["סיים", "סיום", "ביטול", "exit", "cancel"]:
            self.reset_user_flow(phone_number)
            return "התהליך בוטל. תודה!", None
        
        # שמירת המשתתפים
        self.set_user_data(phone_number, "participants", message_text)
        self.set_user_state(phone_number, FlowState.PROPOSAL_NEW_CONTENT)
        return "מה תוכן הדיון?", None
    
    def handle_proposal_content(self, phone_number: str, message_text: str) -> tuple[str, Optional[Dict]]:
        """
        מטפל בתוכן הדיון - השלב האחרון לפני סיכום
        """
        if message_text.lower() in ["סיים", "סיום", "ביטול", "exit", "cancel"]:
            self.reset_user_flow(phone_number)
            return "התהליך בוטל. תודה!", None
        
        # שמירת התוכן
        self.set_user_data(phone_number, "content", message_text)
        self.set_user_state(phone_number, FlowState.PROPOSAL_COMPLETE)
        
        # בניית סיכום
        data = self.get_user_data(phone_number)
        summary = self._build_proposal_summary(data)
        
        # איפוס הזרימה
        self.reset_user_flow(phone_number)
        
        return summary, None
    
    def _build_proposal_summary(self, data: Dict) -> str:
        """בונה סיכום של מצע הדיון"""
        summary_lines = [
            "📋 סיכום מצע הדיון:",
            "",
            f"📝 שם הדיון: {data.get('name', 'לא צוין')}",
            f"👥 משתתפים: {data.get('participants', 'לא צוין')}",
            f"📄 תוכן הדיון:",
            data.get('content', 'לא צוין'),
            "",
            "✅ הפרטים נשמרו בהצלחה!"
        ]
        return "\n".join(summary_lines)
    
    def process_message(self, phone_number: str, choice_id: Optional[str], message_text: str) -> tuple[str, Optional[Dict]]:
        """
        עיבוד הודעה מהמשתמש - נקודת הכניסה הראשית
        Returns: (response_text, next_message_payload)
        """
        current_state = self.get_user_state(phone_number)
        print(f"DEBUG flow_manager: Processing message - phone: {phone_number}, state: {current_state}, choice_id: {choice_id}, text: '{message_text}'")
        
        # אם זו בחירה ראשונית (choice_id קיים והמשתמש במצב IDLE)
        if choice_id and current_state == FlowState.IDLE:
            print(f"DEBUG flow_manager: Handling initial choice: {choice_id}")
            return self.handle_initial_choice(phone_number, choice_id)
        
        # טיפול לפי המצב הנוכחי
        if current_state == FlowState.PROPOSAL_CHOICE:
            print(f"DEBUG flow_manager: Handling PROPOSAL_CHOICE state")
            return self.handle_proposal_choice(phone_number, choice_id or "", message_text)
        elif current_state == FlowState.PROPOSAL_NEW_NAME:
            print(f"DEBUG flow_manager: Handling PROPOSAL_NEW_NAME state")
            return self.handle_proposal_name(phone_number, message_text)
        elif current_state == FlowState.PROPOSAL_NEW_PARTICIPANTS:
            print(f"DEBUG flow_manager: Handling PROPOSAL_NEW_PARTICIPANTS state")
            return self.handle_proposal_participants(phone_number, message_text)
        elif current_state == FlowState.PROPOSAL_NEW_CONTENT:
            print(f"DEBUG flow_manager: Handling PROPOSAL_NEW_CONTENT state")
            return self.handle_proposal_content(phone_number, message_text)
        else:
            # מצב IDLE או לא מזוהה - אם יש choice_id, נטפל בו
            if choice_id:
                print(f"DEBUG flow_manager: State is {current_state}, but choice_id provided, handling as initial choice")
                return self.handle_initial_choice(phone_number, choice_id)
            else:
                print(f"DEBUG flow_manager: State is {current_state}, no choice_id, sending initial message")
                # אם המשתמש במצב לא מזוהה, נשלח לו את הרשימה הראשונית
                return "אנא בחר אחת מהאפשרויות", None


# יצירת instance גלובלי
flow_manager = FlowManager()

