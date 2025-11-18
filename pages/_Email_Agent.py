import streamlit as st
import pandas as pd
from utils.data_loader import MockDataLoader
from utils.email_processor import EmailProcessor
from utils.llm_services import FreeLLMService
import json

def main():
    st.title("🤖 Email Agent")
    st.markdown("Chat with your AI assistant to analyze, summarize, and manage your emails.")
    
    # Initialize services
    if 'email_processor' not in st.session_state:
        st.session_state.email_processor = EmailProcessor()
    if 'data_loader' not in st.session_state:
        st.session_state.data_loader = MockDataLoader()
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Check if emails are loaded
    emails_loaded = st.session_state.get('emails_loaded', False)
    emails = st.session_state.get('emails', [])
    
    # Sidebar for email selection
    with st.sidebar:
        st.subheader("📧 Email Selection")
        
        if not emails_loaded:
            st.warning("No emails loaded yet!")
            if st.button("🔄 Load Mock Inbox"):
                with st.spinner("Loading emails..."):
                    emails = st.session_state.data_loader.load_emails()
                    st.session_state.emails = emails
                    st.session_state.emails_loaded = True
                    st.rerun()
        else:
            st.success(f"✅ {len(emails)} emails loaded")
            
            # Email selector
            email_options = {f"{e['id']}: {e['subject']}": e for e in emails}
            selected_email_label = st.selectbox(
                "Choose an email to analyze:",
                options=list(email_options.keys()),
                index=0
            )
            
            selected_email = email_options[selected_email_label]
            st.session_state.selected_email = selected_email
            
            # Show email preview
            st.markdown("---")
            st.subheader("Selected Email")
            st.write(f"**From:** {selected_email['sender']}")
            st.write(f"**Subject:** {selected_email['subject']}")
            st.write(f"**Category:** {selected_email.get('category', 'Not processed')}")
            
            if st.button("📋 Quick Summary"):
                with st.spinner("Generating summary..."):
                    summary = st.session_state.email_processor.summarize_email(selected_email)
                    st.session_state.chat_history.append({
                        "role": "assistant", 
                        "content": f"**Quick Summary:** {summary}"
                    })
                    st.rerun()
    
    # Main chat interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("💬 Chat with Email Agent")
        
        # Display chat history
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.chat_history:
                if message["role"] == "user":
                    st.chat_message("user").write(message["content"])
                else:
                    st.chat_message("assistant").write(message["content"], unsafe_allow_html=True)
        
        # Chat input
        if prompt := st.chat_input("Ask about your emails..."):
            # Add user message to chat
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            
            # Generate agent response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = process_agent_query(prompt, emails, selected_email if emails_loaded else None)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                    st.rerun()
    
    with col2:
        st.subheader("🚀 Quick Actions")
        
        if emails_loaded:
            # Quick action buttons
            if st.button("📊 Inbox Summary", use_container_width=True):
                summary = generate_inbox_summary(emails)
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": f"**Inbox Summary:**\n\n{summary}"
                })
                st.rerun()
            
            if st.button("🎯 Urgent Items", use_container_width=True):
                urgent_emails = [e for e in emails if e.get('category') == 'Important' or e.get('category') == 'To-Do']
                response = f"**Urgent Items Found:** {len(urgent_emails)}\n\n"
                for email in urgent_emails[:5]:  # Show top 5
                    response += f"• {email['subject']} (From: {email['sender']})\n"
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()
            
            if st.button("📋 All Tasks", use_container_width=True):
                all_tasks = []
                for email in emails:
                    if email.get('actions'):
                        all_tasks.extend(email['actions'])
                
                if all_tasks:
                    response = "**All Extracted Tasks:**\n\n"
                    for i, task in enumerate(all_tasks[:10], 1):  # Show top 10
                        response += f"{i}. **{task.get('task', 'Task')}**"
                        if task.get('priority'):
                            response += f" [{task['priority'].upper()}]"
                        if task.get('deadline'):
                            response += f" - Due: {task['deadline']}"
                        response += "\n"
                else:
                    response = "No tasks found in your emails."
                
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()
            
            if st.button("🧹 Cleanup Suggestions", use_container_width=True):
                spam_count = len([e for e in emails if e.get('category') == 'Spam'])
                newsletter_count = len([e for e in emails if e.get('category') == 'Newsletter'])
                
                response = f"**Cleanup Suggestions:**\n\n"
                if spam_count > 0:
                    response += f"• You have {spam_count} spam emails that can be deleted\n"
                if newsletter_count > 0:
                    response += f"• You have {newsletter_count} newsletters that can be archived\n"
                if spam_count == 0 and newsletter_count == 0:
                    response += "Your inbox looks clean! No obvious cleanup needed."
                
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()
        
        st.markdown("---")
        st.subheader("❓ Example Queries")
        st.caption("""
        Try asking:
        - "Summarize this email"
        - "What should I do about this?"
        - "Find all project-related emails" 
        - "Draft a reply to this"
        - "What's urgent in my inbox?"
        """)
        
        # Clear chat button
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

def process_agent_query(query: str, emails: list, selected_email: dict = None) -> str:
    """Process user query and generate response"""
    query_lower = query.lower()
    
    # Handle different types of queries
    if selected_email and any(word in query_lower for word in ['summarize', 'summary', 'overview']):
        return process_summary_query(selected_email)
    
    elif selected_email and any(word in query_lower for word in ['task', 'action', 'todo', 'do']):
        return process_action_query(selected_email)
    
    elif selected_email and any(word in query_lower for word in ['reply', 'respond', 'draft']):
        return process_reply_query(selected_email)
    
    elif any(word in query_lower for word in ['urgent', 'important', 'priority']):
        return process_urgent_query(emails)
    
    elif any(word in query_lower for word in ['all', 'inbox', 'emails']):
        return process_inbox_query(emails)
    
    elif any(word in query_lower for word in ['find', 'search', 'look for']):
        return process_search_query(query, emails)
    
    else:
        # General conversation or email-specific question
        return process_general_query(query, selected_email, emails)

def process_summary_query(email: dict) -> str:
    """Generate summary for specific email"""
    processor = st.session_state.email_processor
    summary = processor.summarize_email(email)
    return f"**Summary of '{email['subject']}':**\n\n{summary}"

def process_action_query(email: dict) -> str:
    """Extract actions from specific email"""
    processor = st.session_state.email_processor
    
    if email.get('actions'):
        actions = email['actions']
    else:
        actions = processor.extract_actions(email)
        email['actions'] = actions  # Cache for future
    
    if actions:
        response = f"**Actions from '{email['subject']}':**\n\n"
        for i, action in enumerate(actions, 1):
            response += f"{i}. **{action.get('task', 'Task')}**"
            if action.get('priority'):
                response += f" - Priority: {action['priority'].upper()}"
            if action.get('deadline'):
                response += f" - Deadline: {action['deadline']}"
            response += "\n"
        return response
    else:
        return f"No specific actions found in '{email['subject']}'. This email may be informational only."

def process_reply_query(email: dict) -> str:
    """Draft a reply for specific email"""
    processor = st.session_state.email_processor
    draft = processor.draft_reply(email)
    return f"**Draft Reply for '{email['subject']}':**\n\n{draft}\n\n*Remember to review and edit before sending!*"

def process_urgent_query(emails: list) -> str:
    """Find urgent emails"""
    urgent_emails = [e for e in emails if e.get('category') in ['Important', 'To-Do']]
    
    if urgent_emails:
        response = "**Urgent/Important Emails:**\n\n"
        for email in urgent_emails[:8]:  # Show top 8
            response += f"• **{email['subject']}** (From: {email['sender']})\n"
            if email.get('summary'):
                response += f"  {email['summary'][:100]}...\n"
            response += "\n"
        return response
    else:
        return "No urgent emails found! Your inbox looks good. 🎉"

def process_inbox_query(emails: list) -> str:
    """Generate inbox overview"""
    stats = st.session_state.email_processor.get_email_stats(emails)
    
    response = "**Inbox Overview:**\n\n"
    response += f"• 📧 Total Emails: {stats['total']}\n"
    response += f"• 🎯 Important: {stats['important']}\n"
    response += f"• 📋 To-Do: {stats['todo']}\n"
    response += f"• 📰 Newsletter: {stats['newsletter']}\n"
    response += f"• 🗑️ Spam: {stats['spam']}\n\n"
    
    # Add some insights
    if stats['todo'] > 3:
        response += "💡 You have several action items. Consider prioritizing them!\n"
    if stats['spam'] > 5:
        response += "💡 You have spam emails that can be cleaned up.\n"
    if stats['important'] == 0 and stats['todo'] == 0:
        response += "💡 Your inbox looks quiet! No urgent items.\n"
    
    return response

def process_search_query(query: str, emails: list) -> str:
    """Search through emails based on query"""
    search_terms = query.lower().replace('find', '').replace('search', '').replace('look for', '').strip()
    
    matching_emails = []
    for email in emails:
        if (search_terms in email['subject'].lower() or 
            search_terms in email['body'].lower() or 
            search_terms in email['sender'].lower()):
            matching_emails.append(email)
    
    if matching_emails:
        response = f"**Found {len(matching_emails)} emails matching '{search_terms}':**\n\n"
        for email in matching_emails[:6]:  # Show top 6
            response += f"• **{email['subject']}** (From: {email['sender']})\n"
            if email.get('category'):
                response += f"  Category: {email['category']}\n"
            response += "\n"
        return response
    else:
        return f"No emails found matching '{search_terms}'. Try different search terms."

def process_general_query(query: str, selected_email: dict, emails: list) -> str:
    """Handle general questions about emails"""
    if selected_email:
        # Question about specific email
        context = f"""
        User is asking about this email:
        Subject: {selected_email['subject']}
        From: {selected_email['sender']}
        Body: {selected_email['body']}
        
        User's question: {query}
        """
        
        llm_service = FreeLLMService()
        response = llm_service.generate_response(f"Answer this question about the email: {context}")
        return f"**Regarding '{selected_email['subject']}':**\n\n{response}"
    else:
        # General question about inbox
        return "I can help you analyze your emails! Please load your inbox first or select a specific email to discuss."

def generate_inbox_summary(emails: list) -> str:
    """Generate comprehensive inbox summary"""
    stats = st.session_state.email_processor.get_email_stats(emails)
    
    summary = f"""📊 **Inbox Analysis Report**

**Email Distribution:**
• Important: {stats['important']} emails
• To-Do: {stats['todo']} action items  
• Newsletters: {stats['newsletter']} subscriptions
• Spam: {stats['spam']} low-priority

**Recommendations:"""
    
    if stats['todo'] > 0:
        summary += f"\n• You have {stats['todo']} actionable items requiring attention"
    
    if stats['spam'] > 3:
        summary += f"\n• Consider cleaning up {stats['spam']} spam emails"
    
    if stats['important'] == 0:
        summary += "\n• No urgent important emails - great!"
    else:
        summary += f"\n• {stats['important']} important emails need review"
    
    return summary

if __name__ == "__main__":
    main()