# Server Deployment Quick Guide

## Environments

The application supports two modes:
- **test** (default): Uses test webhook URL
- **prod**: Uses production webhook URL

Set environment with: `export ENVIRONMENT=test` or `export ENVIRONMENT=prod`

## Quick Start (Simple)

**Test Mode:**
```bash
# 1. Clone or navigate to project
cd /path/to/whatsapp-bot

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run with screen (recommended for simple setup)
screen -S whatsapp-bot-test
export ENVIRONMENT=test
uvicorn main:app --host 0.0.0.0 --port 8000
# Press Ctrl+A then D to detach
```

**Production Mode:**
```bash
screen -S whatsapp-bot-prod
export ENVIRONMENT=prod
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
# Press Ctrl+A then D to detach
```

**Or use the run scripts:**
```bash
./run.sh          # Test mode
./run-production.sh  # Production mode
```

## Update Server After Git Pull

```bash
cd /path/to/whatsapp-bot
git pull origin main
pip install -r requirements.txt
# Restart your service (see below based on your setup)
```

## Common Commands

### Check if server is running
```bash
ps aux | grep uvicorn
lsof -i :8000
```

### Stop server
```bash
# Find and kill process
pkill -f "uvicorn main:app"

# Or find PID and kill
ps aux | grep uvicorn
kill <PID>
```

### View logs
```bash
# If using nohup
tail -f app.log

# If using systemd
sudo journalctl -u whatsapp-bot -f

# If using PM2
pm2 logs whatsapp-bot
```

## Production Setup (Systemd)

**Test Mode:**
```bash
sudo cp whatsapp-bot-test.service.example /etc/systemd/system/whatsapp-bot-test.service
sudo nano /etc/systemd/system/whatsapp-bot-test.service
# Edit paths: WorkingDirectory, User, PATH

sudo systemctl daemon-reload
sudo systemctl enable whatsapp-bot-test
sudo systemctl start whatsapp-bot-test
sudo systemctl status whatsapp-bot-test
```

**Production Mode:**
```bash
sudo cp whatsapp-bot-prod.service.example /etc/systemd/system/whatsapp-bot-prod.service
sudo nano /etc/systemd/system/whatsapp-bot-prod.service
# Edit paths: WorkingDirectory, User, PATH

sudo systemctl daemon-reload
sudo systemctl enable whatsapp-bot-prod
sudo systemctl start whatsapp-bot-prod
sudo systemctl status whatsapp-bot-prod
```

## Production Setup (PM2)

1. Install PM2:
```bash
npm install -g pm2
```

2. Start with PM2:
```bash
pm2 start ecosystem.config.js.example --name whatsapp-bot
pm2 save
pm2 startup
```

## Firewall Configuration

If using UFW:
```bash
sudo ufw allow 8000/tcp
sudo ufw status
```

If using firewalld:
```bash
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

## Testing

```bash
# Test health endpoint (shows current environment)
curl http://localhost:8000/health

# Test info endpoint (shows environment and webhook URL)
curl http://localhost:8000/info

# Test from external
curl http://YOUR_SERVER_IP:8000/health
curl http://YOUR_SERVER_IP:8000/info
```

