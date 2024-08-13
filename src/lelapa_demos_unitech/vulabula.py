from vulavula import VulavulaClient
import os
import json
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

DetectorFactory.seed = 0

def detect_language(text):
    try:
        lang = detect(text)
        if lang == 'en':
            return 'eng'
        elif lang == 'zu':
            return 'zul'
        elif lang == 'st':
            return 'sot'
        else:
            return 'eng' 
    except LangDetectException:
        return 'eng'
    
def load_faq_data(faq_path):
    """
    Load FAQ data from a JSON file.
    
    :param faq_path: Path to the FAQ JSON file
    :return: List of FAQ entries
    """
    with open(faq_path, 'r') as f:
        return json.load(f)

def create_knowledge_base(client, faqs, language="eng"):
    """
    Create a knowledge base with provided FAQ data.

    :param client: VulavulaClient instance
    :param faqs: List of FAQ data
    :param language: Language of the FAQs (default is "eng")
    """
    for faq in faqs:
        # print(faq)
        client.create_documents(content=faq['content'], language=language)
        print(f"Added FAQ document to knowledge base: {faq['content']}")


def vulavula_translator(query, token, faq_path, target_language=None):
    """
    Function to translate and query using Vulavula API with language detection.
    
    :param query: The query string to be translated and searched
    :param token: Vulavula API token
    :param target_language: Optional target language for translation (eng, zul, or sot)
    :param faq_data: Optional path to a file containing FAQ data
    :return: Query responses in the detected or target language
    """
    # Initialize Vulavula client
    client = VulavulaClient(token)

    # Supported languages
    supported_languages = {'eng': 'English', 'zul': 'IsiZulu', 'sot': 'SeSotho'}

    # Load FAQ data
    faqs = load_faq_data(faq_path)
    

    # Create knowledge base
    knowledge_base_data = {
        "collection": "vv-search"
    }

    print(f"Creating knowledge base with data: {knowledge_base_data}")
    # print(f"Using API URL: {client.search.create_collection.url}")

    knowledge_base = client.create_knowledgebase(knowledge_base_data)
    print("Knowledge Base Created:", knowledge_base)

    # Add FAQ data to the knowledge base
    create_knowledge_base(client, faqs)

    # Detect the language of the query
    detected_language = detect_language(query)
    print(f"Detected query language: {supported_languages[detected_language]}")

    # If no target language is specified, use the detected language
    if not target_language:
        target_language = detected_language
    elif target_language not in supported_languages:
        print(f"Specified target language {target_language} is not supported. Using detected language.")
        target_language = detected_language

    # Translate query to target language if needed
    if detected_language != target_language:
        translated_query = client.translate(text=query, source_lang=detected_language, target_lang=target_language)
        print(f"Translated Query ({supported_languages[target_language]}):", translated_query)
    else:
        translated_query = query
        print(f"No translation needed. Query is already in {supported_languages[target_language]}.")

    # Perform query in target language
    target_responses = client.query(query=translated_query, language=target_language)
    print(f"Responses in {supported_languages[target_language]}:", target_responses)

    return {
        "detected_language": supported_languages[detected_language],
        "response_language": supported_languages[target_language],
        "original_query": query,
        "translated_query": translated_query if detected_language != target_language else None,
        "responses": target_responses
    }


if __name__ == "__main__":
    TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjAxMzhjYzUyOWFjMDRjYThiNmY4YzFlYzI2MTljYjQwIiwiY2xpZW50X2lkIjo3MCwicmVxdWVzdHNfcGVyX21pbnV0ZSI6MCwibGFzdF9yZXF1ZXN0X3RpbWUiOm51bGx9.Q8VPUsIqS_5PQoQOSm08ICYSYGmpF3sVn5qtg9LBQNw"


    # Get the root directory of the project
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

    # Construct the correct path to the FAQ file
    FAQ_PATH = os.path.join(PROJECT_ROOT, 'data', 'eskom_faqs.json')

    # FAQ_PATH = os.path.join(os.path.dirname(__file__), '', 'data', 'eskom_faqs.json')
    
    print(FAQ_PATH)
    print("HELLO, FRIEND")

    queries = [
        "How do I get prepayment electricity?",  # English
    ]

    for query in queries:
        result = vulavula_translator(
            query=query,
            token=TOKEN,
            faq_path=FAQ_PATH,
            # target_language is not specified, so it will respond in the detected language
        )

        print("\nQuery Results:")
        print("Original Query:", result["original_query"])
        print("Detected Language:", result["detected_language"])
        print("Response Language:", result["response_language"])
        if result["translated_query"]:
            print("Translated Query:", result["translated_query"])
        print("Responses:", result["responses"])
        print("-" * 50)

    # Example with a specified target language
    result = vulavula_translator(
        query="How much does electricity cost?",
        token=TOKEN,
        target_language="zul",  # Specify IsiZulu as the target language
        faq_path=FAQ_PATH
    )

    print("\nQuery Results with Specified Target Language:")
    print("Original Query:", result["original_query"])
    print("Detected Language:", result["detected_language"])
    print("Response Language:", result["response_language"])
    if result["translated_query"]:
        print("Translated Query:", result["translated_query"])
    print("Responses:", result["responses"])