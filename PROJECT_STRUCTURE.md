# מבנה הפרויקט

## סקירה כללית

```
whatsapp-bot/
├── app/                          # קוד האפליקציה הראשי
│   ├── __init__.py              # הופך את app למודול Python
│   ├── main.py                  # נקודת הכניסה - FastAPI application
│   └── services/                # תיקיית השירותים
│       ├── __init__.py          # הופך את services למודול
│       └── whatsapp_service.py  # שירות לשליחת הודעות WhatsApp
│
├── scripts/                      # סקריפטי הרצה
│   ├── README.md                # תיעוד סקריפטים
│   ├── run.sh                   # הרצה במצב test (Linux/Mac)
│   ├── run-production.sh        # הרצה במצב production (Linux/Mac)
│   ├── run-test.bat             # הרצה במצב test (Windows CMD)
│   ├── run-production.bat       # הרצה במצב production (Windows CMD)
│   ├── run-test.ps1             # הרצה במצב test (Windows PowerShell)
│   └── run-production.ps1       # הרצה במצב production (Windows PowerShell)
│
├── config/                       # קבצי הגדרות ודוגמאות
│   ├── README.md                # תיעוד קבצי הגדרות
│   ├── ecosystem.config.js.example      # הגדרת PM2 לדוגמה
│   ├── whatsapp-bot.service.example     # Systemd service כללי לדוגמה
│   ├── whatsapp-bot-test.service.example # Systemd service למצב test
│   └── whatsapp-bot-prod.service.example # Systemd service למצב production
│
├── requirements.txt             # תלויות Python
├── README.md                    # תיעוד ראשי
└── SERVER-DEPLOYMENT.md         # מדריך פריסה לשרת
```

## תיאור תיקיות

### `app/`
קוד האפליקציה הראשי. כולל את כל הלוגיקה של האפליקציה.

- **`main.py`**: נקודת הכניסה - מכיל את כל ה-endpoints של FastAPI
- **`services/`**: שירותים נפרדים לניהול פונקציונליות ספציפית
  - `whatsapp_service.py`: שירות לשליחת הודעות WhatsApp דרך N8N

### `scripts/`
סקריפטי הרצה לנוחות. כל סקריפט מגדיר את משתנה הסביבה ומריץ את האפליקציה.

### `config/`
קבצי הגדרות לדוגמה עבור פריסה ב-production:
- קבצי Systemd service לניהול האפליקציה כ-service
- קובץ PM2 ecosystem לניהול עם PM2

## איך להשתמש

### הרצה מהירה
```bash
# Linux/Mac - Test
./scripts/run.sh

# Linux/Mac - Production
./scripts/run-production.sh

# Windows PowerShell - Test
.\scripts\run-test.ps1

# Windows PowerShell - Production
.\scripts\run-production.ps1
```

### פריסה ל-production
ראה `SERVER-DEPLOYMENT.md` לפרטים מלאים על פריסה ב-production.

