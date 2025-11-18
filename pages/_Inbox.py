import streamlit as st
import pandas as pd
from utils.data_loader import MockDataLoader
from utils.email_processor import EmailProcessor
import time

def main():
    st.title("📥 Email Inbox")
    st.markdown("Load and process your emails with AI-powered categorization")
    
    # Initialize services
    if 'email_processor' not in st.session_state:
        st.session_state.email_processor = EmailProcessor()
    if 'data_loader' not in st.session_state:
        st.session_state.data_loader = MockDataLoader()
    
    # Initialize session state
    if 'emails_loaded' not in st.session_state:
        st.session_state.emails_loaded = False
    if 'selected_email_id' not in st.session_state:
        st.session_state.selected_email_id = None
    
    # Sidebar controls
    with st.sidebar:
        st.header("Inbox Controls")
        
        if st.button("🔄 Load Mock Inbox", use_container_width=True):
            load_mock_inbox()
        
        if st.button("🧠 Process All Emails", use_container_width=True):
            if st.session_state.emails_loaded:
                process_all_emails()
            else:
                st.warning("Please load emails first")
        
        st.markdown("---")
        st.header("Email Stats")
        
        if st.session_state.emails_loaded:
            stats = get_email_stats()
            st.metric("Total Emails", stats['total'])
            st.metric("Unread", stats['unread'])
            st.metric("To-Do", stats['todo'])
    
    # Main content area
    if st.session_state.selected_email_id is not None:
        view_email_details(st.session_state.selected_email_id)
    else:
        display_inbox()

def load_mock_inbox():
    """Load mock email data"""
    with st.spinner("Loading emails..."):
        emails = st.session_state.data_loader.load_emails()
        st.session_state.emails = emails
        st.session_state.emails_loaded = True
        st.success(f"✅ Loaded {len(emails)} emails")

def process_all_emails():
    """Process all emails with AI categorization"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, email in enumerate(st.session_state.emails):
        status_text.text(f"Processing email {i+1}/{len(st.session_state.emails)}...")
        
        # Process email with AI
        processed_email = st.session_state.email_processor.process_single_email(email)
        st.session_state.emails[i] = processed_email
        
        progress_bar.progress((i + 1) / len(st.session_state.emails))
        time.sleep(0.1)
    
    status_text.text("✅ All emails processed!")
    st.rerun()

def get_email_stats():
    """Get email statistics"""
    if not st.session_state.emails_loaded:
        return {'total': 0, 'unread': 0, 'todo': 0}
    
    total = len(st.session_state.emails)
    unread = len([e for e in st.session_state.emails if not e.get('read', False)])
    todo = len([e for e in st.session_state.emails if e.get('category') == 'To-Do'])
    
    return {'total': total, 'unread': unread, 'todo': todo}

def display_inbox():
    """Display the email inbox"""
    if not st.session_state.emails_loaded:
        st.info("👆 Click 'Load Mock Inbox' in the sidebar to get started!")
        return
    
    st.subheader(f"📧 Your Inbox ({len(st.session_state.emails)} emails)")
    
    # Create tabs for different views
    tab1, tab2 = st.tabs(["📋 List View", "📊 Categories"])
    
    with tab1:
        display_email_list()
    
    with tab2:
        display_category_view()

def display_email_list():
    """Display emails in a list format"""
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        categories = ["All Categories"] + list(set([e.get('category', 'Uncategorized') for e in st.session_state.emails]))
        selected_category = st.selectbox("Filter by category:", categories)
    
    with col2:
        status_options = ["All", "Unread", "Read"]
        selected_status = st.selectbox("Filter by status:", status_options)
    
    with col3:
        st.write("")  # Spacer
        if st.button("Clear Filters"):
            st.rerun()
    
    # Filter emails
    filtered_emails = st.session_state.emails.copy()
    
    if selected_category != "All Categories":
        filtered_emails = [e for e in filtered_emails if e.get('category') == selected_category]
    
    if selected_status == "Unread":
        filtered_emails = [e for e in filtered_emails if not e.get('read', False)]
    elif selected_status == "Read":
        filtered_emails = [e for e in filtered_emails if e.get('read', False)]
    
    # Display filtered emails
    if not filtered_emails:
        st.info("No emails match your filters.")
        return
    
    for email in filtered_emails:
        display_email_card(email)

def display_email_card(email):
    """Display a single email as a card"""
    with st.container():
        # Create columns for the email card
        col1, col2, col3, col4 = st.columns([1, 4, 2, 1])
        
        with col1:
            # Read status and category
            status_icon = "📧" if not email.get('read', False) else "✅"
            st.write(status_icon)
            
            category = email.get('category', 'Uncategorized')
            category_emoji = {
                'Important': '🔴',
                'To-Do': '🟡', 
                'Newsletter': '🔵',
                'Spam': '⚫',
                'Uncategorized': '⚪'
            }
            st.write(f"{category_emoji.get(category, '⚪')} {category}")
        
        with col2:
            # Email content
            st.write(f"**{email['subject']}**")
            st.write(f"👤 {email['sender']}")
            st.write(f"🕒 {email['timestamp']}")
        
        with col3:
            # Quick actions
            if email.get('actions'):
                st.write(f"🎯 {len(email['actions'])} actions")
            if email.get('summary'):
                st.write("📋 Has summary")
        
        with col4:
            # View button
            if st.button("View", key=f"view_{email['id']}", use_container_width=True):
                st.session_state.selected_email_id = email['id']
                st.rerun()
        
        st.markdown("---")

def display_category_view():
    """Display emails grouped by category"""
    if not st.session_state.emails_loaded:
        return
    
    categories = {}
    for email in st.session_state.emails:
        category = email.get('category', 'Uncategorized')
        if category not in categories:
            categories[category] = []
        categories[category].append(email)
    
    for category, emails in categories.items():
        with st.expander(f"{category} ({len(emails)} emails)", expanded=True):
            for email in emails:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"**{email['subject']}**")
                    st.write(f"From: {email['sender']}")
                with col2:
                    if st.button("View", key=f"cat_view_{email['id']}"):
                        st.session_state.selected_email_id = email['id']
                        st.rerun()
                st.markdown("---")

def view_email_details(email_id):
    """Display detailed email view"""
    email = next((e for e in st.session_state.emails if e["id"] == email_id), None)
    if not email:
        st.error("Email not found")
        return
    
    # Back button
    if st.button("← Back to Inbox"):
        st.session_state.selected_email_id = None
        st.rerun()
    
    st.subheader("Email Details")
    
    # Email header
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.write(f"**From:** {email['sender']}")
        st.write(f"**Subject:** {email['subject']}")
        st.write(f"**Time:** {email['timestamp']}")
        st.write(f"**Category:** {email.get('category', 'Not processed')}")
    
    with col2:
        # Mark as read/unread
        current_read = email.get('read', False)
        read_text = "Mark as Unread" if current_read else "Mark as Read"
        if st.button(read_text, use_container_width=True):
            email['read'] = not current_read
            st.rerun()
    
    st.markdown("---")
    
    # Email body
    st.subheader("Email Content")
    st.text_area("Body", email['body'], height=200, key="email_body", disabled=True)
    
    st.markdown("---")
    
    # Action buttons
    st.subheader("AI Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📝 Extract Actions", use_container_width=True):
            extract_actions(email)
    
    with col2:
        if st.button("📋 Summarize", use_container_width=True):
            summarize_email(email)
    
    with col3:
        if st.button("↩️ Draft Reply", use_container_width=True):
            draft_reply(email)
    
    with col4:
        if st.button("🔄 Re-categorize", use_container_width=True):
            recategorize_email(email)

def extract_actions(email):
    """Extract action items from email"""
    with st.spinner("Extracting actions..."):
        actions = st.session_state.email_processor.extract_actions(email)
        email['actions'] = actions
    
    st.subheader("🎯 Extracted Actions")
    
    if actions and len(actions) > 0:
        for i, action in enumerate(actions, 1):
            with st.container():
                st.write(f"**{i}. {action.get('task', 'Task')}**")
                
                col1, col2 = st.columns(2)
                with col1:
                    if action.get('priority'):
                        st.write(f"**Priority:** {action['priority'].upper()}")
                with col2:
                    if action.get('deadline'):
                        st.write(f"**Deadline:** {action['deadline']}")
                
                if action.get('notes'):
                    st.write(f"*Note:* {action['notes']}")
                
                st.markdown("---")
    else:
        st.info("No specific actions found in this email.")

def summarize_email(email):
    """Generate email summary"""
    with st.spinner("Generating summary..."):
        summary = st.session_state.email_processor.summarize_email(email)
        email['summary'] = summary
    
    st.subheader("📋 Email Summary")
    st.write(summary)

def draft_reply(email):
    """Draft a reply for email"""
    with st.spinner("Drafting reply..."):
        draft = st.session_state.email_processor.draft_reply(email)
        email['draft_reply'] = draft
    
    st.subheader("📝 Draft Reply")
    st.text_area("Reply Content", draft, height=200, key="draft_reply")
    
    if st.button("💾 Save Draft"):
        if 'saved_drafts' not in st.session_state:
            st.session_state.saved_drafts = []
        
        st.session_state.saved_drafts.append({
            'to': email['sender'],
            'subject': f"Re: {email['subject']}",
            'body': draft,
            'original_email_id': email['id']
        })
        st.success("Draft saved! View in Draft Composer.")

def recategorize_email(email):
    """Re-categorize email"""
    with st.spinner("Re-categorizing..."):
        new_category = st.session_state.email_processor._categorize_email({
            'subject': email['subject'],
            'body': email['body'],
            'sender': email['sender']
        })
        email['category'] = new_category
    
    st.success(f"Email re-categorized as: {new_category}")
    st.rerun()

if __name__ == "__main__":
    main()