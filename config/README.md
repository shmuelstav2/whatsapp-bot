# Configuration Files

קבצי הגדרות ודוגמאות לאפליקציית WhatsApp Bot.

## קבצים

- `ecosystem.config.js.example` - הגדרת PM2 לדוגמה
- `whatsapp-bot.service.example` - Systemd service לדוגמה (כללי)
- `whatsapp-bot-test.service.example` - Systemd service לדוגמה (מצב test)
- `whatsapp-bot-prod.service.example` - Systemd service לדוגמה (מצב production)

## שימוש

### PM2 (ecosystem.config.js)
```bash
cp config/ecosystem.config.js.example ecosystem.config.js
# ערוך את הקובץ לפי הצורך
pm2 start ecosystem.config.js
```

### Systemd Service
```bash
# למצב test
sudo cp config/whatsapp-bot-test.service.example /etc/systemd/system/whatsapp-bot-test.service
sudo nano /etc/systemd/system/whatsapp-bot-test.service
sudo systemctl enable whatsapp-bot-test
sudo systemctl start whatsapp-bot-test

# למצב production
sudo cp config/whatsapp-bot-prod.service.example /etc/systemd/system/whatsapp-bot-prod.service
sudo nano /etc/systemd/system/whatsapp-bot-prod.service
sudo systemctl enable whatsapp-bot-prod
sudo systemctl start whatsapp-bot-prod
```

**חשוב**: לפני השימוש, ערוך את הקבצים ועדכן:
- `/path/to/venv/bin` - נתיב ל-venv שלך
- `/path/to/whatsapp-bot` - נתיב לפרויקט
- `your-username` - שם המשתמש

