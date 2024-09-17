import requests
from bs4 import BeautifulSoup
import json
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from typing import List, Dict, Any
import logging
from vulavula import VulavulaClient
from vulavula.common.error_handler import VulavulaError
from dotenv import load_dotenv
import time
import orjson
import aiohttp
import asyncio
from functools import lru_cache
from async_timeout import timeout
import random




# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FAQScraper:
    def __init__(self, url: str):
        self.url = url

    async def scrape(self) -> List[Dict[str, str]]:
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

class FAQProcessor:
    def __init__(self, client: VulavulaClient):
        self.client = client
        self.intent_mapping = self._create_intent_mapping()

    @staticmethod
    def _create_intent_mapping():
        # Create a mapping of keywords to intents
        return {
            'purchase own prepayment meter': 'purchase_own_prepayment_meter',
            'own prepayment meter': 'purchase_own_prepayment_meter',
            'why were prepayment meters installed': 'reason_for_prepayment_meters',
            'reason for prepayment meters': 'reason_for_prepayment_meters',
            'decision to use prepayment metering': 'decision_for_prepayment_metering',
            'go prepayment metering': 'decision_for_prepayment_metering',
            'how do i get prepayment electricity': 'prepayment_electricity_access',
            'get prepayment electricity': 'prepayment_electricity_access',
            'will i save money with prepayment electricity': 'prepayment_electricity_savings',
            'save money with prepayment electricity': 'prepayment_electricity_savings',
            'prepayment meter': 'prepaid_meter',
            'how many prepaid meters': 'prepaid_meters_info',
            'problem': 'prepaid_meter_theft',
            'work': 'prepaid_meter_issues',
            'save money': 'save_money',
            'about electricity': 'electricity_information',
            'sell vending systems': 'sell_vending_systems',
            'purchase': 'purchase_electricity',
            'transfer': 'transfer_credit',
            'protect': 'meter_protection',
            'error': 'error_codes',
            'balance': 'check_balance',
            'track': 'track_usage',
            'hexing comms failed': 'hexing_comms_failed',
            'hexing blank screen': 'hexing_blank_screen',
            'refund': 'refund',
            'sell electricity': 'sell_electricity',
            'what is xmlvend': 'xmlvend_description',
            'why use xmlvend': 'xmlvend_advantages',
            'new metering solution': 'new_metering_solution',
            'prepaid meters to eskom': 'sell_prepaid_meters_to_eskom',
            'installed unit cost': 'installed_unit_cost',
            'service area extreme heat': 'service_area_extreme_heat',
            'service area size': 'service_area_size',
            'service area': 'service_area',
            'electricity theft': 'prepaid_meter_theft_management',
            'report': 'prepaid_meter_fault_report',
            'customer reaction': 'customer_reaction',
            'prepayment decision': 'prepayment_decision',
            'reliability': 'reliability',
            'tamper detection': 'tamper_detection',
            'disposable tokens': 'disposable_tokens',
            'words and acronyms': 'prepaid_meter_terms_and_acronyms',
            'terms and acronyms': 'prepaid_meter_terms_and_acronyms',
            'where do i get my electricity from': 'electricity_source',
            'get electricity': 'electricity_source',
            'sell online vending systems': 'sell_online_vending_systems'
        }
    
    def determine_intent(self, question: str) -> str:
        question_lower = question.lower()
        for key, intent in self.intent_mapping.items():
            if key in question_lower:
                return intent
        return 'general_prepaid_meter'

    @lru_cache(maxsize=128)
    async def translate_text(self, text: str, target_lang: str) -> str:
        max_retries = 5
        retry_delay = 5
        for attempt in range(max_retries):
            try:
                translation_data = {
                    "input_text": text,
                    "source_lang": "eng_Latn",
                    "target_lang": target_lang
                }
                translated_response = self.client.translate(translation_data)
                return translated_response['translation'][0]['translated_text']
            except VulavulaError as e:
                status_code = e.error_data.get('status_code') if hasattr(e, 'error_data') else None
                if status_code == 429:  # Rate limit error
                    retry_delay = min(retry_delay * 2, 60)  # Exponential backoff, capped at 60 seconds
                    logging.info(f"Rate limit hit. Waiting for {retry_delay} seconds before retrying...")
                    await asyncio.sleep(retry_delay)
                elif attempt < max_retries - 1:
                    logging.info(f"Attempt {attempt + 1} failed with error {e}. Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                else:
                    logging.error(f"Attempt {attempt + 1} failed with error {e}. No more retries left.")
                    return "Translation failed"

    async def process_faq(self, entry: Dict[str, str]) -> Dict[str, Any]:
        question = entry['question']
        answer = entry['answer']
        
        intent = self.determine_intent(question)

        # Translate the question into multiple languages
        translated_questions = await asyncio.gather(
            self.translate_text(question, "zul_Latn"),
            self.translate_text(question, "sot_Latn"),
            self.translate_text(question, "afr_Latn")
        )
        examples = [question] + list(translated_questions)

        print("Translated Questions:", translated_questions)

        # Translate the answer into multiple languages
        translated_answers = await asyncio.gather(
            self.translate_text(answer, "zul_Latn"),
            self.translate_text(answer, "sot_Latn"),
            self.translate_text(answer, "afr_Latn")
        )
        print("Translated Answers:", translated_answers)

        answers = [
            {'eng_Latn': answer},
            {'zul_Latn': translated_answers[0]},
            {'sot_Latn': translated_answers[1]},
            {'afr_Latn': translated_answers[2]}
        ]

        return {
            "intent": intent,
            "examples": examples,
            "answer": answers
        }

    async def process_manual_faq(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        intent = entry['intent']
        examples = entry['examples']
        answer = entry['answer']

        async def translate_text_safe(text: str, target_lang: str) -> str:
            try:
                return await self.translate_text(text, target_lang)
            except Exception as e:
                print(f"Translation error for {target_lang}: {str(e)}")
                return f"Translation error: {str(e)}"

        async def ensure_translations(text: str) -> List[Dict[str, str]]:
            languages = ['eng_Latn', 'zul_Latn', 'sot_Latn', 'afr_Latn']
            translations = [{'eng_Latn': text}]
            
            tasks = [translate_text_safe(text, lang.split('_')[0]) for lang in languages[1:]]
            results = await asyncio.gather(*tasks)
            
            for lang, result in zip(languages[1:], results):
                translations.append({lang: result})
            
            return translations

        # Handle examples
        if len(examples) == 1:
            example_translations = await ensure_translations(examples[0])
            examples = [translation[lang] for translation in example_translations for lang in translation]

        # Handle answer
        if isinstance(answer, str):
            answer = await ensure_translations(answer)
        elif isinstance(answer, list) and all(isinstance(item, dict) for item in answer):
            # Check if we have all required translations
            existing_langs = set(lang for item in answer for lang in item.keys())
            required_langs = {'eng_Latn', 'zul_Latn', 'sot_Latn', 'afr_Latn'}
            
            if existing_langs != required_langs:
                # If translations are missing, get the English version and retranslate everything
                eng_text = next((item['eng_Latn'] for item in answer if 'eng_Latn' in item), None)
                if eng_text:
                    answer = await ensure_translations(eng_text)
                else:
                    print("Error: No English text found for retranslation")
        else:
            print("Error: Unexpected answer format")
            answer = [{'eng_Latn': str(answer)}]  # Fallback to string representation

        return {
            "intent": intent,
            "examples": examples,
            "answer": answer
        }

    # async def process_manual_faq(self, entry: Dict[str, Any]) -> Dict[str, Any]:
    #     intent = entry['intent']
    #     examples = entry['examples']
    #     answer = entry['answer']

    #     # Translate examples if they're not already translated
    #     if len(examples) == 1:
    #         translated_examples = await asyncio.gather(
    #             self.translate_text(examples[0], "zul_Latn"),
    #             self.translate_text(examples[0], "sot_Latn"),
    #             self.translate_text(examples[0], "afr_Latn")
    #         )
    #         examples = [examples[0]] + list(translated_examples)

    #     # Check if the answer has already been translated
    #     if isinstance(answer, str):
    #         # If the answer is a string, translate it
    #         translated_answers = await asyncio.gather(
    #             self.translate_text(answer, "zul_Latn"),
    #             self.translate_text(answer, "sot_Latn"),
    #             self.translate_text(answer, "afr_Latn")
    #         )
    #         answer = [
    #             {'eng_Latn': answer},
    #             {'zul_Latn': translated_answers[0]},
    #             {'sot_Latn': translated_answers[1]},
    #             {'afr_Latn': translated_answers[2]}
    #         ]
    #     elif isinstance(answer, list):
    #         # If the answer is already a list of dictionaries, ensure all translations are present
    #         if len(answer) < 4:
    #             missing_translations = [lang for lang in ['eng_Latn', 'zul_Latn', 'sot_Latn', 'afr_Latn'] if not any(lang in a for a in answer)]
    #             eng_answer = next((a['eng_Latn'] for a in answer if 'eng_Latn' in a), None)
    #             if eng_answer:
    #                 new_translations = await asyncio.gather(*(self.translate_text(eng_answer, lang.split('_')[0]) for lang in missing_translations))
    #                 answer.extend({lang: trans} for lang, trans in zip(missing_translations, new_translations))

    #     return {
    #         "intent": intent,
    #         "examples": examples,
    #         "answer": answer
    #     }

    async def convert_faq_data(self, input_data: List[Dict[str, str]], is_manual: bool = False) -> Dict[str, List[Dict[str, Any]]]:
        output_data = {"faq": []}
        
        if is_manual:
            tasks = [self.process_manual_faq(entry) for entry in input_data]
        else:
            tasks = [self.process_faq(entry) for entry in input_data]
        
        processed_faqs = await asyncio.gather(*tasks)
        
        output_data["faq"] = processed_faqs
        return output_data

class RateLimitedClient:
    def __init__(self, client, max_concurrent=5):
        self.client = client
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def translate_text(self, text, target_language, max_retries=5):
        async with self.semaphore:
            for attempt in range(max_retries):
                try:
                    async with timeout(10):  # 10-second timeout
                        return await self.client.translate(text, target_language)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    wait_time = (2 ** attempt) + random.random()
                    print(f"Rate limit hit. Waiting for {wait_time:.2f} seconds before retrying...")
                    await asyncio.sleep(wait_time)


async def main():
        # Load environment variables
    load_dotenv()
    token = os.getenv("VULAVULA_API_TOKEN")


    # Configuration
    url = "https://www.eskom.co.za/prepayment/frequently-asked-questions/"
    output_dir = 'data'
    json_filename = os.path.join(output_dir, 'eskom_faqs.json')
    manual_json_filename = os.path.join(output_dir, 'emfuleni_faqs.json')
    pdf_filename = os.path.join(output_dir, 'eskom_faqs.pdf')
    manual_data_file_path = os.getenv('EMFULENI_FAQ_FILE_PATH')



    # Initialize VulavulaClient
    client = VulavulaClient(token)

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Scrape FAQs
    scraper = FAQScraper(url)
    # faqs = scraper.scrape()
    # faqs = await scraper.scrape()


    # converted_data = convert_faq_data(faqs, client)
    processor = FAQProcessor(client)
    # converted_data = await processor.convert_faq_data(faqs)

    with open(manual_data_file_path, 'r') as f:
        manual_data = json.load(f)

    manual_converted_data = await processor.convert_faq_data(manual_data['faq'], is_manual=True)

    # Export FAQs
    # FAQExporter.to_json(converted_data, json_filename)
    FAQExporter.to_json(manual_converted_data, manual_json_filename)

    # FAQExporter.to_pdf(converted_data, pdf_filename)

    logging.info("FAQ processing completed successfully")

if __name__ == "__main__":
    # main()
    asyncio.run(main())

