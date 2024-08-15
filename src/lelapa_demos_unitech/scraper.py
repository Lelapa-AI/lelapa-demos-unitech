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
        
class FAQCategorizer:
    def __init__(self):
        self.categories = {
            "Customer Questions": {
                "keywords": ["prepayment", "meter", "save money", "electricity"],
                "faqs": []
            },
            "Vending Questions": {
                "keywords": ["sell electricity", "vending", "XMLVend"],
                "faqs": []
            },
            "Meter Manufacturer Questions": {
                "keywords": ["prepaid meters", "reliability", "service area", "theft"],
                "faqs": []
            },
            "Technical Questions": {
                "keywords": ["acronyms", "tamper detection", "tokens"],
                "faqs": []
            }
        }

    def categorize(self, faqs: List[Dict[str, str]]) -> Dict[str, Dict]:
        for faq in faqs:
            categorized = False
            question = faq.get('faq', faq.get('question', ''))  # Try both 'faq' and 'question' keys
            answer = faq.get('faq_response', faq.get('answer', ''))  # Try both 'faq_response' and 'answer' keys
            
            for category, data in self.categories.items():
                if 'keywords' in data and any(keyword.lower() in question.lower() for keyword in data['keywords']):
                    data['faqs'].append({"question": question, "answer": answer})
                    categorized = True
                    break
            
            if not categorized:
                # Add to a general category if not categorized
                if "General Questions" not in self.categories:
                    self.categories["General Questions"] = {"faqs": []}
                self.categories["General Questions"]["faqs"].append({"question": question, "answer": answer})
        
        return self.categories

    def add_manual_questions(self, manual_questions: Dict[str, List[str]]):
        for category, questions in manual_questions.items():
            if category not in self.categories:
                self.categories[category] = {"faqs": []}
            for question in questions:
                self.categories[category]["faqs"].append({
                    "question": question,
                    "answer": "Please contact Eskom support for a detailed answer to this question."
                })


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
    json_filename = os.path.join(output_dir, 'eskom_faqs_categorized.json')
    pdf_filename = os.path.join(output_dir, 'eskom_faqs_categorized.pdf')

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Scrape FAQs
    scraper = FAQScraper(url)
    faqs = scraper.scrape()

    # Categorize FAQs
    categorizer = FAQCategorizer()
    categorized_faqs = categorizer.categorize(faqs)

    # Export FAQs
    FAQExporter.to_json(categorized_faqs, json_filename)
    FAQExporter.to_pdf(categorized_faqs, pdf_filename)

    logging.info("FAQ processing completed successfully")

if __name__ == "__main__":
    main()
