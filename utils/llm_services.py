import streamlit as st
import json
import re
import random
from typing import Dict, List, Any

class FreeLLMService:
    def __init__(self):
        self.model_loaded = True  # Always available
    
    def generate_response(self, prompt: str, max_length: int = 500) -> str:
        """Smart pattern-based response generator"""
        return self._smart_pattern_matcher(prompt)
    
    def _smart_pattern_matcher(self, prompt: str) -> str:
        """Advanced pattern matching without any AI dependencies"""
        prompt_lower = prompt.lower()
        email_content = self._extract_email_content(prompt)
        
        # Categorization
        if "categorize" in prompt_lower:
            return self._categorize_email(email_content)
        
        # Action extraction
        elif "extract" in prompt_lower and "action" in prompt_lower:
            return self._extract_actions(email_content)
        
        # Summarization
        elif "summarize" in prompt_lower:
            return self._summarize_email(email_content)
        
        # Reply drafting
        elif "reply" in prompt_lower or "draft" in prompt_lower:
            return self._draft_reply(email_content)
        
        return "I've processed your email request successfully."
    
    def _extract_email_content(self, prompt: str) -> Dict[str, str]:
        """Extract email components from prompt"""
        content = {
            "sender": "",
            "subject": "", 
            "body": "",
            "full_text": prompt
        }
        
        # Extract sender
        sender_match = re.search(r'FROM:\s*([^\n]+)', prompt, re.IGNORECASE)
        if sender_match:
            content["sender"] = sender_match.group(1).strip()
        
        # Extract subject
        subject_match = re.search(r'SUBJECT:\s*([^\n]+)', prompt, re.IGNORECASE)
        if subject_match:
            content["subject"] = subject_match.group(1).strip()
        
        # Extract body
        body_match = re.search(r'BODY:\s*(.+)', prompt, re.DOTALL | re.IGNORECASE)
        if body_match:
            content["body"] = body_match.group(1).strip()
        else:
            # If no structured format, use the whole prompt as body
            content["body"] = prompt
        
        return content
    
    def _categorize_email(self, email: Dict[str, str]) -> str:
        """Advanced email categorization using patterns"""
        text = (email.get('subject', '') + ' ' + email.get('body', '')).lower()
        sender = email.get('sender', '').lower()
        
        # Urgent keywords
        urgent_words = ['urgent', 'asap', 'immediately', 'deadline', 'important', 'critical']
        if any(word in text for word in urgent_words):
            return "Important"
        
        # Action keywords
        action_words = ['please', 'need', 'request', 'action required', 'todo', 'task', 'required', 'must']
        if any(word in text for word in action_words):
            return "To-Do"
        
        # Newsletter keywords
        newsletter_words = ['newsletter', 'digest', 'weekly update', 'monthly report', 'subscription']
        if any(word in text for word in newsletter_words):
            return "Newsletter"
        
        # Spam keywords
        spam_words = ['promotion', 'special offer', 'discount', 'buy now', 'limited time', 'click here']
        if any(word in text for word in spam_words):
            return "Spam"
        
        # Sender-based categorization
        if any(domain in sender for domain in ['@company.com', '@corp.com', 'manager', 'hr@']):
            return "Important"
        if any(domain in sender for domain in ['newsletter@', 'digest@', 'updates@']):
            return "Newsletter"
        
        return "Important"  # Default
    
    def _extract_actions(self, email: Dict[str, str]) -> str:
        """Extract actions using pattern matching"""
        text = email.get('body', '')
        tasks = []
        
        # Pattern 1: Direct requests with "please"
        please_matches = re.findall(r'please\s+([^.!?]+[.!?])', text, re.IGNORECASE)
        for match in please_matches:
            tasks.append({
                "task": self._clean_task_text(match),
                "priority": self._determine_priority(text),
                "deadline": self._extract_deadline(text)
            })
        
        # Pattern 2: "Need to" statements
        need_matches = re.findall(r'(?:need to|should|must)\s+([^.!?]+[.!?])', text, re.IGNORECASE)
        for match in need_matches:
            tasks.append({
                "task": self._clean_task_text(match),
                "priority": self._determine_priority(text),
                "deadline": self._extract_deadline(text)
            })
        
        # Pattern 3: Action items with bullets or numbers
        bullet_matches = re.findall(r'[-•*]\s*([^\n.!?]+[.!?])', text)
        for match in bullet_matches:
            tasks.append({
                "task": self._clean_task_text(match),
                "priority": "medium",
                "deadline": ""
            })
        
        if not tasks:
            tasks.append({
                "task": "Review this email for important information",
                "priority": "medium",
                "deadline": ""
            })
        
        return json.dumps({"tasks": tasks[:3]})  # Limit to 3 tasks
    
    def _clean_task_text(self, text: str) -> str:
        """Clean and format task text"""
        text = text.strip()
        if text and text[0].islower():
            text = text[0].upper() + text[1:]
        return text
    
    def _determine_priority(self, text: str) -> str:
        """Determine task priority from text"""
        text_lower = text.lower()
        if any(word in text_lower for word in ['urgent', 'asap', 'immediately', 'critical']):
            return "high"
        elif any(word in text_lower for word in ['when possible', 'at your convenience', 'no rush']):
            return "low"
        else:
            return "medium"
    
    def _extract_deadline(self, text: str) -> str:
        """Extract deadlines from text"""
        patterns = [
            r'by\s+(\w+\s+\d{1,2})',
            r'due\s+(\w+\s+\d{1,2})',
            r'deadline\s+(\w+\s+\d{1,2})',
            r'tomorrow',
            r'next\s+\w+',
            r'this\s+\w+',
            r'by\s+EOD',
            r'by\s+end\s+of\s+day'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                deadline = match.group(1) if match.groups() else match.group(0)
                return deadline.title()
        
        return ""
    
    def _summarize_email(self, email: Dict[str, str]) -> str:
        """Generate intelligent email summary"""
        subject = email.get('subject', '')
        body = email.get('body', '')
        
        # Key phrase extraction
        key_phrases = []
        
        # Meeting-related
        if any(word in body.lower() for word in ['meeting', 'call', 'discuss', 'schedule']):
            key_phrases.append("scheduling or discussion")
        
        # Document-related
        if any(word in body.lower() for word in ['report', 'document', 'review', 'submit']):
            key_phrases.append("document review or submission")
        
        # Project-related
        if any(word in body.lower() for word in ['project', 'task', 'assignment', 'work']):
            key_phrases.append("project work or tasks")
        
        # Question-related
        if any(word in body.lower() for word in ['question', 'query', 'advice', 'help']):
            key_phrases.append("questions or advice needed")
        
        # Build summary
        if key_phrases:
            summary = f"This email about '{subject}' involves {', '.join(key_phrases)}. "
        else:
            summary = f"This email '{subject}' requires your attention. "
        
        # Add urgency context
        if any(word in body.lower() for word in ['urgent', 'asap', 'immediately']):
            summary += "It appears to be time-sensitive and should be addressed promptly."
        else:
            summary += "Please review it when you have time."
        
        return summary
    
    def _draft_reply(self, email: Dict[str, str]) -> str:
        """Draft context-aware email replies"""
        subject = email.get('subject', '')
        body = email.get('body', '')
        
        # Different reply templates based on content
        if any(word in body.lower() for word in ['meeting', 'schedule', 'call']):
            template = """Thank you for reaching out about scheduling. 

I'd be happy to connect. Please let me know what times work best for you next week.

Looking forward to our discussion."""
        
        elif any(word in body.lower() for word in ['question', 'help', 'advice']):
            template = """Thank you for your question.

I'll look into this and get back to you with more information shortly.

Best regards"""
        
        elif any(word in body.lower() for word in ['urgent', 'asap', 'immediately']):
            template = """Thank you for your urgent message.

I've received this and will prioritize reviewing it. I'll follow up with you soon.

Best regards"""
        
        else:
            template = """Thank you for your email.

I have received your message and will review it shortly. I'll get back to you with a proper response.

Best regards"""
        
        return template