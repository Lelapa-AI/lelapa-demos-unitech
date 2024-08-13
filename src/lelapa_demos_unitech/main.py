from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .query_processor import load_faqs, find_best_match
from .vulabula import vulavula_translator

app = FastAPI()

faqs = load_faqs()

class Query(BaseModel):
    text: str
    language: str

@app.post("/query_faq")
async def query_faq(query: Query):
    best_match = find_best_match(query.text, faqs)
    if not best_match:
        raise HTTPException(status_code=404, detail="No matching FAQ found")
    
    if query.language == "en":
        return {"question": best_match["faq"], "answer": best_match["faq_response"]}
    elif query.language in ["zu", "st"]:
        translated_question = translate_text(best_match["faq"], query.language)
        translated_answer = vulavula_translator(best_match["faq_response"], query.language)
        return {"faq": translated_question, "faq_response": translated_answer}
    else:
        raise HTTPException(status_code=400, detail="Unsupported language")