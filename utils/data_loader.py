import json
import streamlit as st
from typing import List, Dict, Any
import pandas as pd

class MockDataLoader:
    def __init__(self):
        self.mock_emails = self._generate_mock_emails()
    
    def _generate_mock_emails(self) -> List[Dict[str, Any]]:
        """Generate realistic mock email data"""
        return [
            {
                "id": 1,
                "sender": "project.manager@company.com",
                "subject": "Weekly Project Update - Urgent Review Needed",
                "body": "Hi team, we need to review the Q4 deliverables by tomorrow. Please prepare your status reports and be ready to discuss blockers. The meeting is scheduled for 10 AM tomorrow.",
                "timestamp": "2024-01-15 09:30:00",
                "read": False,
                "category": None
            },
            {
                "id": 2,
                "sender": "newsletter@technews.com",
                "subject": "Weekly Tech Digest: AI Innovations",
                "body": "This week in AI: New breakthroughs in language models, industry updates, and more. Read about the latest developments in machine learning and artificial intelligence.",
                "timestamp": "2024-01-15 08:15:00",
                "read": True,
                "category": None
            },
            {
                "id": 3,
                "sender": "hr@company.com",
                "subject": "Benefits Enrollment Reminder",
                "body": "Reminder: Open enrollment for health benefits ends this Friday. Please complete your selections in the portal.",
                "timestamp": "2024-01-14 14:20:00",
                "read": False,
                "category": None
            },
            {
                "id": 4,
                "sender": "meeting.request@partner.com",
                "subject": "Meeting Request: Project Collaboration",
                "body": "Would you be available for a 30-minute call next Tuesday to discuss potential collaboration? Please let me know what time works best for you.",
                "timestamp": "2024-01-14 11:45:00",
                "read": False,
                "category": None
            },
            {
                "id": 5,
                "sender": "noreply@system.com",
                "subject": "Your weekly system report",
                "body": "System generated report for the week. No action needed.",
                "timestamp": "2024-01-14 10:00:00",
                "read": True,
                "category": None
            }
        ]
    
    def load_emails(self) -> List[Dict[str, Any]]:
        """Load mock emails"""
        return self.mock_emails
    
    def get_email_by_id(self, email_id: int) -> Dict[str, Any]:
        """Get specific email by ID"""
        for email in self.mock_emails:
            if email['id'] == email_id:
                return email
        return None