"""
Healthcare Assistant - Frontend Application
Main entry point for the healthcare chatbot
"""
import streamlit as st
from config.settings import settings
from components.api_client import api_client


# Page configuration
st.set_page_config(
    page_title=settings.PAGE_TITLE,
    page_icon=settings.PAGE_ICON,
    layout=settings.LAYOUT,
    initial_sidebar_state="auto"
)


def check_backend_health():
    """Check if backend API is accessible"""
    if "backend_health_checked" not in st.session_state:
        with st.spinner("Connecting to healthcare assistant..."):
            is_healthy = api_client.health_check()
            st.session_state.backend_health_checked = True
            st.session_state.backend_healthy = is_healthy

    return st.session_state.get("backend_healthy", True)


def show_main_page():
    """Display the main application page"""

    # Sidebar
    with st.sidebar:
        st.markdown(f"### {settings.PAGE_ICON} {settings.APP_NAME}")
        st.markdown("---")

        # Backend status
        backend_status = "🟢 Connected" if st.session_state.get("backend_healthy", False) else "🔴 Disconnected"
        st.markdown(f"**Backend:** {backend_status}")
        st.caption(f"API: {settings.BACKEND_API_URL}")

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


def main():
    """Main application logic"""
    show_main_page()


if __name__ == "__main__":
    main()
