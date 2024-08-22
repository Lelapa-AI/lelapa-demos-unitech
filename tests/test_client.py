import unittest
from unittest.mock import patch
from src.lelapa_demos_unitech.client import EskomFAQBot

class TestEskomFAQBot(unittest.TestCase):
    def setUp(self):
        self.bot = EskomFAQBot("mock_token", "mock_eskom_path", "mock_emfuleni_path")

    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data='{"faq": []}')
    def test_load_faq_data(self, mock_open):
        self.bot = EskomFAQBot("mock_token", "mock_eskom_path", "mock_emfuleni_path")
        self.assertEqual(self.bot.faq_data, {"faq": []})

    @patch('vulavula.VulavulaClient.classify')
    def test_answer_question(self, mock_classify):
        mock_classify.return_value = [
            {
                "probabilities": [
                    {"intent": "intent_1", "score": 0.8},
                    {"intent": "intent_2", "score": 0.2}
                ]
            }
        ]
        self.bot.faq_data = {
            "faq": [
                {"intent": "intent_1", "answer": "Answer 1"},
                {"intent": "intent_2", "answer": "Answer 2"}
            ]
        }
        response = self.bot.answer_question("Sample question")
        self.assertEqual(response, "Answer 1")

    @patch('vulavula.VulavulaClient.translate')
    def test_translate_answer(self, mock_translate):
        mock_translate.return_value = {
            "translation": [
                {"translated_text": "Translated answer"}
            ]
        }
        response = self.bot.translate_answer("Original answer", "zul_Latn")
        self.assertEqual(response, "Translated answer")

if __name__ == '__main__':
    unittest.main()