from fastapi import FastAPI, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from Backend.supabase_client import supabase
from Backend.rag import process_user_query, UserSession
from twilio.twiml.messaging_response import MessagingResponse

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pre-authenticated default user (deepak.mehta)
DEFAULT_USERNAME = "deepak.mehta"

def get_default_user_session():
    result = supabase.table("users").select("*").eq("username", DEFAULT_USERNAME).execute()
    if result.data:
        user = result.data[0]
        return UserSession(
            user_id=user["user_id"],
            username=user["username"],
            role=user["role"],
            dealer_id=user.get("dealer_id"),
        )
    return None

@app.post("/api/login")
async def login(request: Request):
    try:
        data = await request.json()
        username = data.get("username", "").strip()
        password = data.get("password", "").strip()
        role = data.get("role", "").strip().lower()

        result = supabase.table("users").select("*") \
            .eq("username", username) \
            .eq("password", password) \
            .eq("role", role) \
            .execute()

        if result.data:
            return {
                "success": True,
                "message": "Login successful",
                "user": result.data[0]
            }
        else:
            return {"success": False, "message": "Invalid credentials"}

    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "message": str(e)})

@app.post("/api/query")
async def query(request: Request):
    try:
        data = await request.json()
        username = data.get("username", "").strip()
        user_query = data.get("query")

        # Always return default user session (hardcoded)
        user_session = get_default_user_session()
        if not user_session:
            return JSONResponse(status_code=401, content={"success": False, "message": "User session not found"})

        answer = process_user_query(user_query, user_session)
        return {"success": True, "answer": answer}

    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "message": str(e)})

# ✅ Twilio WhatsApp Webhook
@app.post("/whatsapp")
async def whatsapp_webhook(Body: str = Form(...), From: str = Form(...)):
    print(f"[📨 WHATSAPP] From: {From} | Message: {Body}")

    user_session = get_default_user_session()
    if not user_session:
        twiml = MessagingResponse()
        twiml.message("❌ Could not authenticate default user.")
        return Response(content=str(twiml), media_type="application/xml")

    try:
        answer = process_user_query(Body, user_session)
    except Exception as e:
        print(f"[ERROR] while processing WhatsApp message: {e}")
        answer = "⚠️ An error occurred while processing your request."

    twiml = MessagingResponse()
    twiml.message(answer)
    return Response(content=str(twiml), media_type="application/xml")
