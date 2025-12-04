
from src.agents.classifier import classify_ticket

def test_classifier_hr():
    res = classify_ticket("Leave request", "I want vacation for 5 days")
    assert res.category == "HR"

def test_classifier_finance():
    res = classify_ticket("Invoice issue", "Payment not received for invoice 123")
    assert res.category == "FINANCE"

def test_classifier_tech_default():
    res = classify_ticket("Laptop broken", "Blue screen of death")
    assert res.category == "TECH"
