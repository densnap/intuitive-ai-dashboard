from fastapi import FastAPI, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from Backend.supabase_client import supabase
from Backend.rag import authenticate_user, current_user, process_user_query, UserSession
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

# ✅ Utility to get user session by username

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

# ✅ Twilio WhatsApp Webhook (Deepak Mehta authenticated by default)
@app.post("/whatsapp", response_class=PlainTextResponse)
async def whatsapp_webhook(
    Body: str = Form(...),
    From: str = Form(...)
):
    print(f"[WHATSAPP] Received message from {From}: {Body}")

    # ✅ Auto-authenticate hardcoded user deepak.mehta
    try:
        result = supabase.table("users").select("*") \
            .eq("username", "deepak.mehta") \
            .eq("password", "$2b$12$QuuT0N.p3NBXSCFFdRkwAeOgjE5/4taqMEr9XqKHIhVgz58X.R.8W") \
            .execute()

        if not result.data:
            response = MessagingResponse()
            response.message("❌ Default user authentication failed.")
            return str(response)

        user = result.data[0]
        user_session = UserSession(
            user_id=user["user_id"],
            username=user["username"],
            role=user["role"],
            dealer_id=user.get("dealer_id")
        )

        global current_user
        current_user = user_session

        answer = process_user_query(Body, user_session)

    except Exception as e:
        print(f"[ERROR] while processing WhatsApp message: {e}")
        answer = "⚠️ An error occurred while processing your request."

    response = MessagingResponse()
    response.message(answer)
    return str(response)
