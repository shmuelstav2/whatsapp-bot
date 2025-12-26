import requests
from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/whatsapp")
async def receive_whatsapp(request: Request):
    data = await request.json()
    print("Incoming WhatsApp message:")
    print(data)

    return {"status": "ok"}

N8N_WEBHOOK_URL = "https://ninsights.app.n8n.cloud/webhook-test/whatsappout"

@app.post("/what6")
def send_whatsapp():
    payload = {
        "to": "972542202468",
        "text": "הודעה ישירות דרך n8n"
    }

    r = requests.post(N8N_WEBHOOK_URL, json=payload)

    return {
        "status": "sent",
        "n8n_status": r.status_code,
        "n8n_response": r.text
    }



