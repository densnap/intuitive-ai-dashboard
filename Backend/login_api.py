from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
#from supabase_client import supabase  # ✅ import your Supabase client
from rag import authenticate_user, current_user, process_user_query  # Import your RAG logic
from rag import UserSession 
app = FastAPI()
from supabase import create_client
from dotenv import load_dotenv
import os

# Load .env variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
print("✅ Supabase client created successfully!")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_user_session_by_username(username):
    # Normalize username: lowercase and remove dots for matching
    normalized_username = username.strip().lower().replace('.', '')
    # Fetch all users and match normalized username
    result = supabase.table("users").select("*").execute()
    if result.data and len(result.data) > 0:
        for user in result.data:
            db_username = user["username"].strip().lower().replace('.', '')
            if db_username == normalized_username:
                return UserSession(
                    user_id=user["user_id"],
                    username=user["username"],
                    role=user["role"],
                    dealer_id=user.get("dealer_id"),
                )
    print(f"[ERROR] No user found for username: {username}")
    return None
#this is for checking username and password with database
@app.post("/api/login")
async def login(request: Request):
    print("\n✅ /api/login endpoint called")

    try:
        data = await request.json()
        username = data.get("username")
        password = data.get("password")
        role = data.get("role")
        
        print(f"➡ Username: {username}")
        print(f"➡ Password: {password}")
        print(f"➡ Role: {role}")
        username = username.strip()
        password = password.strip()
        role = role.strip().lower()
        # ✅ Query the users table
        result = supabase.table("users").select("*") \
            .eq("username", username) \
            .eq("password", password) \
            .eq("role", role) \
            .execute()

        print("🔍 Supabase result:", result)

        if result.data and len(result.data) > 0:
            return {
                "success": True,
                "message": "Login successful",
                "user": result.data[0]
            }
        else:
            return {
                "success": False,
                "message": "Invalid credentials"
            }

    except Exception as e:
        print(f"❌ Error in /api/login: {str(e)}")
        return JSONResponse(status_code=500, content={
            "success": False,
            "message": "Internal server error",
            "error": str(e)
        })

# this is for dealer role based masking 
@app.post("/api/query")
async def query(request: Request):
    print("🚀 [DEBUG] /api/query endpoint hit")

    try:
        data = await request.json()
        username = data.get("username")
        user_query = data.get("query")

        print(f"👤 [DEBUG] Incoming query from user: {username}")
        print(f"💬 [DEBUG] User query: {user_query}")

        # Step 1: Get user session
        print("🔍 [DEBUG] Looking up user session...")
        user_session = get_user_session_by_username(username)

        if not user_session:
            print(f"❌ [ERROR] No matching user found for username: {username}")
            return JSONResponse(status_code=401, content={"success": False, "message": "Unauthorized"})

        print(f"✅ [DEBUG] User session retrieved: {user_session.username}, Role: {user_session.role}, Dealer ID: {user_session.dealer_id}")

        # Step 2: Set current_user globally for use in rag logic
        global current_user
        current_user = user_session

        # Step 3: Process the query
        print("🧠 [DEBUG] Passing query to process_user_query()...")
        answer = process_user_query(user_query, user_session)

        print("📤 [DEBUG] Answer received from RAG pipeline or order placement logic.")
        print(f"📝 [DEBUG] Final answer:\n{answer}")

        return {"success": True, "answer": answer}

    except Exception as e:
        print(f"🔥 [ERROR] Exception occurred in /api/query: {e}")
        return JSONResponse(status_code=500, content={"success": False, "message": str(e)})
