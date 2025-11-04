"""
Healthcare Assistant - Chat History
View past conversations (Coming Soon)
"""
import streamlit as st

from config.settings import settings


# Page configuration
st.set_page_config(
    page_title=f"{settings.APP_NAME} - History",
    page_icon=settings.PAGE_ICON,
    layout=settings.LAYOUT,
)


def main():
    """Main history page logic"""

    # Check authentication
    if not st.session_state.get('authentication_status'):
        st.warning("🔒 Please log in to access chat history.")
        st.stop()

    # Header
    st.title("📊 Chat History")

    # Coming soon message
    st.info(
        """
        ### 🚧 Coming Soon!

        The chat history feature is currently under development.

        **Planned features:**
        - View all past conversations
        - Search through chat history
        - Export conversations
        - Resume previous sessions
        - Delete old conversations

        For now, your current conversation is saved in the active session.
        Use the "Chat" page to continue your current conversation.
        """
    )

    # Placeholder for future implementation
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            ### 📝 Current Session
            Your active conversation is available in the **Chat** page.

            To start a new conversation, click "New Conversation" in the Chat page.
            """
        )

    with col2:
        st.markdown(
            """
            ### 💾 Data Storage
            In production, conversation history would be:
            - Stored securely in Cloud Firestore
            - Encrypted at rest and in transit
            - Accessible only to the authenticated user
            - Compliant with healthcare data regulations
            """
        )


if __name__ == "__main__":
    main()
