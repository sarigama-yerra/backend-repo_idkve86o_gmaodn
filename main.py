import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import User, BlogPost, ContactMessage

app = FastAPI(title="SaaS Starter API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "SaaS Backend Running"}

# -------- Auth (simplified) --------
class RegisterPayload(BaseModel):
    name: str
    email: EmailStr
    password: str

@app.post("/api/auth/register")
def register_user(payload: RegisterPayload):
    # Very simplified: store hashed (demo) password. In prod, use bcrypt/argon2.
    import hashlib, os as _os
    salt = _os.urandom(8).hex()
    pw_hash = hashlib.sha256((salt + payload.password).encode()).hexdigest()
    user = User(name=payload.name, email=payload.email, password_hash=f"{salt}${pw_hash}")
    try:
        user_id = create_document("user", user)
        return {"id": user_id, "name": user.name, "email": user.email}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class LoginPayload(BaseModel):
    email: EmailStr
    password: str

@app.post("/api/auth/login")
def login_user(payload: LoginPayload):
    # Very simplified login: find by email and verify hash
    try:
        docs = list(db["user"].find({"email": payload.email}).limit(1))
        if not docs:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        user = docs[0]
        salt, saved_hash = user.get("password_hash", "$").split("$", 1)
        import hashlib
        if hashlib.sha256((salt + payload.password).encode()).hexdigest() != saved_hash:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return {"id": str(user.get("_id")), "name": user.get("name"), "email": user.get("email")}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# -------- Blog --------
@app.get("/api/blog", response_model=List[dict])
def list_blog():
    posts = get_documents("blogpost", {"published": True}, limit=20)
    for p in posts:
        p["id"] = str(p.pop("_id", ""))
    return posts

class BlogCreatePayload(BaseModel):
    title: str
    slug: str
    excerpt: Optional[str] = None
    content: str
    author: str
    published: bool = True

@app.post("/api/blog")
def create_blog(payload: BlogCreatePayload):
    post = BlogPost(**payload.model_dump())
    try:
        post_id = create_document("blogpost", post)
        return {"id": post_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# -------- Contact --------
class ContactPayload(BaseModel):
    name: str
    email: EmailStr
    topic: Optional[str] = None
    message: str

@app.post("/api/contact")
def submit_contact(payload: ContactPayload):
    msg = ContactMessage(**payload.model_dump())
    try:
        msg_id = create_document("contactmessage", msg)
        return {"id": msg_id, "status": "received"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Health and DB test
@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
