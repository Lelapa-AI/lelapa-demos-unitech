import json
from vulavula import VulavulaClient

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
                            "answer": item['answer']
                        }

                # If intent is not found in the faq_data
                return f"Identified intent: {top_intent} with confidence {top_confidence}, but no corresponding answer was found."
            else:
                return "No probabilities found in classification results."
        except Exception as e:
            print(f"An error occurred while classifying the input: {e}")
            return "Error processing the question."
