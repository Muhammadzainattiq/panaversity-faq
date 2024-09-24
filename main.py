from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import SQLModel, Field, create_engine, Session, select
from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel

app = FastAPI(
    title="FAQ GPT API",
    description="API for adding unanswered questions to the database",
    version="1.0.0",
)

# Database Configuration
DATABASE_URL = "postgresql://neondb_owner:jIg9Cs1Lxeqy@ep-bold-darkness-a5z0u0uu.us-east-2.aws.neon.tech/neondb?sslmode=require"
engine = create_engine(DATABASE_URL)

# Models
class QuestionBase(SQLModel):
    question: str

class Question(QuestionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    datetime: datetime

class QuestionCreate(QuestionBase):
    pass

class QuestionRead(QuestionBase):
    id: int
    datetime: datetime

    class Config:
        from_attributes = True

# Dependency to get DB session
def get_session():
    with Session(engine) as session:
        yield session

# Create the database and tables
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

@app.post("/questions/", response_model=QuestionRead, status_code=201, summary="Add a new question", description="Adds a new question to the database.")
async def add_question(question: QuestionCreate, session: Session = Depends(get_session)):
    new_question = Question(question=question.question, datetime=datetime.now(timezone.utc))
    session.add(new_question)
    session.commit()
    session.refresh(new_question)
    return new_question

@app.get("/", summary="Root endpoint", description="Welcome message for the API.")
async def read_root():
    return {"message": "Welcome to the FAQ GPT API..."}
