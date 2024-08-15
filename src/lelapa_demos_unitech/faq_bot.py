from fastapi import HTTPException
from vulavula import VulavulaClient
import json
from fuzzywuzzy import process
from langdetect import detect


class EskomFAQBot:
    def __init__(self, vula_token, faq_file_path):
        self.client = VulavulaClient(vula_token)
        self.eskom_data = self.load_faq_data(faq_file_path)
        self.classification_data = self.prepare_classification_data()
        self.supported_languages = ['en','zul'] 

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
        
        if best_score > 70:
            return next(faq for faq in faqs if faq['question'] == best_match)
        
        return None


    @staticmethod
    def get_translated_text(translation_result, default_answer):
        # Extract the 'translation' list from the result
        translations = translation_result.get('translation', [])
        
        # Check if the list is not empty and access the first element's 'translated_text'
        if translations and 'translated_text' in translations[0]:
            return translations[0]['translated_text']
        
        # Return the default answer if the translation is not available
        return default_answer
    
    def answer_question(self, query_data: dict):
        question = query_data.get('question', '')
        target_language = query_data.get('language')
        source_language = None
        
        source_language = self.detect_language(question)
        
        print('Question: ', question)
        print('Target Lingo: ', target_language)
        print('Source Lingo: ', source_language)

        if source_language != 'en':
            translation_data = {
                "input_text": question,
                "source_lang": f"{source_language}_Latn",
                "target_lang": "eng_Latn"
            }
            translation_result = self.client.translate(translation_data)
            english_question = translation_result[0].get('translated_text', question)
        else:
            english_question = question

        intent = self.classify_query(english_question)
        
        if intent in self.eskom_data:
            best_match = self.find_best_match(english_question, self.eskom_data[intent]['faqs'])
            
            if best_match:
                if isinstance(best_match['answer'], dict) and source_language in best_match['answer']:
                    answer = best_match['answer'][source_language]
                else:
                    answer = best_match['answer'] if isinstance(best_match['answer'], str) else best_match['answer'].get('en', '')
                                
                if target_language and target_language != source_language:
                    translation_data = {
                        "input_text": answer,
                        "source_lang": "eng_Latn",
                        "target_lang": f"{target_language}_Latn"
                    }
                    translation_result = self.client.translate(translation_data)                    
                    result = self.get_translated_text(translation_result, answer)
                    return result
                return answer
        
        default_messages = {
            'en': "I'm sorry, I couldn't find a matching answer to your question.",
            'zul': "Ngiyaxolisa, angitholanga mpendulo ehambisana nombizo wakho.",
        }
        return default_messages.get(source_language, default_messages['en'])


    def detect_language(self, query: str):
        try:
            detected_lang = detect(query)
            print('LANGUAGE', detected_lang)
            return detected_lang if detected_lang in self.supported_languages else 'en'
        except:
            return 'en' 
    