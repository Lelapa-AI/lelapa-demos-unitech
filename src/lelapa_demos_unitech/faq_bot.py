from vulavula import VulavulaClient
import json
from fuzzywuzzy import process
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from .data import FAQCategorizer
import re

class TranslationError(Exception):
    pass

class EskomFAQBot:
    def __init__(self, vula_token, faq_file_path, emfuleni_file_path):
        self.client = VulavulaClient(vula_token)
        self.eskom_data = self.load_faq_data(faq_file_path)
        self.emfuleni_data = self.load_emfuleni_data(emfuleni_file_path)
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
                        "example": faq['question'],
                        "language": "en"
                    })
                    
                    try:
                        zulu_question = self.translate_with_retry(faq['question'], "eng_Latn", "zul_Latn")
                        classification_data["examples"].append({
                            "intent": category,
                            "example": zulu_question,
                            "language": "zu"
                        })
                    except TranslationError as e:
                        print(f"Translation failed for question: {faq['question']}. Error: {str(e)}")
                        # Log the error for later investigation
                        self.log_error(f"Translation error: {str(e)}", faq['question'])

                        classification_data["examples"].append({
                            "intent": category,
                            "example": faq['question'],
                            "language": "en"
                        })
                    except Exception as e:
                        print(f"Unexpected error during translation: {str(e)}")
                        self.log_error(f"Unexpected translation error: {str(e)}", faq['question'])
        
        # print(self.emfuleni_data)
        new_faqs = self.parse_faq_from_text(self.emfuleni_data)
        print(new_faqs)
        # question_pattern = re.compile(r'^\d+\.\s+(.*?)\n\s*\* Answer:', re.DOTALL | re.MULTILINE)
        # questions = question_pattern.findall(self.emfuleni_data)

        # print(len(questions), questions)
        # emfuleni_faqs = self.get_emfuleni_faqs()
        # for faq in emfuleni_faqs:
        #     classification_data["examples"].append({
        #         "intent": "Emfuleni FAQs",
        #         "example": faq['question'],
        #         "language": "en"
        #     })
            
        #     try:
        #         zulu_question = self.translate_with_retry(faq['question'], "eng_Latn", "zul_Latn")
        #         classification_data["examples"].append({
        #             "intent": "Emfuleni FAQs",
        #             "example": zulu_question,
        #             "language": "zu"
        #         })
        #     except TranslationError as e:
        #         print(f"Translation failed for question: {faq['question']}. Error: {str(e)}")
        #         self.log_error(f"Translation error: {str(e)}", faq['question'])
        #     except Exception as e:
        #         print(f"Unexpected error during translation: {str(e)}")
        #         self.log_error(f"Unexpected translation error: {str(e)}", faq['question'])

        print(classification_data)
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


    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(TranslationError),
        reraise=True
    )
    def translate_with_retry(self, text, source_lang, target_lang):
        translation_data = {
            "input_text": text,
            "source_lang": source_lang,
            "target_lang": target_lang
        }
        result = self.client.translate(translation_data)
        if 'error' in result and result['error']:
            raise TranslationError(f"Translation failed: {result.get('message', 'Unknown error')}")
        return result.get('translated_text', '')

    def log_error(self, error_message, question):
        # Implement your logging mechanism here
        # For example, write to a file or send to a logging service
        pass

    
    def load_emfuleni_data(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def parse_faq_from_text(self, text):
        # Split the text into individual FAQ items
        faq_items = re.split(r'\n\d+\.\s', text)  # Skip the first empty split
        
        faqs = []
        for item in faq_items:
            # Split each item into question and answer
            parts = item.split('\n* Answer: ', 1)
            if len(parts) == 2:
                question, answer = parts
                # Clean up the answer (remove newlines and extra spaces)
                answer = ' '.join(answer.split())
                faqs.append({"question": question.strip(), "answer": answer.strip()})
        
        return faqs


        

    def get_emfuleni_faqs(self):
        faqs = []
        current_question = None
        current_answer = []

        for line in self.emfuleni_data.split('\n'):
            line = line.strip()
            if line.startswith(tuple(f"{i}. " for i in range(1, 25))):
                if current_question:
                    faqs.append({"question": current_question, "answer": ' '.join(current_answer)})
                current_question = line.split('. ', 1)[1]
                current_answer = []
            elif line.startswith('* Answer:'):
                current_answer.append(line.replace('* Answer:', '').strip())
            elif current_answer:
                current_answer.append(line)

        if current_question:
            faqs.append({"question": current_question, "answer": ' '.join(current_answer)})

        return faqs
    
    
    def answer_question(self, query, language=None):
        # Default to English if no language is specified
        language = language or 'en'

        if language not in self.supported_languages:
            return f"Sorry, I don't support the language: {language}"


        intent = self.classify_query(query)
        if intent in self.eskom_data:
            best_match = self.find_best_match(query, self.eskom_data[intent]['faqs'])
            if best_match:
                return best_match['answer']
        
        default_messages = {
            'en': "I'm sorry, I couldn't find a matching answer to your question.",
        }
        return default_messages.get(language, default_messages['en'])

