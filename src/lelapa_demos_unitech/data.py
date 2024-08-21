import requests
from bs4 import BeautifulSoup
import json
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from typing import List, Dict
import logging
from vulavula import VulavulaClient
from vulavula.common.error_handler import VulavulaError
from dotenv import load_dotenv
import time



# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FAQScraper:
    def __init__(self, url: str):
        self.url = url

    def scrape(self) -> List[Dict[str, str]]:
        logging.info(f"Scraping FAQs from {self.url}")
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            faqs = []
            faq_elements = soup.find_all('div', class_='eael-accordion-list')
            
            for faq_element in faq_elements:
                question_element = faq_element.find('span', class_='eael-accordion-tab-title')
                answer_element = faq_element.find('div', id=lambda x: x and x.startswith('elementor-tab-content-'))
                
                if question_element and answer_element:
                    faqs.append({
                        "question": question_element.text.strip(),
                        "answer": answer_element.text.strip()
                    })
            
            logging.info(f"Successfully scraped {len(faqs)} FAQs")
            return faqs
        except requests.RequestException as e:
            logging.error(f"Error scraping FAQs: {e}")
            return []


class FAQExporter:
    @staticmethod
    def to_json(categories: Dict[str, Dict], filename: str):
        logging.info(f"Saving FAQs to JSON: {filename}")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(categories, f, indent=2, ensure_ascii=False)

    @staticmethod
    def to_pdf(categories: Dict[str, Dict], filename: str):
        logging.info(f"Saving FAQs to PDF: {filename}")
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        
        content = []
        
        # Title
        content.append(Paragraph('Eskom FAQs', styles['Title']))
        content.append(Spacer(1, 12))
        
        for category, data in categories.items():
            # Category title
            content.append(Paragraph(category, styles['Heading1']))
            content.append(Spacer(1, 6))
            
            for faq in data['faqs']:
                # Question
                content.append(Paragraph(faq['question'], styles['Heading2']))
                content.append(Spacer(1, 6))
                
                # Answer
                content.append(Paragraph(faq['answer'], styles['BodyText']))
                content.append(Spacer(1, 12))
        
        doc.build(content)

def convert_faq_data(input_data, client: VulavulaClient):
    # Initialize the structure for the output JSON
    output_data = {"faq": []}

    # Process each entry in the input data
    for entry in input_data:
        question = entry['question']
        question_lower = question.lower()

        answer = entry['answer']
        
        # Determine the intent based on the question (or use a predefined mapping)
        # For simplicity, we'll use a basic rule-based approach for assigning intents
        if 'prepayment electricity' in question_lower:
            intent = 'prepayment_electricity'
        elif 'prepayment meter' in question_lower:
            intent = 'prepaid_meter'
        elif 'How many prepaid meters' in question_lower:
            intent = 'prepaid_meters_info'
        elif 'work' in question_lower or 'problem' in question_lower:
            intent = 'prepaid_meter_issues'
        elif 'save money' in question_lower:
            intent = 'save_money'
        elif 'about electricity' in question_lower:
            intent = 'electricity_information'
        elif 'sell vending systems' in question_lower:
            intent = 'sell_vending_systems'
        elif 'purchase' in question_lower:
            intent = 'purchase_electricity'
        elif 'transfer' in question_lower:
            intent = 'transfer_credit'
        elif 'protect' in question_lower:
            intent = 'meter_protection'
        elif 'error' in question_lower:
            intent = 'error_codes'
        elif 'balance' in question_lower:
            intent = 'check_balance'
        elif 'track' in question_lower:
            intent = 'track_usage'
        elif 'hexing' in question_lower:
            if 'comms failed' in question_lower:
                intent = 'hexing_comms_failed'
            elif 'blank screen' in question_lower:
                intent = 'hexing_blank_screen'
        elif 'refund' in question_lower:
            intent = 'refund'
        elif 'sell electricity' in question_lower:
            intent = 'sell_electricity'
        elif 'xmlvend' in question_lower:
            intent = 'xmlvend'
        elif 'new metering solution' in question_lower:
            intent = 'new_metering_solution'
        elif 'prepaid meters to eskom' in question_lower:
            intent = 'sell_prepaid_meters_to_eskom'
        elif 'installed unit cost' in question_lower:
            intent = 'installed_unit_cost'
        elif 'service area' in question_lower:
            intent = 'service_area'
        elif 'electricity theft' in question_lower:
            intent = 'electricity_theft'
        elif 'customer reaction' in question_lower:
            intent = 'customer_reaction'
        elif 'prepayment decision' in question_lower:
            intent = 'prepayment_decision'
        elif 'reliability' in question_lower:
            intent = 'reliability'
        elif 'tamper detection' in question_lower:
            intent = 'tamper_detection'
        elif 'disposable tokens' in question_lower:
            intent = 'disposable_tokens'
        else:
            intent = 'General'

        # Convert question to IsiZulu
        max_retries = 3
        retry_delay = 5  # seconds
        translated_question = None

        for attempt in range(max_retries):
            try:
                translation_data = {
                "input_text": question,
                "source_lang": "eng_Latn",
                "target_lang": "zul_Latn"
                }
                translated_response = client.translate(translation_data)
                translated_question = translated_response['translation'][0]['translated_text']                
                break
            except VulavulaError as e:
                if attempt < max_retries - 1:
                    print(f"Attempt {attempt + 1} failed with error {e}. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    print(f"Attempt {attempt + 1} failed with error {e}. No more retries left.")
                    # Handle failure case here, e.g., skip translation or log error
                    translated_question = "Translation failed"


        # Create the example translations (for now, just a placeholder example)
        examples = [question, translated_question]

        # Append the formatted entry to the output data
        output_data["faq"].append({
            "intent": intent,
            "examples": examples,
            "answer": answer
        })

    return output_data


def save_faqs_to_json(faqs, filename):
    with open(filename, 'w') as file:
        json.dump(faqs, file, indent=4)
    print(f"Data saved to {filename}")


def main():
        # Load environment variables
    load_dotenv()
    token = os.getenv("VULAVULA_API_TOKEN")


    # Configuration
    url = "https://www.eskom.co.za/prepayment/frequently-asked-questions/"
    output_dir = 'data'
    json_filename = os.path.join(output_dir, 'eskom_faqs.json')
    pdf_filename = os.path.join(output_dir, 'eskom_faqs.pdf')


    # Initialize VulavulaClient
    client = VulavulaClient(token)

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Scrape FAQs
    scraper = FAQScraper(url)
    faqs = scraper.scrape()

    converted_data = convert_faq_data(faqs, client)

    # Export FAQs
    FAQExporter.to_json(converted_data, json_filename)
    # FAQExporter.to_pdf(converted_data, pdf_filename)

    logging.info("FAQ processing completed successfully")

if __name__ == "__main__":
    main()
