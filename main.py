import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import BlogPost

app = FastAPI(title="Mom's Colorful Blog API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Mom's Blog Backend is running!"}

# Helpers
class BlogPostOut(BaseModel):
    id: str
    title: str
    content: str
    author: str
    tags: List[str] = []
    cover_image: Optional[str] = None


def serialize_post(doc) -> BlogPostOut:
    return BlogPostOut(
        id=str(doc.get("_id")),
        title=doc.get("title"),
        content=doc.get("content"),
        author=doc.get("author", "Mom"),
        tags=doc.get("tags", []),
        cover_image=doc.get("cover_image"),
    )


@app.get("/api/posts", response_model=List[BlogPostOut])
def list_posts(limit: int = 10):
    try:
        docs = get_documents("blogpost", {}, limit)
        return [serialize_post(d) for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/posts", response_model=str)
def create_post(post: BlogPost):
    try:
        new_id = create_document("blogpost", post)
        return new_id
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
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
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
