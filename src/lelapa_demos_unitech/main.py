import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from .faq_bot import EskomFAQBot

load_dotenv()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize the EskomFAQBot
vulavula_token = os.getenv("VULAVULA_API_TOKEN")
faq_file_path = os.getenv("FAQ_FILE_PATH")

bot_bot = EskomFAQBot(vulavula_token, faq_file_path)

class Query(BaseModel):
    question: str

@app.get("/")
async def root():
    return {"message": "Welcome to the Eskom FAQ API"}

@app.post("/faq")
async def answer_question(query: Query):
    try:
        response = bot_bot.answer_question(query.question)
        return {"answer": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    