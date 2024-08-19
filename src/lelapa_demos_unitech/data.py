import requests
from bs4 import BeautifulSoup
import json
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from typing import List, Dict
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FAQDATA:
    def __init__(self, url: str):
        self.url = url
    
    def load_faq_data(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                data = f.read()
                # print(data)
                return json.loads(data)
        except json.JSONDecodeError as e:
            logging.error(f"Failed to decode JSON from {file_path}: {e}")
            return []
        except Exception as e:
            logging.error(f"An unexpected error occurred while loading JSON from {file_path}: {e}")
            return []



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



class FAQCategorizer:
    def __init__(self):
        self.categories = {
            "Customer Questions": {
                "keywords": ["prepayment", "meter", "save money", "electricity", "purchase", "balance", "refund"],
                "faqs": []
            },
            "Vending Questions": {
                "keywords": ["sell electricity", "vending", "XMLVend", "token"],
                "faqs": []
            },
            "Meter Manufacturer Questions": {
                "keywords": ["prepaid meters", "reliability", "service area", "theft", "Hexing"],
                "faqs": []
            },
            "Technical Questions": {
                "keywords": ["acronyms", "tamper detection", "tokens", "TID Rollover", "key change"],
                "faqs": []
            },
            "Emfuleni Support": {
                "keywords": ["support", "contact", "WhatsApp", "email", "phone"],
                "faqs": []
            },
            "Emfuleni Meter Operations": {
                "keywords": ["error code", "blank screen", "Comms Failed", "update"],
                "faqs": []
            }
        }

    def categorize(self, faqs: List[Dict[str, str]], faq_type: str = "eskom") -> Dict[str, Dict]:
        for faq in faqs:
            categorized = False
            question = faq.get('faq', faq.get('question', ''))
            answer = faq.get('faq_response', faq.get('answer', ''))
            
            for category, data in self.categories.items():
                if 'keywords' in data and any(keyword.lower() in question.lower() or keyword.lower() in answer.lower() for keyword in data['keywords']):
                    data['faqs'].append({"question": question, "answer": answer})
                    categorized = True
                    break
            
            if not categorized:
                # Add to a general category if not categorized
                general_category = "General Questions" if faq_type == "eskom" else "Emfuleni General Questions"
                if general_category not in self.categories:
                    self.categories[general_category] = {"faqs": []}
                self.categories[general_category]["faqs"].append({"question": question, "answer": answer})
        
        return self.categories

    def add_manual_questions(self, manual_questions: Dict[str, List[str]]):
        for category, questions in manual_questions.items():
            if category not in self.categories:
                self.categories[category] = {"faqs": []}
            for question in questions:
                self.categories[category]["faqs"].append({
                    "question": question,
                    "answer": "Please contact support for a detailed answer to this question."
                })
    
    def merge_faqs(self, emfuleni_faqs, categorized_eskom_faqs):
        # Create a copy of emfuleni_faqs to avoid modifying the original
        combined_faqs = emfuleni_faqs.copy()
        
        # Iterate through the categories in categorized_eskom_faqs
        for category, content in categorized_eskom_faqs.items():
            if category not in combined_faqs:
                # If the category doesn't exist in combined_faqs, add it
                combined_faqs[category] = content
            else:
                # If the category exists, extend the keywords and faqs lists
                combined_faqs[category]['keywords'].extend(content['keywords'])
                combined_faqs[category]['faqs'].extend(content['faqs'])
        
        return combined_faqs


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


def main():
    # Configuration
    url = "https://www.eskom.co.za/prepayment/frequently-asked-questions/"
    output_dir = 'data'
    json_filename = os.path.join(output_dir, 'categorized_faqs.json')
    pdf_filename = os.path.join(output_dir, 'categorized_faqs.pdf')

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Load Emfuleni FAQs from a JSON file
    emfuleni_faq_file_path = os.getenv("EMFULENI_FAQ_FILE_PATH")

    emfuleni_faqs = []
    if emfuleni_faq_file_path:
        faq_data = FAQDATA(url)
        emfuleni_faqs = faq_data.load_faq_data(emfuleni_faq_file_path)
    else:
        logging.error("Environment variable EMFULENI_FAQ_FILE_PATH is not set.")

    # Scrape Eskom FAQs
    scraper = FAQDATA(url)
    eskom_faqs = scraper.scrape()

    # Categorize Eskom FAQs
    categorizer = FAQCategorizer()
    categorized_eskom_faqs = categorizer.categorize(eskom_faqs, faq_type="eskom")

    all_faqs =categorizer.merge_faqs(emfuleni_faqs, categorized_eskom_faqs)

    # Export FAQs
    FAQExporter.to_json(all_faqs, json_filename)
    # FAQExporter.to_pdf(all_faqs, pdf_filename)
    print()
    logging.info("FAQ processing completed successfully")

if __name__ == "__main__":
    main()
