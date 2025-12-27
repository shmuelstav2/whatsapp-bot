# WhatsApp Bot

A FastAPI application for receiving and sending WhatsApp messages via n8n webhooks.

## Environments

The application supports two modes: **test** and **prod**, which use different n8n webhook URLs:

- **test** (default): Uses `https://ninsights.app.n8n.cloud/webhook-test/whatsappout`
- **prod**: Uses `https://ninsights.app.n8n.cloud/webhook/whatsappout`

Set the environment using the `ENVIRONMENT` environment variable:
```bash
export ENVIRONMENT=test  # or prod
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:

**Test Mode (default):**
```bash
# Using the run script (sets ENVIRONMENT=test automatically):
./scripts/run.sh

# Or manually:
export ENVIRONMENT=test
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Production Mode:**
```bash
# Using the production script (sets ENVIRONMENT=prod automatically):
./scripts/run-production.sh

# Or manually:
export ENVIRONMENT=prod
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Windows:**
```powershell
# PowerShell - Test mode
.\scripts\run-test.ps1

# PowerShell - Production mode
.\scripts\run-production.ps1

# CMD - Test mode
scripts\run-test.bat

# CMD - Production mode
scripts\run-production.bat
```

The API will be available at:
- Local: `http://localhost:8000`
- External: `http://YOUR_IP:8000` (when using --host 0.0.0.0)

## Endpoints

### GET `/`
Health check endpoint - returns server status.

### GET `/health`
Health check endpoint - returns server status and current environment.

### GET `/info`
Returns server information including current environment and n8n webhook URL.

### POST `/whatsapp`
Receives incoming WhatsApp messages and logs them.

### POST `/what6`
Sends a WhatsApp message via the n8n webhook.

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Server Deployment

### Option 1: Direct Run (Development/Testing)

```bash
# Run in foreground
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or use the run script
./scripts/run.sh
```

### Option 2: Run in Background with nohup

```bash
# Run in background, output to nohup.out
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > app.log 2>&1 &

# Check if running
ps aux | grep uvicorn

# View logs
tail -f app.log

# Stop the process
pkill -f "uvicorn app.main:app"
```

### Option 3: Run with screen (Recommended for simple deployments)

```bash
# Start a new screen session
screen -S whatsapp-bot

# Run the server
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Detach: Press Ctrl+A then D
# Reattach: screen -r whatsapp-bot
# List sessions: screen -ls
```

### Option 4: Run with tmux

```bash
# Start a new tmux session
tmux new -s whatsapp-bot

# Run the server
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Detach: Press Ctrl+B then D
# Reattach: tmux attach -t whatsapp-bot
# List sessions: tmux ls
```

### Option 5: Systemd Service (Production - Recommended)

**For TEST mode:**

1. Copy and edit the test service file:
```bash
sudo cp config/whatsapp-bot-test.service.example /etc/systemd/system/whatsapp-bot-test.service
sudo nano /etc/systemd/system/whatsapp-bot-test.service
# Edit paths: WorkingDirectory, User, PATH
```

2. Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable whatsapp-bot-test
sudo systemctl start whatsapp-bot-test
sudo systemctl status whatsapp-bot-test
```

**For PRODUCTION mode:**

1. Copy and edit the production service file:
```bash
sudo cp config/whatsapp-bot-prod.service.example /etc/systemd/system/whatsapp-bot-prod.service
sudo nano /etc/systemd/system/whatsapp-bot-prod.service
# Edit paths: WorkingDirectory, User, PATH
```

2. Enable and start the service:

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable whatsapp-bot

# Start the service
sudo systemctl start whatsapp-bot

# Check status
sudo systemctl status whatsapp-bot

# View logs
sudo journalctl -u whatsapp-bot -f

# Stop the service
sudo systemctl stop whatsapp-bot

# Restart the service
sudo systemctl restart whatsapp-bot
```

### Option 6: PM2 Process Manager

```bash
# Install PM2 globally
npm install -g pm2

# Start the application
pm2 start "uvicorn app.main:app --host 0.0.0.0 --port 8000" --name whatsapp-bot

# Save PM2 configuration
pm2 save

# Setup PM2 to start on boot
pm2 startup

# View logs
pm2 logs whatsapp-bot

# Monitor
pm2 monit

# Stop
pm2 stop whatsapp-bot

# Restart
pm2 restart whatsapp-bot
```

### Updating the Server

After pulling new changes from GitHub:

```bash
# Navigate to project directory
cd /path/to/whatsapp-bot

# Pull latest changes
git pull origin main

# Update dependencies (if needed)
pip install -r requirements.txt

# Restart the service (choose based on your deployment method)
# For systemd:
sudo systemctl restart whatsapp-bot

# For PM2:
pm2 restart whatsapp-bot

# For screen/tmux:
# Reattach and restart manually, or kill and restart
```



