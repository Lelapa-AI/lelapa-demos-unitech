# tests/test_main.py
import os
import json
from fastapi.testclient import TestClient
from src.lelapa_demos_unitech.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Emfuleni FAQ API"}

def test_answer_question_eng():
    query = {
                "question": "What is a prepaid STS meter?", 
                "language": "eng_Latn"
            }
    response = client.post("/faq", json=query)
    assert response.status_code == 200
    assert "A prepaid STS (Standard Transfer Specification) meter is a device used to allow customers to pay for electricity in advance." in response.json()["answer"]
    assert "This system lets customers purchase electricity tokens that are then entered into the meter to get electricity." in response.json()["answer"]
    assert "The STS meters help customers manage their electricity usage and avoid unexpected bills." in response.json()["answer"]

def test_answer_question_zul():
    query = {"question": "Yini i-prepaid STS meter?", "language": "zul_Latn"}
    response = client.post("/faq", json=query)
    assert response.status_code == 200
    # Add the translated answer for Zulu language
    assert response.json()["answer"] == "Isikali se-STS esikhokhelwa kusengaphambili (Standard Transfer Specification) iyimishini esetshenziselwa ukuvumela amakhasimende ukuba akhokhe ugesi kusengaphambili Lolu hlelo luvumela amakhasimende ukuba athenge amathokheni kagesi abese efakwa kumitha ukuze athole ugesi Amamitha e-STS asiza amakhasimende ukuba aphathe ukusetshenziswa kwawo kukagesi futhi agweme izikweletu ezingalindelekile"

def test_answer_question_unsupported_language():
    query = {"question": "What is a prepaid STS meter?", "language": "say_Latn"}
    response = client.post("/faq", json=query)
    assert response.status_code == 200
    print(response.json())
    assert response.json()["detail"] == "Language not accommodated."

def test_answer_question_no_language():
    query = {"question": "What is a prepaid STS meter?"}
    response = client.post("/faq", json=query)
    assert response.status_code == 200
    assert response.json()["answer"] == "A prepaid STS (Standard Transfer Specification) meter is a device used to allow customers to pay for electricity in advance. This system lets customers purchase electricity tokens that are then entered into the meter to get electricity. The STS meters help customers manage their electricity usage and avoid unexpected bills."

def test_answer_question_invalid_input():
    query = {"question": "", "language": "eng_Latn"}
    response = client.post("/faq", json=query)
    assert response.status_code == 200
    assert response.json()["detail"] == "Question field required"

def test_answer_question_missing_input():
    query = {}
    response = client.post("/faq", json=query)
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "field required"