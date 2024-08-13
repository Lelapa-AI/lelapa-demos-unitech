import requests
from bs4 import BeautifulSoup
import json
import os

def scrape_eskom_faqs():
    url = "https://www.eskom.co.za/prepayment/frequently-asked-questions/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    faqs = []
    
    # Find all FAQ elements
    faq_elements = soup.find_all('div', class_='eael-accordion-list')
    # print(faq_elements)
    print('-'*10)
    for faq_element in faq_elements:
        # Find the question (heading)
        question_element = faq_element.find('span', class_='eael-accordion-tab-title')
        faq = question_element.text.strip() if question_element else ''

        # Find the response
        answer_element = faq_element.find('div', id=lambda x: x and x.startswith('elementor-tab-content-'))
        answer = answer_element.text.strip() if answer_element else ''
        
        faqs.append({"faq": faq, "faq_response": answer})
    
    return faqs

if __name__ == "__main__":
    if not os.path.exists('data'):
        os.makedirs('data')
    faqs = scrape_eskom_faqs()
    with open('data/eskom_faqs.json', 'w') as f:
        json.dump(faqs, f, indent=2)