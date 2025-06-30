from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from supabase_client import supabase  # ✅ import your Supabase client
from rag import authenticate_user, current_user, process_user_query  # Import your RAG logic
from rag import UserSession 
app = FastAPI()

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
    data = await request.json()
    username = data.get("username")
    user_query = data.get("query")

    print(f"✅ /api/query called | Username: {username} | Query: {user_query}")

    # Look up user in your database/session by username
    user_session = get_user_session_by_username(username)  # <-- implement this function
    if not user_session:
        return JSONResponse(status_code=401, content={"success": False, "message": "Unauthorized"})

    global current_user
    current_user = user_session

    try:
        answer = process_user_query(user_query, user_session)
        return {"success": True, "answer": answer}
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "message": str(e)})