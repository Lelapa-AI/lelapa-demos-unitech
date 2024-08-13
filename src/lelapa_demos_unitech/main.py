from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from query_processor import load_faqs, find_best_match
from translator import translate_text

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
        return {"question": best_match["question"], "answer": best_match["answer"]}
    elif query.language in ["zu", "st"]:
        translated_question = translate_text(best_match["question"], query.language)
        translated_answer = translate_text(best_match["answer"], query.language)
        return {"question": translated_question, "answer": translated_answer}
    else:
        raise HTTPException(status_code=400, detail="Unsupported language")