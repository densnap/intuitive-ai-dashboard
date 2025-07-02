import os
import re
import json
import requests
import numpy as np
import psycopg2
from supabase import create_client
from dotenv import load_dotenv
from difflib import SequenceMatcher
from fuzzywuzzy import fuzz, process
from datetime import datetime
from collections import deque
import requests
import json
import uuid



# --- Set your database credentials here or in a .env file ---
os.environ["user"] = "postgres.ojbalezgbnwunzzoajum"
os.environ["password"] = "wheelychatbot"
os.environ["host"] = "aws-0-ap-south-1.pooler.supabase.com"
os.environ["port"] = "5432"
os.environ["dbname"] = "postgres"
 
load_dotenv()
 
# --- Azure OpenAI Embedding Endpoint and Headers ---
embedding_endpoint = os.getenv("AZURE_OPENAI_URL")
embedding_headers = {
    "Content-Type": "application/json",
    "Ocp-Apim-Subscription-Key": os.getenv("AZURE_OPENAI_SUBSCRIPTION_KEY"),
    "x-service-line": os.getenv("AZURE_OPENAI_SERVICE_LINE"),
    "x-brand": os.getenv("AZURE_OPENAI_BRAND"),
    "x-project": os.getenv("AZURE_OPENAI_PROJECT"),
    'api-version': os.getenv("AZURE_OPENAI_API_VERSION")
}
 
# --- Supabase Client (for vector search) ---
supabase_url = "https://ojbalezgbnwunzzoajum.supabase.co"
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9qYmFsZXpnYm53dW56em9hanVtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk0OTk0MzMsImV4cCI6MjA2NTA3NTQzM30.20UaD3p7f1PHDCUhyEO4n3orWGqB-ku7pzBQLESXh4E"
supabase = create_client(supabase_url, supabase_key)
 
# --- Azure OpenAI Chat Endpoint and Headers ---
chat_endpoint = "https://ai-api-dev.dentsu.com/openai/deployments/GPT35Turbo/chat/completions?api-version=2024-10-21"
chat_headers  = {
    "x-service-line": "functions",
    "x-brand": "dentsu",
    "x-project": "aiassistant",
    "api-version": "v15",
    "Ocp-Apim-Subscription-Key": "3c6489668e324e6e8123e94f41456484"
}







########################################################################
#########################  USER SESSION ################################
current_user = None
current_session_id = None 
 
class UserSession:
    def __init__(self, user_id, username, role, dealer_id=None, dealer_name=None):
        self.user_id = user_id
        self.username = username
        self.role = role.lower()
        self.dealer_id = dealer_id
        self.dealer_name = dealer_name
        self.is_authenticated = True
    
    def is_dealer(self):
        return self.role == 'dealer'
    
    def is_sales_rep(self):
        """Check if user is a sales representative"""
        return self.role.lower() in ['sales_rep', 'sales', 'representative', 'sales_representative']
    
    def is_admin(self):
        return self.role in ['admin', 'superuser', 'manager']
    
    def can_access_all_data(self):
        return self.is_admin()
    
    def get_dealer_filter(self):
        """Returns dealer_id for filtering if user is a dealer"""
        return self.dealer_id if self.is_dealer() else None
 
def authenticate_user(username, password):
    """
    Authenticate user and return UserSession object
    """
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("dbname"),
            user=os.getenv("user"),
            password=os.getenv("password"),
            host=os.getenv("host"),
            port=os.getenv("port")
        )
        cur = conn.cursor()
        
        # Get user details with dealer info
        query = """
        SELECT u.user_id, u.username, u.role, u.dealer_id, d.name as dealer_name
        FROM users u
        LEFT JOIN dealer d ON u.dealer_id = d.dealer_id
        WHERE u.username = %s AND u.password = %s
        """
        cur.execute(query, (username, password))
        result = cur.fetchone()
        
        cur.close()
        conn.close()
        
        if result:
            user_id, username, role, dealer_id, dealer_name = result
            return UserSession(user_id, username, role, dealer_id, dealer_name)
        else:
            return None
            
    except Exception as e:
        print(f"Authentication error: {e}")
        return None
 
def login():
    """
    Handle user login
    """
    global current_user
 
    print("=== LOGIN REQUIRED ===")
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    
    user_session = authenticate_user(username, password)
    
    if user_session:
        current_user = user_session
        print(f"Welcome {user_session.username}!")
        print(f"Role: {user_session.role}")
        if user_session.dealer_name:
            print(f"Dealer: {user_session.dealer_name}")
        print("-" * 50)
        return True
    else:
        print("Invalid credentials. Please try again.")
        return False
 
#def logout():
    """
    Handle user logout
    """
    #global current_user
    if current_user:
        print(f"Goodbye {current_user.username}!")
        current_user = None
 
def logout():
    global current_user, current_session_id
    current_user = None
    current_session_id = None  # ✅ Clear session ID on logout
    print("User logged out.")
def check_authentication():
    """
    Check if user is authenticated
    """
    return current_user is not None and current_user.is_authenticated
 
#############################################################################
########################  CONVERSATION LOGS ################################






def get_conversation_context(num_exchanges=5):
    try:
        result = supabase.table("conversation_logs") \
            .select("user_query, ai_response") \
            .eq("user_id", current_user.user_id) \
            .order("query_timestamp", desc=True) \
            .limit(num_exchanges) \
            .execute()
 
        rows = result.data if hasattr(result, 'data') else result.get('data', [])
        if not rows:
            return ""
 
        context = f"Last {num_exchanges} conversations from this user:\n"
        for i, row in enumerate(reversed(rows), 1):
            context += f"\nExchange {i}:\nUser: {row['user_query']}\nAssistant: {row['ai_response']}\n"
        return context
 
    except Exception as e:
        print("DEBUG: Failed to fetch context from Supabase:", e)
        return ""
 
def is_follow_up_question(user_query):
    follow_up_signals = [
        'what about', 'and what', 'also show', 'more details', 'can you also',
        'tell me more', 'how about', 'compare', 'difference between'
    ]
    return any(signal in user_query.lower() for signal in follow_up_signals)
 
def enhance_query_with_context(user_query):
    if not is_follow_up_question(user_query):
        return user_query
 
    try:
        result = supabase.table("conversation_logs") \
            .select("user_query, ai_response") \
            .eq("user_id", current_user.user_id) \
            .order("query_timestamp", desc=True) \
            .limit(1) \
            .execute()
 
        rows = result.data if hasattr(result, 'data') else result.get('data', [])
        if not rows:
            return user_query
 
        last = rows[0]
        return (
            f"Previous context: {last['user_query']}\n"
            f"Previous response: {last['ai_response']}\n\n"
            f"Follow-up question: {user_query}\n\n"
            f"Please answer the follow-up considering the previous context."
        )
 
    except Exception as e:
        print("DEBUG: Failed to enhance query with context:", e)
        return user_query
 
def save_to_supabase(user_query, response):
    try:
        log_data = {
            'user_id': current_user.user_id,
            'dealer_id': current_user.dealer_id,
            'user_query': user_query,
            'ai_response': response,
            'session_id': current_session_id,
            'query_timestamp': datetime.now().isoformat(),
            'query_type': "followup" if is_follow_up_question(user_query) else "initial",
            'metadata': {}  # Add any relevant metadata if needed
        }
        result = supabase.table("conversation_logs").insert(log_data).execute()
        print(f"DEBUG: Supabase log result: {result}")
    except Exception as e:
        print(f"Error saving to Supabase: {e}")
 
#############################################################################
########################  FUZZY  ################################
DEALER_CACHE = {}
PRODUCT_CACHE = {}
WAREHOUSE_CACHE = {}
 
def normalize_text(text):
    """Normalize text for better matching"""
    if not isinstance(text, str):
        text = str(text)
    text = re.sub(r'[^\w\s]', '', text.lower())
    text = re.sub(r'\s+', ' ', text).strip()
    return text
 
def fuzzy_match_string(query_string, candidates, threshold=70):
    """
    Find the best fuzzy match for a string from a list of candidates
    Returns (best_match, score) or (None, 0) if no good match found
    """
    if not query_string or not candidates:
        return None, 0
    
    query_normalized = normalize_text(query_string)
    candidates_normalized = [normalize_text(c) for c in candidates]
    
    try:
        result = process.extractOne(query_normalized, candidates_normalized, scorer=fuzz.ratio)
        if result and result[1] >= threshold:
            original_index = candidates_normalized.index(result[0])
            return candidates[original_index], result[1]
    except:
        pass
    
    return None, 0
 
def get_database_entities():
    """Cache database entities for fuzzy matching"""
    global DEALER_CACHE, PRODUCT_CACHE, WAREHOUSE_CACHE
    
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("dbname"),
            user=os.getenv("user"),
            password=os.getenv("password"),
            host=os.getenv("host"),
            port=os.getenv("port")
        )
        cur = conn.cursor()
        
        # Get dealers
        cur.execute("SELECT DISTINCT name FROM dealer WHERE name IS NOT NULL")
        dealers = [row[0] for row in cur.fetchall()]
        DEALER_CACHE = {normalize_text(d): d for d in dealers}
        
        # Get products
        cur.execute("SELECT DISTINCT product_id FROM product WHERE product_id IS NOT NULL")
        products = [row[0] for row in cur.fetchall()]
        PRODUCT_CACHE = {normalize_text(p): p for p in products}
        
        # Get warehouses
        cur.execute("SELECT DISTINCT location FROM warehouse WHERE location IS NOT NULL")
        warehouses = [row[0] for row in cur.fetchall()]
        WAREHOUSE_CACHE = {normalize_text(w): w for w in warehouses}
        
        cur.close()
        conn.close()
        
        print(f"DEBUG: Cached {len(dealers)} dealers, {len(products)} products, {len(warehouses)} warehouses")
        
    except Exception as e:
        print(f"DEBUG: Error caching entities: {e}")
 
def fuzzy_correct_entities(text):
    """
    Find and correct entity names in the text using fuzzy matching
    """
    corrected_text = text
    corrections_made = []
    
    # Check for dealer names
    for cached_dealer in DEALER_CACHE.values():
        words_in_dealer = cached_dealer.lower().split()
        for word in words_in_dealer:
            if len(word) > 3:
                text_words = text.lower().split()
                for text_word in text_words:
                    similarity = fuzz.ratio(word, text_word)
                    if similarity >= 75 and word != text_word:
                        pattern = re.compile(re.escape(text_word), re.IGNORECASE)
                        corrected_text = pattern.sub(word, corrected_text)
                        corrections_made.append(f"{text_word} -> {word}")
    
    # Check for product IDs
    for cached_product in PRODUCT_CACHE.values():
        if cached_product.lower() in text.lower():
            continue
        similarity = fuzz.ratio(normalize_text(cached_product), normalize_text(text))
        if similarity >= 80:
            corrected_text = corrected_text.replace(text, cached_product)
            corrections_made.append(f"Product: {text} -> {cached_product}")
    
    # Check for warehouse locations
    for cached_warehouse in WAREHOUSE_CACHE.values():
        similarity = fuzz.ratio(normalize_text(cached_warehouse), normalize_text(text))
        if similarity >= 80:
            pattern = re.compile(re.escape(text), re.IGNORECASE)
            corrected_text = pattern.sub(cached_warehouse, corrected_text)
            corrections_made.append(f"Warehouse: {text} -> {cached_warehouse}")
    
    if corrections_made:
        print(f"DEBUG: Fuzzy corrections made: {corrections_made}")
    
    return corrected_text
########################################################################################
#####################################  SQLL  ################################################
 
# def add_role_based_filters(base_query: str, user_session) -> str:
#     if not user_session or user_session.can_access_all_data() or user_session.is_sales_rep():
#         return base_query
 
#     dealer_id = user_session.dealer_id
#     query_lower = base_query.lower()
 
#     # Apply warehouse restriction for inventory queries (only for dealers)
#     if 'from inventory' in query_lower or 'join inventory' in query_lower:
#         if 'where' in query_lower:
#             return base_query.replace(
#                 ' where ',
#                 f" WHERE i.warehouse_id IN (SELECT warehouse_id FROM dealer WHERE dealer_id = {dealer_id}) AND "
#             )
#         else:
#             return base_query.rstrip(';') + f" WHERE i.warehouse_id IN (SELECT warehouse_id FROM dealer WHERE dealer_id = {dealer_id});"
 
#     return base_query



def get_llm_sql(user_query):
    """Generate SQL with correct role-based access control logic + recent history"""
    corrected_query = fuzzy_correct_entities(user_query)
 
    # Fetch last 3 user logs for context
    try:
        result = supabase.table("conversation_logs") \
            .select("user_query, ai_response") \
            .eq("user_id", current_user.user_id) \
            .order("query_timestamp", desc=True) \
            .limit(3) \
            .execute()
 
        rows = result.data if hasattr(result, 'data') else result.get('data', [])
        history_context = ""
        for i, row in enumerate(reversed(rows), 1):
            history_context += f"\nExchange {i}:\nUser: {row['user_query']}\nAssistant: {row['ai_response']}\n"
    except Exception as e:
        print("DEBUG: Failed to fetch history logs for SQL context:", e)
        history_context = ""
 
    # Inject role-specific access control info
    role_info = ""
    if current_user:
        if current_user.is_dealer():
            role_info = f"""
IMPORTANT ROLE-BASED ACCESS CONTROL:
- The current user is a DEALER with dealer_id = {current_user.dealer_id}
- Dealers can access:
  * All inventory/stock data (no dealer filter needed)
  * ONLY their own sales data → Filter sales queries with: AND s.dealer_id = {current_user.dealer_id}
  * ONLY their own claims data → Filter claims queries with: AND c.dealer_id = {current_user.dealer_id}
- NEVER allow access to other dealer_id data.
"""
        elif current_user.is_sales_rep():
            role_info = """
IMPORTANT ROLE-BASED ACCESS CONTROL:
- The current user is a SALES REPRESENTATIVE
- Sales reps can access:
  * All inventory data (no dealer filter)
  * Their own orders (orders table)
- DO NOT restrict queries to a specific dealer unless explicitly mentioned by user.
"""
        elif current_user.is_admin():
            role_info = """
IMPORTANT ROLE-BASED ACCESS CONTROL:
- The current user is an ADMIN
- Admins have full unrestricted access to all data across all dealers and tables.
"""
 
    system_prompt = (
        "You are an AI assistant for a tyre manufacturing company. "
        "You help generate efficient SQL SELECT queries from user questions based on the following PostgreSQL schema.\n\n"
        "Tables and their descriptions:\n"
        "1. users(user_id, username, password, email, role, dealer_id): User login info\n"
        "2. dealer(dealer_id, name): Tyre dealers\n"
        "3. claim(claim_id, dealer_id, status , claim_date , resolved_date,product_id,amount , approved_amount, reason)\n"
        "4. product(product_id, product_name, category, price, section_width, aspect_ratio, construction_type, rim_diameter_inch)\n"
        "5. warehouse(warehouse_id, location, zone)\n"
        "6. sales(sales_id, dealer_id, product_id, warehouse_id, quantity, cost, date)\n"
        "7. inventory(product_id, warehouse_id, quantity)\n"
        "8. orders(order_id, dealer_id, product_id, warehouse_id, quantity, unit_price, total_cost, order_date, status, sales_rep_id)\n\n"
        "Key relationships:\n"
        "- users joins dealer on dealer_id\n"
        "- claim joins dealer on dealer_id\n"
        "- sales joins dealer, product, and warehouse\n"
        "- inventory joins product and warehouse\n\n"
        + role_info +
        "\nDO NOT create SQL queries if user asks for other dealer_id data (when user is a dealer).\n"
        "\nRules for Generating SQL:\n"
        "1. Use ONLY the columns and tables exactly as defined above.\n"
        "2. For string comparisons, use ILIKE with wildcards: name ILIKE '%term%'\n"
        "3. Use LOWER() for case-insensitive match\n"
        "4. Try matching multiple variants (spelling/case)\n"
        "5. Return only the columns needed to answer\n"
        "6. Use aliases (s = sales, c = claim, etc.)\n"
        "7. ENFORCE access control strictly\n\n"
        "Here is the user’s recent context to help understand their intent:\n"
        + history_context
    )
 
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": corrected_query}
    ]
 
    payload = {
        "messages": messages,
        "temperature": 0,
        "max_tokens": 250,
        "top_p": 1,
        "frequency_penalty": 0,
        "presence_penalty": 0
    }
 
    response = requests.post(chat_endpoint, headers=chat_headers, json=payload)
    if response.status_code == 200:
        sql = response.json()["choices"][0]["message"]["content"].strip()
 
        # Final safety pass
        # if current_user:
        #     sql = add_role_based_filters(sql, current_user)
 
        return sql
    else:
        raise Exception(f"Chat API error (SQL): {response.status_code}: {response.text}")




def clean_sql_output(raw_sql):
    # Remove markdown code fences and leading/trailing spaces
    cleaned = re.sub(r"```(?:sql)?", "", raw_sql, flags=re.IGNORECASE).strip()
    return cleaned
 
def try_select_sql(sql):
    sql = sql.strip()
    if not sql.lower().startswith("select"):
        return None, "Only SELECT statements are allowed for safety."
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("dbname"),
            user=os.getenv("user"),
            password=os.getenv("password"),
            host=os.getenv("host"),
            port=os.getenv("port")
        )
        cur = conn.cursor()
        cur.execute(sql)
        columns = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        result = [dict(zip(columns, row)) for row in rows]
        cur.close()
        conn.close()
        return result, None
    except Exception as e:
        return None, str(e)
    
 
def sql_result_to_context(sql_result):
    if not sql_result:
        return "No results found."
    rows_as_strings = []
    for row in sql_result:
        row_str = ', '.join(f"{k}: {v}" for k, v in row.items())
        rows_as_strings.append(row_str)
    return "\n---\n".join(rows_as_strings)
 
    
 
############################################################################################
###################### RAG ############################################################
 
def rewrite_query_for_rag(user_query):
    """
    Enhanced query rewriting with fuzzy correction
    """
    corrected_query = fuzzy_correct_entities(user_query)
    
    system_prompt = (
        "You are an expert at rewriting queries for better vector similarity search in a tyre manufacturing context. "
        "Your task is to rewrite user queries to make them more neutral, comprehensive, and suitable for semantic search. "
        "\n\nGuidelines for rewriting:\n"
        "1. Remove conversational elements (please, can you, I want to know, etc.)\n"
        "2. Expand abbreviations and acronyms related to tyres (e.g., 'R' to 'radial')\n"
        "3. Add relevant synonyms and related terms\n"
        "4. Convert questions to declarative statements focusing on key concepts\n"
        "5. Include industry-specific terminology where appropriate\n"
        "6. Maintain all specific identifiers (IDs, part numbers, names)\n"
        "7. Focus on the core information need\n"
        "8. Include variations and synonyms for names and products to handle typos\n"
        "\nOnly return the rewritten query, nothing else."
    )
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": corrected_query}
    ]
    
    payload = {
        "messages": messages,
        "temperature": 0.1,
        "max_tokens": 150,
        "top_p": 0.9,
        "frequency_penalty": 0,
        "presence_penalty": 0
    }
    
    try:
        response = requests.post(chat_endpoint, headers=chat_headers, json=payload)
        if response.status_code == 200:
            rewritten_query = response.json()["choices"][0]["message"]["content"].strip()
            print(f"DEBUG: Original query: {user_query}")
            print(f"DEBUG: Corrected query: {corrected_query}")
            print(f"DEBUG: Rewritten query: {rewritten_query}")
            return rewritten_query
        else:
            print(f"Query rewriting failed: {response.status_code}: {response.text}")
            return corrected_query
    except Exception as e:
        print(f"Query rewriting error: {e}")
        return corrected_query
 
def preprocess_query(query):
    text = query.lower()
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text
 
def get_embedding(text):
    payload = {"input": text}
    response = requests.post(embedding_endpoint, headers=embedding_headers, json=payload)
    if response.status_code == 200:
        return response.json()["data"][0]["embedding"]
    else:
        raise Exception(f"Embedding API error {response.status_code}: {response.text}")
 
def cosine_similarity(vec1, vec2):
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    if np.linalg.norm(vec1) == 0 or np.linalg.norm(vec2) == 0:
        return 0.0
    return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))
 
def extract_metadata_with_llm(user_query):
    """
    Enhanced metadata extraction with role-based context
    """
    corrected_query = fuzzy_correct_entities(user_query)
    
    # Add current user context to metadata extraction
    user_context = ""
    if current_user and current_user.is_dealer():
        user_context = f" The current user is dealer {current_user.dealer_name} with dealer_id {current_user.dealer_id}."
    
    system_prompt = (
        "You are an assistant that extracts structured metadata from user queries about tyres, warehouses, dealers, claims, sales, and inventory. "
        "Given a user query, return a JSON object with as many of these fields as possible if present: "
        " user_id, username, email, role, dealer_id, dealer_name,claim_id, status, claim_date, product_id(number ,symbol , alphabets eg. 100/35R24 50P), amount, approved_amount, resolved_date, reason,sales_id, date, product_name(only text eg. SpeedoCruze Pro), warehouse_id(number),zone,quantity(number), cost, product_price, category, location"
        "Be flexible with variations and partial matches in names and locations. "
        + user_context +
        " If a field is not present, omit it. Only return a valid JSON object, no explanation or extra text."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": corrected_query}
    ]
    payload = {
        "messages": messages,
        "temperature": 0,
        "max_tokens": 200,
        "top_p": 1,
        "frequency_penalty": 0,
        "presence_penalty": 0
    }
    response = requests.post(chat_endpoint, headers=chat_headers, json=payload)
    if response.status_code == 200:
        content = response.json()["choices"][0]["message"]["content"]
        try:
            metadata = json.loads(content)
            if isinstance(metadata, dict):
                return metadata
        except Exception as e:
            print("DEBUG: Metadata JSON decode error:", e)
            return None
    return None
 
def enhanced_metadata_filter_matching(metadata_filter, row_metadata):
    """
    Enhanced metadata matching with fuzzy logic and role-based filtering
    """
    if not metadata_filter or not row_metadata:
        return 0
    
    # Add role-based filtering to metadata
    if current_user and current_user.is_dealer():
        # Check if metadata contains dealer-specific information
        if 'dealer_id' in row_metadata:
            if str(row_metadata['dealer_id']) != str(current_user.dealer_id):
                # If this is sales or claims data from another dealer, exclude it
                if any(key in row_metadata for key in ['sales_id', 'claim_id']):
                    return 0
    
    match_score = 0
    total_filters = len(metadata_filter)
    
    for key, filter_value in metadata_filter.items():
        row_value = row_metadata.get(key, "")
        
        if not filter_value or not row_value:
            continue
            
        # Exact match
        if str(filter_value).lower() == str(row_value).lower():
            match_score += 1
        # Fuzzy match for strings
        elif isinstance(filter_value, str) and isinstance(row_value, str):
            similarity = fuzz.ratio(filter_value.lower(), row_value.lower())
            if similarity >= 70:
                match_score += similarity / 100
        # Partial match
        elif str(filter_value).lower() in str(row_value).lower() or str(row_value).lower() in str(filter_value).lower():
            match_score += 0.7
    
    return match_score / total_filters if total_filters > 0 else 0
 
def vector_store_similarity_search(query_embedding, top_k=10, metadata_filter=None, similarity_threshold=0.1):
    """
    Enhanced vector similarity search with role-based access control
    """
    response = supabase.table("vector_store").select("*").execute()
    rows = response.data
    if not rows:
        return []
    
    # Enhanced metadata filtering with role-based access control
    if metadata_filter:
        scored_rows = []
        for row in rows:
            try:
                meta = row.get("metadata")
                if isinstance(meta, str):
                    meta = json.loads(meta)
                
                match_score = enhanced_metadata_filter_matching(metadata_filter, meta)
                if match_score > 0:
                    scored_rows.append((match_score, row))
            except Exception:
                continue
        
        scored_rows.sort(reverse=True, key=lambda x: x[0])
        if scored_rows:
            rows = [row for score, row in scored_rows if score >= 0.3]
        else:
            rows = []
    
    # Vector similarity with threshold filtering
    similarities = []
    for row in rows:
        try:
            row_embedding = json.loads(row["embedding"])
            sim = cosine_similarity(query_embedding, row_embedding)
            if sim >= similarity_threshold:
                similarities.append((sim, row))
        except Exception:
            continue
    
    similarities.sort(reverse=True, key=lambda x: x[0])
    results = [row for sim, row in similarities[:top_k]]
    
    if similarities:
        print(f"DEBUG: Found {len(similarities)} results above threshold {similarity_threshold}")
        print(f"DEBUG: Top similarity scores: {[round(sim, 3) for sim, _ in similarities[:5]]}")
    
    return results
 
# def rows_to_context(rows):
#     context = ""
#     for idx, row in enumerate(rows, 1):
#         context += f"\nRow {idx}:\n"
#         for key, value in row.items():
#             if key != "embedding":
#                 context += f"{key}: {value}\n"
#     return context.strip()
 
def vector_rows_to_context(rows):
    context = ""
    for idx, row in enumerate(rows, 1):
        context += f"\nVector Row {idx}:\n"
        for key, value in row.items():
            if key != "embedding":
                context += f"{key}: {value}\n"
    return context.strip()
 
###########################################################################################
####################### FINAL RESPONSE #####################################################
 
def get_llm_final_response(sql_context, rag_context, user_query):
    # Detect if this is a follow-up and enhance query
    enhanced_query = enhance_query_with_context(user_query)
    history_context = get_conversation_context(2)
 
    # Build user context string for system prompt
    user_context = ""
    if current_user:
        user_context = (
            f"User Info:\n"
            f"- Username: {current_user.username}\n"
            f"- Role: {current_user.role}\n"
            
        )
        if current_user.is_dealer():
            user_context += (
                f"- Dealer Name: {current_user.dealer_name}\n\n"
                f"- Dealer ID: {current_user.dealer_id}\n"
                "ACCESS RESTRICTIONS:\n"
                "- The user is a DEALER.\n"
                "- They are only allowed to view data belonging to their own dealer_id.\n"
                "- NEVER reveal or refer to sales, orders, claims, or inventory from other dealers.\n"
                "- If RAG or SQL context includes other-dealer data, IGNORE or exclude it.\n"
                "- Dealers are not allowed to place orders through this assistant.\n"
            )
        elif current_user.is_sales_rep():
            user_context += (
                "\nACCESS RESTRICTIONS:\n"
                "- The user is a SALES REPRESENTATIVE.\n"
                "- They can view all product and inventory data.\n"
                "- They can view and manage orders that they have placed (via sales_rep_id).\n"
                "- If the query is about a dealer, respond accordingly using dealer_id mentioned.\n"
                "- Do not restrict access unless the query is about private dealer-specific sales or claims.\n"
            )
        elif current_user.is_admin():
            user_context += (
                "\nACCESS RESTRICTIONS:\n"
                "- The user is an ADMIN.\n"
                "- Admins have full access to ALL data, across ALL dealers and all tables.\n"
                "- Do not apply any restrictions or filters.\n"
            )
 
    # System behavior and role enforcement
    system_prompt = (
        "You are an AI assistant named 'shivam' for the tyre manufacturing industry.\n"
        "You combine results from SQL databases and RAG-based retrieval (vector search).\n"
        "be a human like assistant and respond politely and use natural language \n"
        "NEVER fabricate or guess missing information.\n"
         "If asked about similar products provide information from the context provided of muliple other products '\n"
        "STRICTLY ENFORCE user access:\n"
        "- If the user is a dealer, he cannot place order and never mention sales or claims from other dealers.\n"
        "- Only show data for the logged-in user's dealer_id.\n"
        #"Respond directly. Do not explain your process.\n"
        #"If relevant context is missing, say: 'Sorry, I can't assist with that.'\n"
        "always Consider SQL response as the correct and relevant context and also RAGs context to it if its relevant '\n"
       + user_context
    )
 
    # User prompt with merged context and follow-up trace
    user_message = f"""
{history_context}
 
SQL Context:
{sql_context}
 
RAG Context:
{rag_context}
 
User Query:
{enhanced_query}
"""
 
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message.strip()}
    ]
 
    payload = {
        "messages": messages,
        "temperature": 0.0,
        "max_tokens": 300,
        "top_p": 1,
        "frequency_penalty": 0,
        "presence_penalty": 0
    }
 
    try:
        response = requests.post(chat_endpoint, headers=chat_headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print("DEBUG: Chat API failed:", e)
        return "Sorry, I can't assist with that."
 
###################################################################################################
##############################  ORDERS ############################################################
 
def place_order(dealer_id, product_id, quantity, warehouse_id=None):
    """
    Place an order - only for sales representatives.
    Deducts stock from warehouse and records the order.
    """
    if not current_user or not current_user.is_sales_rep():
        return {"success": False, "message": "Only sales representatives can place orders."}
    
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("dbname"),
            user=os.getenv("user"),
            password=os.getenv("password"),
            host=os.getenv("host"),
            port=os.getenv("port")
        )
        cur = conn.cursor()
 
        # 1. Validate product
        cur.execute("SELECT product_name, price FROM product WHERE product_id = %s", (product_id,))
        product_row = cur.fetchone()
        if not product_row:
            return {"success": False, "message": f"Product {product_id} not found."}
        
        product_name, unit_price = product_row
 
        # 2. Validate dealer
        cur.execute("SELECT name FROM dealer WHERE dealer_id = %s", (dealer_id,))
        dealer_row = cur.fetchone()
        if not dealer_row:
            return {"success": False, "message": f"Dealer ID {dealer_id} not found."}
        
        dealer_name = dealer_row[0]
 
        # 3. Check inventory
        if warehouse_id:
            cur.execute("""
                SELECT w.warehouse_id, w.location, i.quantity
                FROM inventory i
                JOIN warehouse w ON i.warehouse_id = w.warehouse_id
                WHERE i.product_id = %s AND i.warehouse_id = %s AND i.quantity >= %s
            """, (product_id, warehouse_id, quantity))
        else:
            cur.execute("""
                SELECT w.warehouse_id, w.location, i.quantity
                FROM inventory i
                JOIN warehouse w ON i.warehouse_id = w.warehouse_id
                WHERE i.product_id = %s AND i.quantity >= %s
                ORDER BY i.quantity DESC
                LIMIT 1
            """, (product_id, quantity))
        
        stock_row = cur.fetchone()
        if not stock_row:
            return {"success": False, "message": f"Insufficient stock for product {product_id}. Required: {quantity}"}
 
        selected_warehouse_id, warehouse_location, available_quantity = stock_row
 
        total_cost = unit_price * quantity
 
        # 4. Start transaction
        cur.execute("BEGIN")
 
        # 5. Insert order into orders table
        cur.execute("""
            INSERT INTO orders (
                dealer_id, product_id, warehouse_id, quantity,
                unit_price, total_cost, order_date, sales_rep_id
            )
            VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, %s)
            RETURNING order_id
        """, (
            dealer_id, product_id, selected_warehouse_id,
            quantity, unit_price, total_cost, current_user.user_id
        ))
        order_id = cur.fetchone()[0]
 
        # 6. Deduct stock
        cur.execute("""
            UPDATE inventory
            SET quantity = quantity - %s
            WHERE product_id = %s AND warehouse_id = %s
        """, (quantity, product_id, selected_warehouse_id))
 
        # 7. Commit
        conn.commit()
 
        return {
            "success": True,
            "message": "Order placed successfully.",
            "details": {
                "order_id": order_id,
                "dealer": dealer_name,
                "product": f"{product_name} ({product_id})",
                "quantity": quantity,
                "warehouse": f"{warehouse_location} (ID: {selected_warehouse_id})",
                "unit_price": float(unit_price),
                "total_cost": float(total_cost),
                "remaining_stock": available_quantity - quantity
            }
        }
 
    except Exception as e:
        if conn:
            conn.rollback()
        return {"success": False, "message": f"Transaction failed: {str(e)}"}
 
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
 
def check_stock_availability(product_id, required_quantity=1):
    """
    Check stock availability across all warehouses
    """
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("dbname"),
            user=os.getenv("user"),
            password=os.getenv("password"),
            host=os.getenv("host"),
            port=os.getenv("port")
        )
        cur = conn.cursor()
        
        cur.execute("""
            SELECT w.warehouse_id, w.location, w.zone, i.quantity,
                   p.product_name, p.price
            FROM inventory i
            JOIN warehouse w ON i.warehouse_id = w.warehouse_id
            JOIN product p ON i.product_id = p.product_id
            WHERE i.product_id = %s AND i.quantity > 0
            ORDER BY i.quantity DESC
        """, (product_id,))
        
        results = cur.fetchall()
        cur.close()
        conn.close()
        
        if not results:
            return {"available": False, "message": f"Product {product_id} not found or out of stock"}
        
        stock_info = []
        total_stock = 0
        
        for row in results:
            warehouse_id, location, zone, quantity, product_name, price = row
            stock_info.append({
                "warehouse_id": warehouse_id,
                "location": location,
                "zone": zone,
                "quantity": quantity,
                "sufficient": quantity >= required_quantity
            })
            total_stock += quantity
        
        return {
            "available": total_stock >= required_quantity,
            "product_name": results[0][4],
            "price": float(results[0][5]),
            "total_stock": total_stock,
            "required_quantity": required_quantity,
            "warehouses": stock_info
        }
        
    except Exception as e:
        return {"available": False, "message": f"Error checking stock: {str(e)}"}



def extract_order_details(user_query):
    """
    Extract order intent and details using LLM.
    Supports fallback to dealer_name and product_name for fuzzy resolution.
 
    Returns a JSON object like:
    {
        "intent": "order" or "info",
        "dealer_id": ...,
        "dealer_name": ...,
        "product_id": ...,
        "product_name": ...,
        "quantity": ...,
        "warehouse_id": ...
    }
    """
    system_prompt = """
You are an AI assistant extracting structured order information from user input.
Always return a valid JSON object with the following keys:
 
- intent: "order" or "info"
- product_id: (exact SKU if given)
- product_name: (if no product_id, extract name like "SpeedoCruze")
- dealer_id: (numeric ID if given)
- dealer_name: (if no dealer_id, extract name like "Pooja Singh")
- quantity: number of units (if mentioned)
- warehouse_id: optional (if present)
 
Rules:
- Use product_name and dealer_name as fallback when product_id or dealer_id are missing.
- If the user is only asking about availability or product info, use intent: "info".
- Do not include extra text outside the JSON.
 
Examples:
 
"Order 50 units of 100/35R24 for dealer 123" ->
{"intent": "order", "dealer_id": 123, "product_id": "100/35R24", "quantity": 50}
 
"Check if 100/35R24 is in stock" ->
{"intent": "info", "product_id": "100/35R24"}
 
"Place 3 SpeedoCruze for Pooja Singh" ->
{"intent": "order", "product_name": "SpeedoCruze", "dealer_name": "Pooja Singh", "quantity": 3}
 
"Need 20 SpeedoCruze tires" ->
{"intent": "order", "product_name": "SpeedoCruze", "quantity": 20}
"""
 
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query}
    ]
 
    payload = {
        "messages": messages,
        "temperature": 0,
        "max_tokens": 200,
        "top_p": 1
    }
 
    try:
        response = requests.post(chat_endpoint, headers=chat_headers, json=payload)
        if response.status_code == 200:
            content = response.json()["choices"][0]["message"]["content"]
            return json.loads(content)
    except Exception as e:
        print(f"Error extracting order details: {e}")
    
    return {"intent": "unknown"}
 
def resolve_dealer_id(dealer_name):
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("dbname"),
            user=os.getenv("user"),
            password=os.getenv("password"),
            host=os.getenv("host"),
            port=os.getenv("port")
        )
        cur = conn.cursor()
        cur.execute("""
            SELECT dealer_id FROM dealer
            WHERE LOWER(name) ILIKE %s
            LIMIT 1
        """, (f"%{dealer_name.lower()}%",))
        result = cur.fetchone()
        return result[0] if result else None
    except Exception as e:
        print("DEBUG resolve_dealer_id error:", e)
        return None
    finally:
        cur.close()
        conn.close()
 
def resolve_product_id(product_name):
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("dbname"),
            user=os.getenv("user"),
            password=os.getenv("password"),
            host=os.getenv("host"),
            port=os.getenv("port")
        )
        cur = conn.cursor()
        cur.execute("""
            SELECT product_id FROM product
            WHERE LOWER(product_name) ILIKE %s
            LIMIT 1
        """, (f"%{product_name.lower()}%",))
        result = cur.fetchone()
        return result[0] if result else None
    except Exception as e:
        print("DEBUG resolve_product_id error:", e)
        return None
    finally:
        cur.close()
        conn.close()





#####################################################################################################################
####################### MAIN ########################################################################
 
def main():
    print("🔐 Enhanced RAG System with Role-Based Access Control")
    print("Features: Fuzzy Matching + Dealer Access Control + Supabase Logging")
    print("=" * 60)
 
    while not check_authentication():
        if not login():
            retry = input("Try again? (y/n): ").lower()
            if retry != 'y':
                print("Goodbye!")
                return
 
    global current_session_id
    current_session_id = str(uuid.uuid4())
    print(f"DEBUG: New session started. session_id = {current_session_id}")
 
    print("Initializing entity cache...")
    get_database_entities()
 
    print(f"\nWelcome, {current_user.username}!")
    if current_user.is_dealer():
        print("🏪 Dealer Access: Sales/Claims limited to your dealership")
    elif current_user.is_admin():
        print("🔑 Admin Access: Full data access")
 
    print("\nCommands:")
    print("- Type your query to search")
    print("- Type 'logout' to switch users")
    print("- Type 'exit' to quit")
    print("-" * 60)
 
    while True:
        user_query = input(f"{current_user.username} > ").strip()
 
        if user_query.lower() == "exit":
            break
        elif user_query.lower() == "logout":
            logout()
            main()
            return
        elif not user_query:
            continue
 
        try:
            # 🛒 Sales Rep: Determine intent
            if current_user.is_sales_rep():
                extracted = extract_order_details(user_query)
                intent = extracted.get("intent", "unknown")
 
                if intent == "order":
                    product_id = extracted.get("product_id")
                    dealer_id = extracted.get("dealer_id")
                    quantity = extracted.get("quantity")
                    warehouse_id = extracted.get("warehouse_id")
 
                    # If dealer_id missing but dealer_name is present
                    if not dealer_id and "dealer_name" in extracted:
                        dealer_id = resolve_dealer_id(extracted["dealer_name"])
                    
                    # If product_id missing but product_name is present
                    if not product_id and "product_name" in extracted:
                        product_id = resolve_product_id(extracted["product_name"])
 
                    if not product_id or not quantity or not dealer_id:
                        response = "❌ Missing order details. Please specify dealer, product, and quantity."
                    else:
                        response_obj = place_order(dealer_id, product_id, quantity, warehouse_id)
                        response = f"✅ {response_obj['message']}" if response_obj["success"] else f"❌ {response_obj['message']}"
 
                    print(f"shivam : {response}")
                    
                    save_to_supabase(user_query, response)
                    continue
 
                elif intent == "info":
                    # Fall through to SQL + RAG section below
                    pass
                else:
                    response = "❌ Could not understand your intent. Please try rephrasing."
                    print(f"shivam : {response}")
                    
                    save_to_supabase(user_query, response)
                    continue
 
            # 🧠 SQL + RAG for Dealer, Admin, or Sales Rep with info intent
            if current_user.is_dealer() or current_user.is_admin() or current_user.is_sales_rep():
                # SQL
                sql = get_llm_sql(user_query)
                sql = clean_sql_output(sql)
                print("DEBUG: SQL:", sql)
                sql_context = "No results found."
                if sql.strip().upper() != "NO_SQL" and sql.strip().lower().startswith("select"):
                    sql_result, sql_error = try_select_sql(sql)
                    if sql_result:
                        sql_context = sql_result_to_context(sql_result)
                        print("SQL Result:", sql_context)
                        print("=" * 50)
 
                # RAG
                rewritten_query = rewrite_query_for_rag(user_query)
                query_embedding = get_embedding(preprocess_query(rewritten_query))
                metadata_filter = extract_metadata_with_llm(user_query)
 
                vector_rows = vector_store_similarity_search(
                    query_embedding,
                    top_k=10,
                    metadata_filter=metadata_filter,
                    similarity_threshold=0.08
                )
 
                rag_context = vector_rows_to_context(vector_rows) if vector_rows else "No relevant vector context found."
                if vector_rows:
                    print("RAG Vector Search Result:")
                    print(rag_context)
                else:
                    print("RAG Vector Search: No relevant results found.")
 
                # Final Response
                print("=" * 50)
                print("Final Response Generation")
                print("=" * 50)
                answer = get_llm_final_response(sql_context, rag_context, user_query)
                print(f"shivam : {answer}")
 
                
                save_to_supabase(user_query, answer)
 
        except Exception as e:
            print("shivam : Sorry, I can't assist with that.")
            print("DEBUG Exception:", e)
 
        print("\n" + "-" * 50 + "\n")

def process_user_query(user_query, user_session):
    # This is a wrapper for your main RAG logic
    try:
        if user_session is None:
            print("[ERROR] No user_session set in process_user_query")
            return "User not authenticated."
        print(f"[DEBUG] process_user_query: current_user={user_session.username}, role={user_session.role}, dealer_id={user_session.dealer_id}")
        sql = get_llm_sql(user_query, user_session)
        sql = clean_sql_output(sql)
        sql_context = "No results found."
        if sql.strip().upper() != "NO_SQL" and sql.strip().lower().startswith("select"):
            sql_result, sql_error = try_select_sql(sql)
            if sql_result:
                sql_context = sql_result_to_context(sql_result)
        rewritten_query = rewrite_query_for_rag(user_query)
        query_embedding = get_embedding(preprocess_query(rewritten_query))
        metadata_filter = extract_metadata_with_llm(user_query)
        vector_rows = vector_store_similarity_search(
            query_embedding,
            top_k=10,
            metadata_filter=metadata_filter,
            similarity_threshold=0.08
        )
        rag_context = vector_rows_to_context(vector_rows) if vector_rows else "No relevant vector context found."
        answer = get_llm_final_response(sql_context, rag_context, user_query, user_session)
        return answer
    except Exception as e:
        print("[ERROR] process_user_query failed:", e)
        return "Sorry, I can't assist with that."

if __name__ == "__main__":
    main()
 
 
    
