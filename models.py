"""Small OOP models used across the application."""
from dataclasses import dataclass
from datetime import datetime

@dataclass
class UserSession:
    user_id: int
    name: str
    username: str
    theme: str = "light"

@dataclass
class Idea:
    idea_id: int
    text: str
    source: str
    created_at: str

@dataclass
class RewardTransaction:
    transaction_id: int
    date: str
    reason: str
    kilograms: float
    points: float
    value_inr: float
