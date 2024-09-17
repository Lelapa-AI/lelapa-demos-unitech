import json
from vulavula import VulavulaClient
from functools import lru_cache
import orjson

class EskomFAQBot:
    def __init__(self, vula_vula_token, eskom_faq_file_path, emfuleni_faq_file_path):
        self.client = VulavulaClient(vula_vula_token)
        self.faq_data = self.load_faq_data(eskom_faq_file_path, emfuleni_faq_file_path)
        self.classification_data = self.prepare_classification_data()
        self.intent_to_answer = {item['intent']: item['answer'] for item in self.faq_data['faq']}

    @staticmethod
    def load_faq_data(eskom_path, emfuleni_path):
        faq_data = {"faq": []}
        for path in (eskom_path, emfuleni_path):
            try:
                with open(path, 'rb') as f:
                    faq_data['faq'].extend(orjson.loads(f.read())['faq'])
            except FileNotFoundError as e:
                print(f"Error: {e}")
                exit()
        return faq_data
    
    def prepare_classification_data(self):
        return {
            "examples": [
                {"intent": item['intent'], "example": example}
                for item in self.faq_data['faq']
                for example in item['examples']
            ],
            "inputs": []
        }
    
    @lru_cache(maxsize=128)
    def translate_answer(self, answer, language):
        try:
            translation_data = {
                "input_text": answer,
                "source_lang": "eng_Latn",
                "target_lang": language
            }
            translated_answer = self.client.translate(translation_data)
            return translated_answer['translation'][0]['translated_text']
        except Exception as e:
            print(f"An error occurred during translation: {e}")
            return "Error translating the answer."
    
    def answer_question(self, question, language=None):
        try:
            classification_data = self.classification_data.copy()
            classification_data['inputs'] = [question]
            
            classification_results = self.client.classify(classification_data)
            
            if classification_results and 'probabilities' in classification_results[0]:
                top_intent = max(classification_results[0]['probabilities'], key=lambda x: x['score'])

                if float(top_intent['score']) < float(0.09):
                    return "Please contact Lethabo service."
                
                answer = self.get_translated_answer(top_intent, language)
                
                # if answer and language and language != 'eng_Latn':
                #     return self.translate_answer(answer, language)
                return answer
            else:
                return "No probabilities found in classification results."
        except Exception as e:
            print(f"An error occurred while classifying the input: {e}")
            return str(e)
        
    
    def get_translated_answer(self, top_intent, language_code):
        # Get the intent
        answers = self.intent_to_answer.get(top_intent['intent'])
        
        if not answers:
            return "Sorry, I could not find an answer for that question."

        # Find the translation for the provided language code
        for answer in answers:
            if language_code in answer:
                return answer[language_code]
        
        # Fallback to English if the translation is not found
        return answers[0].get('eng_Latn', "Sorry, no translation available.")