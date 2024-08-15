from vulavula import VulavulaClient
import json
from fuzzywuzzy import process

class EskomFAQBot:
    def __init__(self, vula_token, faq_file_path):
        self.client = VulavulaClient(vula_token)
        self.eskom_data = self.load_faq_data(faq_file_path)
        self.classification_data = self.prepare_classification_data()

    def load_faq_data(self, file_path):
        with open(file_path, 'r') as f:
            return json.load(f)

    def prepare_classification_data(self):
        classification_data = {"examples": []}
        for category, data in self.eskom_data.items():
            if 'faqs' in data:
                for faq in data['faqs']:
                    classification_data["examples"].append({
                        "intent": category,
                        "example": faq['question']
                    })
        return classification_data

    def classify_query(self, query: str):
        self.classification_data["inputs"] = [query]
        classification_results = self.client.classify(self.classification_data)
        probabilities = classification_results[0]['probabilities']
        sorted_probs = sorted(probabilities, key=lambda x: x['score'], reverse=True)
        return sorted_probs[0]['intent']

    def find_best_match(self, query, faqs):
        faq_questions = [faq['question'] for faq in faqs]
        best_match, best_score = process.extractOne(query, faq_questions)
        
        if best_score > 70:  # Similarity threshold
            return next(faq for faq in faqs if faq['question'] == best_match)
        
        return None

    def answer_question(self, query: str):
        intent = self.classify_query(query)
        if intent in self.eskom_data:
            best_match = self.find_best_match(query, self.eskom_data[intent]['faqs'])
            if best_match:
                return best_match['answer']
        
        return "I'm sorry, I couldn't find a matching answer to your question."
