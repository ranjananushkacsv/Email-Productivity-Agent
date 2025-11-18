import json
import os
import streamlit as st
from typing import Dict, Any

class PromptManager:
    def __init__(self):
        self.prompts_file = "data/prompts.json"
        self._ensure_prompts_file()
        self.load_prompts()
    
    def _ensure_prompts_file(self):
        """Create prompts file with defaults if it doesn't exist"""
        os.makedirs("data", exist_ok=True)
        
        if not os.path.exists(self.prompts_file):
            default_prompts = {
                "categorization": "Categorize this email into one of these categories: Important, Newsletter, Spam, To-Do. To-Do emails must include a direct request requiring user action. Respond with only the category name.",
                "action_extraction": "Extract actionable tasks from this email. Look for requests, deadlines, and required actions. Respond in JSON format with tasks array containing task, deadline, and priority.",
                "summarization": "Provide a concise 2-3 sentence summary of this email focusing on the main purpose and key points. Highlight any required actions or decisions.",
                "auto_reply": "Draft a polite and professional email reply. Keep it brief (3-4 sentences max), address the main points, and maintain a helpful tone. Do not make promises you can't keep."
            }
            
            with open(self.prompts_file, 'w') as f:
                json.dump(default_prompts, f, indent=2)
    
    def load_prompts(self) -> Dict[str, str]:
        """Load prompts from file"""
        try:
            with open(self.prompts_file, 'r') as f:
                prompts = json.load(f)
                st.session_state.prompts = prompts
                return prompts
        except Exception as e:
            st.error(f"Error loading prompts: {e}")
            return {}
    
    def save_prompts(self, prompts: Dict[str, str]):
        """Save prompts to file"""
        try:
            with open(self.prompts_file, 'w') as f:
                json.dump(prompts, f, indent=2)
            st.session_state.prompts = prompts
            st.success("✅ Prompts saved successfully!")
        except Exception as e:
            st.error(f"Error saving prompts: {e}")
    
    def get_prompt(self, prompt_type: str) -> str:
        """Get a specific prompt"""
        prompts = st.session_state.get('prompts', self.load_prompts())
        return prompts.get(prompt_type, "")
    
    def update_prompt(self, prompt_type: str, new_prompt: str):
        """Update a specific prompt"""
        prompts = st.session_state.get('prompts', self.load_prompts())
        prompts[prompt_type] = new_prompt
        self.save_prompts(prompts)
    
    def get_all_prompts(self) -> Dict[str, str]:
        """Get all prompts"""
        return st.session_state.get('prompts', self.load_prompts())
    
    def reset_to_defaults(self):
        """Reset all prompts to default values"""
        default_prompts = {
            "categorization": "Categorize this email into one of these categories: Important, Newsletter, Spam, To-Do. To-Do emails must include a direct request requiring user action. Respond with only the category name.",
            "action_extraction": "Extract actionable tasks from this email. Look for requests, deadlines, and required actions. Respond in JSON format with tasks array containing task, deadline, and priority.",
            "summarization": "Provide a concise 2-3 sentence summary of this email focusing on the main purpose and key points. Highlight any required actions or decisions.",
            "auto_reply": "Draft a polite and professional email reply. Keep it brief (3-4 sentences max), address the main points, and maintain a helpful tone. Do not make promises you can't keep."
        }
        
        self.save_prompts(default_prompts)
        st.success("✅ Prompts reset to defaults!")