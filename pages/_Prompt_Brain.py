import streamlit as st
import json
from utils.prompt_manager import PromptManager

def main():
    st.title("🧠 Prompt Brain")
    st.markdown("Configure how your AI agent processes emails. Edit the prompts below to change the agent's behavior.")
    
    # Initialize prompt manager
    if 'prompt_manager' not in st.session_state:
        st.session_state.prompt_manager = PromptManager()
    
    # Load current prompts
    prompts = st.session_state.prompt_manager.get_all_prompts()
    
    # Sidebar with controls
    with st.sidebar:
        st.subheader("Prompt Management")
        
        if st.button("🔄 Reload Prompts", use_container_width=True):
            st.session_state.prompt_manager.load_prompts()
            st.rerun()
        
        if st.button("🔄 Reset to Defaults", use_container_width=True):
            st.session_state.prompt_manager.reset_to_defaults()
            st.rerun()
        
        st.markdown("---")
        st.subheader("💡 Prompt Tips")
        st.info("""
        **Best Practices:**
        - Be specific about expected outputs
        - Include examples when possible
        - Define clear categories/rules
        - Specify response format (JSON, text, etc.)
        """)
    
    # Main content - Prompt editing interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📝 Edit Prompts")
        
        # Categorization Prompt
        with st.expander("🎯 Categorization Prompt", expanded=True):
            st.caption("How the AI categorizes emails into: Important, Newsletter, Spam, To-Do")
            categorization_prompt = st.text_area(
                "Categorization Prompt",
                value=prompts.get("categorization", ""),
                height=150,
                key="categorization_editor",
                help="Define how emails should be categorized. Be specific about what makes each category."
            )
            
            # Preview how this prompt works
            if st.button("🧪 Test Categorization", key="test_cat"):
                show_prompt_preview("categorization", categorization_prompt)
        
        # Action Extraction Prompt
        with st.expander("📋 Action Extraction Prompt"):
            st.caption("How the AI extracts tasks and action items from emails")
            action_prompt = st.text_area(
                "Action Extraction Prompt",
                value=prompts.get("action_extraction", ""),
                height=150,
                key="action_editor",
                help="Define how to find tasks, deadlines, and priorities in emails."
            )
            
            if st.button("🧪 Test Action Extraction", key="test_action"):
                show_prompt_preview("action_extraction", action_prompt)
        
        # Summarization Prompt
        with st.expander("📄 Summarization Prompt"):
            st.caption("How the AI summarizes email content")
            summary_prompt = st.text_area(
                "Summarization Prompt",
                value=prompts.get("summarization", ""),
                height=150,
                key="summary_editor",
                help="Define what makes a good email summary - focus on key points and actions."
            )
            
            if st.button("🧪 Test Summarization", key="test_summary"):
                show_prompt_preview("summarization", summary_prompt)
        
        # Auto-Reply Prompt
        with st.expander("↩️ Auto-Reply Prompt"):
            st.caption("How the AI drafts email replies")
            reply_prompt = st.text_area(
                "Auto-Reply Prompt",
                value=prompts.get("auto_reply", ""),
                height=150,
                key="reply_editor",
                help="Define the tone and style for automated email replies."
            )
            
            if st.button("🧪 Test Auto-Reply", key="test_reply"):
                show_prompt_preview("auto_reply", reply_prompt)
    
    with col2:
        st.subheader("💾 Save Changes")
        
        # Save all prompts
        if st.button("💾 Save All Prompts", type="primary", use_container_width=True):
            updates = {
                "categorization": categorization_prompt,
                "action_extraction": action_prompt,
                "summarization": summary_prompt,
                "auto_reply": reply_prompt
            }
            
            st.session_state.prompt_manager.save_prompts(updates)
            st.success("✅ All prompts saved! The AI agent will use these new instructions.")
        
        st.markdown("---")
        st.subheader("📊 Current Configuration")
        
        # Show current prompt stats
        st.metric("Total Prompts", len(prompts))
        
        # Prompt lengths
        st.write("**Prompt Lengths:**")
        for prompt_type, prompt_text in prompts.items():
            length = len(prompt_text)
            emoji = "📏"
            st.write(f"{emoji} {prompt_type}: {length} chars")
        
        st.markdown("---")
        st.subheader("🚀 Quick Templates")
        
        # Quick template buttons
        if st.button("🎯 Strict Categorization", use_container_width=True):
            strict_cat_prompt = """Categorize this email into exactly one category: Important, Newsletter, Spam, or To-Do.

RULES:
- Important: Business-critical, time-sensitive, from key contacts
- Newsletter: Mass emails, subscriptions, non-urgent updates  
- Spam: Promotions, marketing, unsolicited commercial emails
- To-Do: Contains specific requests, action items, or required responses

Respond with ONLY the category name, nothing else."""
            st.session_state.prompt_manager.update_prompt("categorization", strict_cat_prompt)
            st.rerun()
        
        if st.button("📋 Detailed Actions", use_container_width=True):
            detailed_actions_prompt = """Extract ALL actionable items from this email. For each task, identify:

1. The specific action required
2. Deadline (if mentioned)
3. Priority (high/medium/low based on urgency language)
4. Required preparation

Respond in EXACT JSON format:
{
  "tasks": [
    {
      "task": "clear description",
      "deadline": "date or timeframe", 
      "priority": "high/medium/low",
      "notes": "additional context"
    }
  ]
}

If no clear actions, return: {"tasks": []}"""
            st.session_state.prompt_manager.update_prompt("action_extraction", detailed_actions_prompt)
            st.rerun()

def show_prompt_preview(prompt_type: str, prompt_content: str):
    """Show a preview of how the prompt works"""
    st.subheader(f"🔍 {prompt_type.replace('_', ' ').title()} Preview")
    
    # Show the prompt structure
    st.write("**Your Prompt:**")
    st.code(prompt_content, language="text")
    
    # Show example usage
    st.write("**Example Usage:**")
    
    if prompt_type == "categorization":
        example_email = {
            "sender": "manager@company.com",
            "subject": "Urgent: Q4 Report Needed by Friday",
            "body": "Please prepare the Q4 performance report. We need it by Friday EOD for the board meeting."
        }
        st.json(example_email)
        st.write("**Expected Output:** `To-Do`")
    
    elif prompt_type == "action_extraction":
        example_email = "We need the budget review completed by Wednesday. Also, please schedule a team meeting for next week to discuss the new project timeline."
        st.text(example_email)
        st.write("**Expected Output:** JSON with tasks, deadlines, priorities")
    
    elif prompt_type == "summarization":
        example_email = "The quarterly review meeting is scheduled for next Monday at 2 PM. Please bring your department reports and be prepared to discuss Q1 projections. The meeting should take about 2 hours and we'll cover budget allocations for next quarter."
        st.text(example_email)
        st.write("**Expected Output:** Brief 2-3 sentence summary")
    
    elif prompt_type == "auto_reply":
        example_email = "Hi, I'd like to schedule a meeting to discuss the upcoming project. Are you available sometime next week?"
        st.text(example_email)
        st.write("**Expected Output:** Professional, polite reply draft")

# Custom prompt templates
def get_prompt_templates():
    """Return dictionary of prompt templates"""
    return {
        "minimal": {
            "categorization": "Categorize: Important, Newsletter, Spam, To-Do",
            "action_extraction": "Extract tasks as JSON",
            "summarization": "Summarize briefly", 
            "auto_reply": "Draft a polite reply"
        },
        "detailed": {
            "categorization": """Analyze this email and categorize it:

Important: Time-sensitive, business-critical, requires attention
Newsletter: Informational, subscription-based, not urgent  
Spam: Commercial, promotional, irrelevant
To-Do: Contains specific requests or action items

Consider sender, subject, content, and urgency. Respond with one category only.""",
            
            "action_extraction": """Extract all actionable items with details:

For each task identify:
- Specific action required
- Mentioned deadline or timeframe  
- Priority level (high/medium/low)
- Any dependencies or context

Format as JSON with tasks array. If no actions, return empty array.""",
            
            "summarization": """Create a comprehensive yet concise summary:

1. Main purpose of email
2. Key points covered
3. Required actions or decisions
4. Urgency level

Keep to 3-4 sentences maximum.""",
            
            "auto_reply": """Draft a professional email reply:

- Acknowledge receipt
- Address main points
- Set expectations if needed
- Professional closing

Tone: Helpful, professional, clear. Length: 4-5 sentences."""
        }
    }

if __name__ == "__main__":
    main()