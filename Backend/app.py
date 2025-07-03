from fastapi import FastAPI, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from supabase_client import supabase
from rag import authenticate_user, current_user, process_user_query, UserSession
from twilio.twiml.messaging_response import MessagingResponse

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Utility to get user session
def get_user_session_by_username(username: str):
    normalized_username = username.strip().lower().replace('.', '')
    result = supabase.table("users").select("*").execute()
    if result.data:
        for user in result.data:
            db_username = user["username"].strip().lower().replace('.', '')
            if db_username == normalized_username:
                return UserSession(
                    user_id=user["user_id"],
                    username=user["username"],
                    role=user["role"],
                    dealer_id=user.get("dealer_id"),
                )
    return None

# ✅ Login API
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

# ✅ RAG Query API
@app.post("/api/query")
async def query(request: Request):
    try:
        data = await request.json()
        username = data.get("username")
        user_query = data.get("query")

        user_session = get_user_session_by_username(username)
        if not user_session:
            return JSONResponse(status_code=401, content={"success": False, "message": "Unauthorized"})

        global current_user
        current_user = user_session

        answer = process_user_query(user_query, user_session)
        return {"success": True, "answer": answer}

    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "message": str(e)})

# ✅ Twilio WhatsApp Webhook
@app.post("/whatsapp", response_class=PlainTextResponse)
async def whatsapp_webhook(
    Body: str = Form(...),
    From: str = Form(...)
):
    print(f"[WHATSAPP] Received message from {From}: {Body}")

    # Optional: Map From (phone) to username
    # TODO: Replace with actual phone-to-username mapping or Supabase lookup
    phone_map = {
        "whatsapp:+14155238886": "deepak.mehta",  # Sandbox number → your username
        # Add other numbers if needed
    }
    username = phone_map.get(From)

    if not username:
        response = MessagingResponse()
        response.message("❌ Your number is not linked to any user account.")
        return str(response)

    user_session = get_user_session_by_username(username)
    if not user_session:
        response = MessagingResponse()
        response.message("❌ Could not find a valid user session.")
        return str(response)

    global current_user
    current_user = user_session

    try:
        answer = process_user_query(Body, user_session)
    except Exception as e:
        print(f"[ERROR] while processing: {e}")
        answer = "⚠️ An error occurred while processing your request."

    response = MessagingResponse()
    response.message(answer)
    return str(response)
