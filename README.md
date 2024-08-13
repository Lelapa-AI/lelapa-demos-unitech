# lelapa-demos-unitech

This project provides an API for querying Eskom FAQs in English, isiZulu, and Sesotho.

## Setup

1. Clone the repository
2. Install PDM if you haven't already: `pip install pdm`
3. Install dependencies: `pdm install`
4. Run the scraper: `pdm run scrape`
5. Start the API: `pdm run start`

## Usage

Send a POST request to `/query_faq` with a JSON body:

```json
{
  "text": "How do I get prepayment electricity?",
  "language": "zu"
}