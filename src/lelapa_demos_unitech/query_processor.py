import json
from fuzzywuzzy import fuzz

def load_faqs():
    with open('eskom_faqs.json', 'r') as f:
        return json.load(f)

def find_best_match(query, faqs):
    best_match = None
    highest_score = 0
    
    for faq in faqs:
        score = fuzz.token_set_ratio(query.lower(), faq['faq'].lower())
        if score > highest_score:
            highest_score = score
            best_match = faq
    
    return best_match if highest_score > 60 else None