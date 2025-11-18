import streamlit as st

st.set_page_config(
    page_title="Email Productivity Agent",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Simple CSS fixes
st.markdown("""
<style>
    .main .block-container {
        padding-top: 1rem;
    }
    .stButton button {
        width: 100%;
    }
    div[data-testid="column"] {
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Simple navigation
st.sidebar.title("📧 Email Agent")
page = st.sidebar.radio(
    "Go to:",
    ["Inbox", "Prompt Brain", "Email Agent", "Draft Composer"]
)

if page == "Inbox":
    st.switch_page("pages/1_Inbox.py")
elif page == "Prompt Brain":
    st.switch_page("pages/2_Prompt_Brain.py") 
elif page == "Email Agent":
    st.switch_page("pages/3_Email_Agent.py")
elif page == "Draft Composer":
    st.switch_page("pages/4_Draft_Composer.py")