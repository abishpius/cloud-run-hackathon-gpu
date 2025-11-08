"""
Healthcare Assistant - Frontend Application
Main entry point with authentication
"""
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from pathlib import Path

from config.settings import settings
from components.api_client import api_client


# Page configuration
st.set_page_config(
    page_title=settings.PAGE_TITLE,
    page_icon=settings.PAGE_ICON,
    layout=settings.LAYOUT,
    initial_sidebar_state="collapsed"
)


def load_config():
    """Load authentication configuration"""
    config_path = Path(settings.USERS_FILE)

    if not config_path.exists():
        st.error(f"Configuration file not found: {settings.USERS_FILE}")
        st.stop()

    with open(config_path) as file:
        config = yaml.load(file, Loader=SafeLoader)

    return config


def check_backend_health():
    """Check if backend API is accessible"""
    if "backend_health_checked" not in st.session_state:
        with st.spinner("Connecting to healthcare assistant..."):
            is_healthy = api_client.health_check()

            if is_healthy:
                st.session_state.backend_health_checked = True
                st.session_state.backend_healthy = True
            else:
                st.session_state.backend_health_checked = True
                st.session_state.backend_healthy = False

    return st.session_state.get("backend_healthy", False)


def show_login_page():
    """Display the login page"""

    # Header
    st.markdown(
        f"""
        <div style="text-align: center; padding: 2rem 0;">
            <h1>{settings.PAGE_ICON} {settings.APP_NAME}</h1>
            <p style="font-size: 1.2rem; color: #666;">{settings.APP_SUBTITLE}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Check backend health
    if not check_backend_health():
        st.error(
            f"⚠️ Unable to connect to the Healthcare Assistant backend at {settings.BACKEND_API_URL}\n\n"
            "Please ensure the backend service is running and accessible."
        )
        st.info(
            "**For local development:**\n"
            "1. Start the backend service: `python main.py`\n"
            "2. Update BACKEND_API_URL in your .env file if needed"
        )
        return

    # Login form container
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("### 🔐 Sign In")

        # Load config and create authenticator
        config = load_config()

        authenticator = stauth.Authenticate(
            config['credentials'],
            config['cookie']['name'],
            config['cookie']['key'],
            config['cookie']['expiry_days']
        )

        # Login widget
        name, authentication_status, username = authenticator.login(
            fields={
                'Form name': 'Login',
                'Username': 'Username',
                'Password': 'Password',
                'Login': 'Sign In'
            }
        )

        # Handle authentication status
        if authentication_status:
            st.session_state['authentication_status'] = True
            st.session_state['name'] = name
            st.session_state['username'] = username
            st.session_state['authenticator'] = authenticator
            st.rerun()

        elif authentication_status == False:
            st.error('❌ Username or password is incorrect')

        elif authentication_status == None:
            st.info('👋 Please enter your credentials')

        # Demo credentials info
        with st.expander("ℹ️ Demo Credentials"):
            st.markdown(
                """
                **For demonstration purposes:**

                - **Username:** `demo`
                - **Password:** `demo123`

                ---

                *In production, use proper authentication (Firebase Auth, OAuth, etc.)*
                """
            )

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: #666; font-size: 0.9rem;">
            <p>Built with Google ADK • Powered by Gemini</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def show_main_page():
    """Display the main application page (after login)"""

    # Sidebar
    with st.sidebar:
        st.markdown(f"### {settings.PAGE_ICON} {settings.APP_NAME}")
        st.markdown(f"**Signed in as:** {st.session_state['name']}")

        st.markdown("---")

        # Navigation info
        st.markdown("### 📑 Pages")
        st.markdown("- 💬 **Chat** - Talk to Dr. Cloud")
        st.markdown("- 📊 **History** - View past conversations (coming soon)")

        st.markdown("---")

        # Backend status
        backend_status = "🟢 Connected" if st.session_state.get("backend_healthy", False) else "🔴 Disconnected"
        st.markdown(f"**Backend:** {backend_status}")
        st.caption(f"API: {settings.BACKEND_API_URL}")

        st.markdown("---")

        # Logout button
        authenticator = st.session_state.get('authenticator')
        if authenticator:
            authenticator.logout('Logout', 'sidebar')

    # Main content
    st.title(f"{settings.PAGE_ICON} Welcome to {settings.APP_NAME}")

    st.markdown(
        f"""
        ### {settings.APP_SUBTITLE}

        Dr. Cloud is an AI-powered healthcare assistant that can help you with:

        - 🩺 **Symptom Analysis** - Get preliminary assessments
        - 🧪 **Lab Results** - Understand your test results
        - 💊 **Medication Information** - Learn about drug interactions
        - 🏃 **Lifestyle Guidance** - Receive personalized recommendations
        - 👨‍⚕️ **Specialist Referrals** - Know when to see a specialist
        - 📋 **Clinical Documentation** - Generate medical notes

        ### 🚀 Getting Started

        Click on **💬 Chat** in the sidebar to start a conversation with Dr. Cloud!

        ---
        """
    )

    # Show disclaimer
    if settings.SHOW_DISCLAIMER:
        st.warning(settings.DISCLAIMER_TEXT)

    # Quick actions
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 💡 Quick Tips")
        st.markdown(
            """
            - Be specific about your symptoms
            - Mention duration and severity
            - Include relevant medical history
            - Ask follow-up questions
            """
        )

    with col2:
        st.markdown("### ⚠️ When to Seek Emergency Care")
        st.markdown(
            """
            - Chest pain or pressure
            - Difficulty breathing
            - Severe bleeding
            - Loss of consciousness
            - **Call emergency services immediately**
            """
        )


def main():
    """Main application logic"""

    # Initialize session state
    if 'authentication_status' not in st.session_state:
        st.session_state['authentication_status'] = None

    # Check authentication
    if st.session_state['authentication_status']:
        show_main_page()
    else:
        show_login_page()


if __name__ == "__main__":
    main()
