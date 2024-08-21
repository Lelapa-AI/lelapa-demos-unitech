import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from .client import EskomFAQBot

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
eskom_faq_file_path = os.getenv("ESKOM_FAQ_FILE_PATH")
emfuleni_faq_file_path = os.getenv("EMFULENI_FAQ_FILE_PATH")

bot_bot = EskomFAQBot(vulavula_token, eskom_faq_file_path, emfuleni_faq_file_path)

class Query(BaseModel):
    question: str
    language: str = None

@app.get("/")
async def root():
    return {"message": "Welcome to the Emfuleni FAQ API"}

@app.post("/faq")
async def answer_question(query: Query):
    try:
        # Pass both question and language to the answer_question method
        response = bot_bot.answer_question(query.question, query.language)
        return {"answer": response}
    except Exception as e:
        print(f"Error in answer_question: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))