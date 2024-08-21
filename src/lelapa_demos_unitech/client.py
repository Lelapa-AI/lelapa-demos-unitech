import json
from vulavula import VulavulaClient
from dotenv import load_dotenv
import os

class EskomFAQBot:
    def __init__(self, vula_vula_token, eskom_faq_file_path, emfuleni_faq_file_path):
        self.client = VulavulaClient(vula_vula_token)
        self.faq_data = {
            "faq": []
        }

        # Load the JSON data from both Eskom and Emfuleni FAQ files
        try:
            with open(eskom_faq_file_path, 'r') as f:
                eskom_data = json.load(f)
                self.faq_data['faq'].extend(eskom_data['faq'])

            with open(emfuleni_faq_file_path, 'r') as f:
                emfuleni_data = json.load(f)
                self.faq_data['faq'].extend(emfuleni_data['faq'])
        except FileNotFoundError as e:
            print(f"Error: {e}")
            exit()

    def prepare_classification_data(self):
        classification_data = {
            "examples": [],
            "inputs": []
        }

        # Populate the classification data with examples
        for item in self.faq_data['faq']:
            for example in item['examples']:
                classification_data['examples'].append({
                    "intent": item['intent'],
                    "example": example
                })

        return classification_data

    def answer_question(self, question, language=None):
        classification_data = self.prepare_classification_data()

        # Add the user input to the classification data
        classification_data['inputs'].append(question)

        # Classify input
        try:
            classification_results = self.client.classify(classification_data)

            if classification_results and 'probabilities' in classification_results[0]:
                probabilities = classification_results[0]['probabilities']
                sorted_probs = sorted(probabilities, key=lambda x: x['score'], reverse=True)
                top_intent = sorted_probs[0]['intent']
                top_confidence = sorted_probs[0]['score']

                # Map intent to the corresponding FAQ answer
                for item in self.faq_data['faq']:
                    if item['intent'] == top_intent:
                        return {
                            "intent": top_intent,
                            "confidence": top_confidence,
                            "answer": item['answer']  # Assuming each FAQ item has an 'answer' field
                        }

                # If intent is not found in the faq_data
                return f"Identified intent: {top_intent} with confidence {top_confidence}, but no corresponding answer was found."
            else:
                return "No probabilities found in classification results."
        except Exception as e:
            print(f"An error occurred while classifying the input: {e}")
            return "Error processing the question."

    # def answer_question(self, question, language=None):
    #     classification_data = self.prepare_classification_data()

    #     # Add the user input to the classification data
    #     classification_data['inputs'].append(question)

    #     # Classify input
    #     try:
    #         classification_results = self.client.classify(classification_data)

    #         if classification_results and 'probabilities' in classification_results[0]:
    #             probabilities = classification_results[0]['probabilities']
    #             sorted_probs = sorted(probabilities, key=lambda x: x['score'], reverse=True)
    #             top_intent = sorted_probs[0]['intent']
    #             top_confidence = sorted_probs[0]['score']

    #             #Map intent from faq_data
    #             return f"Identified intent: {top_intent} with confidence {top_confidence}"
    #         else:
    #             return "No probabilities found in classification results."
    #     except Exception as e:
    #         print(f"An error occurred while classifying the input: {e}")
    #         return "Error processing the question."







































# from vulavula import VulavulaClient
# import json
# from fuzzywuzzy import process
# from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
# from .data import FAQCategorizer
# import re

# class TranslationError(Exception):
#     pass

# class EskomFAQBot:

#     def __init__(self, vula_token, emfuleni_faq_file_path, eskom_faq_file_path):
#         self.client = VulavulaClient(vula_token)
#         self.faq_data = self.load_faq_data(emfuleni_faq_file_path)
#         self.classification_data = self.prepare_classification_data()
#         self.supported_languages = ['en','zul'] 

#     # def __init__(self, vula_token, faq_file_path):
#     #     self.client = VulavulaClient(vula_token)
#     #     self.faq_data = self.load_faq_data(faq_file_path)
#     #     self.classification_data = self.prepare_classification_data()
#     #     self.supported_languages = ['en','zul'] 


#     def load_faq_data(self, file_path):
#         with open(file_path, 'r') as f:
#             return json.load(f)
        
    
#     def prepare_classification_data(self):
#         classification_data = {"examples": []}
#         print(self.faq_data)
#         for category, data in self.faq_data.items():
#             if 'faqs' in data:
#                 for faq in data['faqs']:
#                     classification_data["examples"].append({
#                         "intent": category,
#                         "example": faq['question']
#                     })
#         # print(classification_data)
#         return classification_data
    

#     # def prepare_classification_data(self):
#     #     classification_data = {"examples": []}
#     #     for category, data in self.eskom_data.items():
#     #         if 'faqs' in data:
#     #             for faq in data['faqs']:
#     #                 classification_data["examples"].append({
#     #                     "intent": category,
#     #                     "example": faq['question'],
#     #                     "language": "en"
#     #                 })
                    
#     #                 try:
#     #                     zulu_question = self.translate_with_retry(faq['question'], "eng_Latn", "zul_Latn")
#     #                     classification_data["examples"].append({
#     #                         "intent": category,
#     #                         "example": zulu_question,
#     #                         "language": "zu"
#     #                     })
#     #                 except TranslationError as e:
#     #                     print(f"Translation failed for question: {faq['question']}. Error: {str(e)}")
#     #                     # Log the error for later investigation
#     #                     self.log_error(f"Translation error: {str(e)}", faq['question'])

#     #                     classification_data["examples"].append({
#     #                         "intent": category,
#     #                         "example": faq['question'],
#     #                         "language": "en"
#     #                     })
#     #                 except Exception as e:
#     #                     print(f"Unexpected error during translation: {str(e)}")
#     #                     self.log_error(f"Unexpected translation error: {str(e)}", faq['question'])
        
#     #     # print(self.emfuleni_data)
#     #     new_faqs = self.parse_faq_from_text(self.emfuleni_data)
#     #     print(new_faqs)
#     #     # question_pattern = re.compile(r'^\d+\.\s+(.*?)\n\s*\* Answer:', re.DOTALL | re.MULTILINE)
#     #     # questions = question_pattern.findall(self.emfuleni_data)

#     #     # print(len(questions), questions)
#     #     # emfuleni_faqs = self.get_emfuleni_faqs()
#     #     # for faq in emfuleni_faqs:
#     #     #     classification_data["examples"].append({
#     #     #         "intent": "Emfuleni FAQs",
#     #     #         "example": faq['question'],
#     #     #         "language": "en"
#     #     #     })
            
#     #     #     try:
#     #     #         zulu_question = self.translate_with_retry(faq['question'], "eng_Latn", "zul_Latn")
#     #     #         classification_data["examples"].append({
#     #     #             "intent": "Emfuleni FAQs",
#     #     #             "example": zulu_question,
#     #     #             "language": "zu"
#     #     #         })
#     #     #     except TranslationError as e:
#     #     #         print(f"Translation failed for question: {faq['question']}. Error: {str(e)}")
#     #     #         self.log_error(f"Translation error: {str(e)}", faq['question'])
#     #     #     except Exception as e:
#     #     #         print(f"Unexpected error during translation: {str(e)}")
#     #     #         self.log_error(f"Unexpected translation error: {str(e)}", faq['question'])

#     #     print(classification_data)
#     #     return classification_data

#     def classify_query(self, query: str):
#         self.classification_data["inputs"] = [query]
#         classification_results = self.client.classify(self.classification_data)
#         probabilities = classification_results[0]['probabilities']
#         sorted_probs = sorted(probabilities, key=lambda x: x['score'], reverse=True)
#         return sorted_probs[0]['intent']

#     def find_best_match(self, query, faqs):
#         faq_questions = [faq['question'] for faq in faqs]
#         best_match, best_score = process.extractOne(query, faq_questions)
        
#         if best_score > 70:
#             return next(faq for faq in faqs if faq['question'] == best_match)
        
#         return None


#     @retry(
#         stop=stop_after_attempt(3),
#         wait=wait_exponential(multiplier=1, min=4, max=10),
#         retry=retry_if_exception_type(TranslationError),
#         reraise=True
#     )
#     def translate_with_retry(self, text, source_lang, target_lang):
#         translation_data = {
#             "input_text": text,
#             "source_lang": source_lang,
#             "target_lang": target_lang
#         }
#         result = self.client.translate(translation_data)
#         if 'error' in result and result['error']:
#             raise TranslationError(f"Translation failed: {result.get('message', 'Unknown error')}")
#         return result.get('translated_text', '')

#     def log_error(self, error_message, question):
#         # Implement your logging mechanism here
#         # For example, write to a file or send to a logging service
#         pass   
    
#     def answer_question(self, query, language=None):
#         # Default to English if no language is specified
#         language = language or 'en'

#         if language not in self.supported_languages:
#             return f"Sorry, I don't support the language: {language}"


#         intent = self.classify_query(query)
#         if intent in self.faq_data:
#             best_match = self.find_best_match(query, self.faq_data[intent]['faqs'])
#             if best_match:
#                 return best_match['answer']
        
#         default_messages = {
#             'en': "I'm sorry, I couldn't find a matching answer to your question.",
#         }
#         return default_messages.get(language, default_messages['en'])

