import streamlit as st
import json
import re
from typing import Dict, List, Any, Optional
from utils.llm_services import FreeLLMService
from utils.prompt_manager import PromptManager

class EmailProcessor:
    def __init__(self):
        self.llm_service = FreeLLMService()
        self.prompt_manager = PromptManager()
        
    def process_single_email(self, email: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single email with categorization and action extraction"""
        try:
            # Categorize email
            category = self._categorize_email(email)
            email['category'] = category
            
            # Extract actions for To-Do emails
            if category == "To-Do":
                actions = self._extract_actions(email)
                email['actions'] = actions
            else:
                email['actions'] = []
                
            # Generate summary
            summary = self._summarize_email(email)
            email['summary'] = summary
            
            return email
            
        except Exception as e:
            st.error(f"Error processing email: {e}")
            # Return email with default values
            email['category'] = "Error"
            email['actions'] = []
            email['summary'] = "Failed to process email"
            return email
    
    def _categorize_email(self, email: Dict[str, Any]) -> str:
        """Categorize email using AI"""
        categorization_prompt = self.prompt_manager.get_prompt("categorization")
        
        email_context = f"""
        EMAIL DETAILS:
        From: {email['sender']}
        Subject: {email['subject']}
        Body: {email['body']}
        """
        
        full_prompt = f"{categorization_prompt}\n\n{email_context}"
        
        response = self.llm_service.generate_response(full_prompt, max_length=100)
        
        # Clean up response to get just the category
        category = self._clean_category_response(response)
        return category
    
    def _clean_category_response(self, response: str) -> str:
        """Clean and validate category response"""
        # Extract just the category name
        valid_categories = ["Important", "Newsletter", "Spam", "To-Do"]
        
        # Look for category in response
        for category in valid_categories:
            if category.lower() in response.lower():
                return category
        
        # Fallback logic based on keywords
        response_lower = response.lower()
        if any(word in response_lower for word in ['urgent', 'important', 'critical']):
            return "Important"
        elif any(word in response_lower for word in ['newsletter', 'digest', 'update']):
            return "Newsletter"
        elif any(word in response_lower for word in ['task', 'action', 'todo', 'to-do', 'please']):
            return "To-Do"
        else:
            return "Important"  # Default fallback
    
    def extract_actions(self, email: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract actionable items from email"""
        action_prompt = self.prompt_manager.get_prompt("action_extraction")
        
        email_context = f"""
        EMAIL CONTENT:
        {email['body']}
        """
        
        full_prompt = f"{action_prompt}\n\n{email_context}"
        
        response = self.llm_service.generate_response(full_prompt, max_length=300)
        
        # Parse JSON response or extract actions from text
        actions = self._parse_actions_response(response)
        return actions
    
    def _parse_actions_response(self, response: str) -> List[Dict[str, str]]:
        """Parse actions from LLM response"""
        try:
            # Try to parse as JSON first
            if '{' in response and '}' in response:
                # Extract JSON part
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
                    data = json.loads(json_str)
                    
                    if 'tasks' in data:
                        return data['tasks']
                    elif isinstance(data, list):
                        return data
                    elif isinstance(data, dict):
                        return [data]
        except:
            pass
        
        # Fallback: extract actions from text
        return self._extract_actions_from_text(response)
    
    def _extract_actions_from_text(self, text: str) -> List[Dict[str, str]]:
        """Extract actions from plain text response"""
        actions = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 10:  # Skip short lines
                continue
                
            # Look for task-like patterns
            if any(keyword in line.lower() for keyword in ['task', 'action', 'need to', 'please', 'review', 'prepare']):
                action = {
                    'task': line,
                    'priority': 'medium',
                    'deadline': ''
                }
                
                # Try to extract priority
                if any(word in line.lower() for word in ['urgent', 'asap', 'immediately']):
                    action['priority'] = 'high'
                elif any(word in line.lower() for word in ['when possible', 'at your convenience']):
                    action['priority'] = 'low'
                
                # Try to extract deadline
                deadline_patterns = [
                    r'by (\w+ \d{1,2})',
                    r'due (\w+ \d{1,2})',
                    r'deadline (\w+ \d{1,2})',
                    r'tomorrow',
                    r'next \w+'
                ]
                
                for pattern in deadline_patterns:
                    match = re.search(pattern, line.lower())
                    if match:
                        action['deadline'] = match.group(1).title()
                        break
                
                actions.append(action)
        
        return actions if actions else [{'task': 'Review this email', 'priority': 'medium', 'deadline': ''}]
    
    def summarize_email(self, email: Dict[str, Any]) -> str:
        """Generate email summary"""
        summary_prompt = self.prompt_manager.get_prompt("summarization")
        
        email_context = f"""
        FROM: {email['sender']}
        SUBJECT: {email['subject']}
        BODY: {email['body']}
        """
        
        full_prompt = f"{summary_prompt}\n\n{email_context}"
        
        response = self.llm_service.generate_response(full_prompt, max_length=200)
        return response.strip()
    
    def draft_reply(self, email: Dict[str, Any]) -> str:
        """Draft a reply for the email"""
        reply_prompt = self.prompt_manager.get_prompt("auto_reply")
        
        email_context = f"""
        ORIGINAL EMAIL:
        From: {email['sender']}
        Subject: {email['subject']}
        Body: {email['body']}
        """
        
        full_prompt = f"{reply_prompt}\n\n{email_context}"
        
        response = self.llm_service.generate_response(full_prompt, max_length=300)
        return response.strip()
    
    def process_batch_emails(self, emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process multiple emails at once"""
        processed_emails = []
        for email in emails:
            processed_email = self.process_single_email(email)
            processed_emails.append(processed_email)
        return processed_emails
    
    def get_email_stats(self, emails: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get statistics about processed emails"""
        stats = {
            "total": len(emails),
            "important": 0,
            "newsletter": 0,
            "spam": 0,
            "todo": 0,
            "unprocessed": 0
        }
        
        for email in emails:
            category = email.get('category', 'unprocessed')
            if category in stats:
                stats[category] += 1
            else:
                stats['unprocessed'] += 1
                
        return stats