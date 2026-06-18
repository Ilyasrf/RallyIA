from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from shared.database import SessionLocal, Property
from shared.embedding_service import get_embedding
from chatbot.schemas import ChatRequest, ChatResponse
from chatbot.service import generate_chat_reply

router = APIRouter(prefix="/chat", tags=["Chatbot"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("", response_model=ChatResponse)
def chat_with_bot(request: ChatRequest, db: Session = Depends(get_db)):
    if not request.messages:
        raise HTTPException(status_code=400, detail="Messages list cannot be empty.")

    latest_msg = request.messages[-1].content

    try:
        query_embedding = get_embedding(latest_msg)
        db_query = (
            select(Property)
            .order_by(Property.embedding.cosine_distance(query_embedding))
            .limit(2)
        )
        relevant_properties = db.execute(db_query).scalars().all()
    except Exception:
        relevant_properties = []

    messages_dict = [{"role": msg.role, "content": msg.content} for msg in request.messages]

    try:
        reply_text = generate_chat_reply(messages_dict, relevant_properties)
        return ChatResponse(reply=reply_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")
