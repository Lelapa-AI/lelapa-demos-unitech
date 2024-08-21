import json
from vulavula import VulavulaClient
from fuzzywuzzy import process
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve the file path from the environment variable
faq_data_path = os.getenv('FAQ_FILE_PATH')

# Initialize Vulavula client
client = VulavulaClient(os.getenv("VULAVULA_API_TOKEN"))

# Load the JSON data using the path from the .env file
with open(faq_data_path, 'r') as f:
    faq_data = json.load(f)

# Prepare the classification input data
classification_data = {
    "examples": [],
    "inputs": []
}

# Populate the classification data with examples
for item in faq_data['faq']:
    for example in item['examples']:
        classification_data['examples'].append({
            "intent": item['intent'],
            "example": example
        })


# Prompt the user for input to classify
user_input = input("Please enter your query: ")

# Add the user input to the classification data
classification_data['inputs'].append(user_input)


# Classify input
classification_results = client.classify(classification_data)

# Process classification results
probabilities = classification_results[0]['probabilities']
sorted_probs = sorted(probabilities, key=lambda x: x['score'], reverse=True)
print(sorted_probs[0]['intent'])

print(f"Identified intent: {sorted_probs[0]['intent']} with confidence {sorted_probs[0]['score']}")







    # [
    #     {"intent": "prepaid_meter", "example": "What is a prepaid STS meter?"},
    #     {"intent": "prepaid_meter", "example": "Can you explain what a prepaid meter is?"},
    #     {"intent": "prepaid_meter_issues", "example": "Who should I contact if I have issues with my prepaid meter?"},
    #     {"intent": "prepaid_meter_issues", "example": "My prepaid meter is not working, who should I call?"},
    #     {"intent": "purchase_electricity", "example": "How can I purchase electricity for my prepaid meter?"},
    #     {"intent": "purchase_electricity", "example": "Where can I buy electricity tokens?"},
    #     {"intent": "transfer_credit", "example": "Can I transfer my prepaid meter credit to another meter or property?"},
    #     {"intent": "transfer_credit", "example": "Is it possible to transfer credit between prepaid meters?"},
    #     {"intent": "meter_protection", "example": "How can I protect my meter from tampering or theft?"},
    #     {"intent": "meter_protection", "example": "What should I do to prevent my meter from being tampered with?"},
    #     {"intent": "error_codes", "example": "What should I do if my meter displays an error code?"},
    #     {"intent": "error_codes", "example": "My meter shows an error, what does it mean?"},
    #     {"intent": "check_balance", "example": "How can I check my remaining electricity balance?"},
    #     {"intent": "check_balance", "example": "How do I know how much electricity I have left?"},
    #     {"intent": "track_usage", "example": "Can I track my electricity usage over time?"},
    #     {"intent": "track_usage", "example": "Is there a way to monitor my electricity consumption?"},
    #     {"intent": "hexing_comms_failed", "example": "My Hexing meter is displaying a 'Comms Failed' message. What should I do?"},
    #     {"intent": "hexing_comms_failed", "example": "How do I fix a 'Comms Failed' error on my Hexing meter?"},
    #     {"intent": "hexing_blank_screen", "example": "What should I do if my Hexing meter is showing a blank screen?"},
    #     {"intent": "hexing_blank_screen", "example": "My Hexing meter won't turn on, what should I do?"},
    #     {"intent": "refund", "example": "Can I get a refund if I accidentally purchase the wrong amount of electricity?"},
    #     {"intent": "refund", "example": "I bought the wrong amount of electricity, can I get a refund?"},
    #     {"intent": "tid_rollover", "example": "What is the TID Rollover, and why is it important?"},
    #     {"intent": "tid_rollover", "example": "Can you explain the TID Rollover?"},
    #     {"intent": "tid_rollover_process", "example": "How do I perform the TID Rollover on my meter?"},
    #     {"intent": "tid_rollover_process", "example": "How can I update my meter for the TID Rollover?"},
    #     {"intent": "tid_rollover_requirement", "example": "How will I know if my meter needs the TID Rollover update?"},
    #     {"intent": "tid_rollover_requirement", "example": "Does my meter need a TID Rollover?"},
    #     {"intent": "bxc_meters", "example": "Do BXC smart meters require the TID rollover update?"},
    #     {"intent": "bxc_meters", "example": "Is the TID Rollover necessary for BXC smart meters?"},
    #     {"intent": "key_change_tokens", "example": "What are key change tokens, and why am I seeing them on my receipt?"},
    #     {"intent": "key_change_tokens", "example": "Why do I need to enter key change tokens?"},
    #     {"intent": "enter_key_change_tokens", "example": "How do I enter the key change tokens?"},
    #     {"intent": "enter_key_change_tokens", "example": "What's the process to enter key change tokens?"},
    #     {"intent": "use_old_tokens", "example": "Can I use my old credit tokens after the update?"},
    #     {"intent": "use_old_tokens", "example": "Are my old tokens still valid after the TID update?"},
    #     {"intent": "update_success", "example": "How do I know if my meter has been successfully updated?"},
    #     {"intent": "update_success", "example": "How can I confirm my meter update was successful?"},
    #     {"intent": "update_failure", "example": "What should I do if my meter doesn’t accept the key change tokens?"},
    #     {"intent": "update_failure", "example": "My meter rejected the key change tokens, what now?"},
    #     {"intent": "key_change_deadline", "example": "Is there a deadline for using the key change tokens?"},
    #     {"intent": "key_change_deadline", "example": "When is the deadline for entering key change tokens?"},
    #     {"intent": "future_key_change_tokens", "example": "Will I get new key change tokens with every electricity purchase?"},
    #     {"intent": "future_key_change_tokens", "example": "Do I need to enter key change tokens every time I buy electricity?"},
    #     {"intent": "key_change_cost", "example": "Will I be charged for the key change tokens?"},
    #     {"intent": "key_change_cost", "example": "Do I have to pay for key change tokens?"},
    #     {"intent": "rollover_deadline", "example": "What happens if I do not perform the update by the deadline?"},
    #     {"intent": "rollover_deadline", "example": "What are the consequences of missing the TID Rollover deadline?"}
    # ],