"""
Healthcare Assistant - Chat Interface
Interactive chat page with Dr. Cloud
"""
import streamlit as st
from datetime import datetime

from config.settings import settings
from components.api_client import api_client
from utils.helpers import (
    validate_message,
    get_agent_avatar,
    get_user_avatar,
    format_error_message,
    format_timestamp
)


# Page configuration
st.set_page_config(
    page_title=f"{settings.APP_NAME} - Chat",
    page_icon=settings.PAGE_ICON,
    layout=settings.LAYOUT,
)


def initialize_session():
    """Initialize session state for chat"""
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "backend_session_id" not in st.session_state:
        st.session_state.backend_session_id = None

    if "backend_user_id" not in st.session_state:
        st.session_state.backend_user_id = None

    if "conversation_started" not in st.session_state:
        st.session_state.conversation_started = False


def create_backend_session():
    """Create a new session with the backend"""
    try:
        with st.spinner("Creating new session..."):
            # Create session with username as user_id
            username = st.session_state.get('username', 'anonymous')
            response = api_client.create_session(user_id=username)

            st.session_state.backend_user_id = response['user_id']
            st.session_state.backend_session_id = response['session_id']
            st.session_state.conversation_started = True

            return True

    except Exception as e:
        st.error(format_error_message(e))
        return False


def start_new_conversation():
    """Start a new conversation"""
    # Delete old session if exists
    if st.session_state.backend_session_id:
        api_client.delete_session(
            st.session_state.backend_user_id,
            st.session_state.backend_session_id
        )

    # Reset session state
    st.session_state.messages = []
    st.session_state.backend_session_id = None
    st.session_state.backend_user_id = None
    st.session_state.conversation_started = False

    st.rerun()


def send_message_to_backend(user_message: str):
    """
    Send message to backend and get response

    Args:
        user_message: User's message text
    """
    # Create session if needed
    if not st.session_state.conversation_started:
        if not create_backend_session():
            return

    # Add user message to chat
    st.session_state.messages.append({
        "role": "user",
        "content": user_message,
        "timestamp": datetime.now()
    })

    # Display user message immediately
    with st.chat_message("user", avatar=get_user_avatar()):
        st.markdown(user_message)

    # Get response from backend
    with st.chat_message("assistant", avatar=get_agent_avatar()):
        message_placeholder = st.empty()

        try:
            # Show thinking indicator
            message_placeholder.markdown("🤔 Analyzing your query...")

            # Call backend API
            response = api_client.send_message(
                user_id=st.session_state.backend_user_id,
                session_id=st.session_state.backend_session_id,
                message=user_message
            )

            # Get response text
            assistant_response = response.get("response", "I apologize, but I couldn't generate a response.")

            # Display response
            message_placeholder.markdown(assistant_response)

            # Add to message history
            st.session_state.messages.append({
                "role": "assistant",
                "content": assistant_response,
                "timestamp": datetime.now(),
                "metadata": response.get("metadata", {})
            })

        except Exception as e:
            error_msg = format_error_message(e)
            message_placeholder.markdown(error_msg)

            # Add error to history
            st.session_state.messages.append({
                "role": "assistant",
                "content": error_msg,
                "timestamp": datetime.now(),
                "is_error": True
            })


def render_chat_interface():
    """Render the main chat interface"""

    # Header
    col1, col2 = st.columns([3, 1])

    with col1:
        st.title(f"{get_agent_avatar()} Chat with Dr. Cloud")

    with col2:
        if st.button("🔄 New Conversation", use_container_width=True):
            start_new_conversation()

    # Show disclaimer
    if settings.SHOW_DISCLAIMER and len(st.session_state.messages) == 0:
        st.info(settings.DISCLAIMER_TEXT)

    # Chat message container
    chat_container = st.container()

    with chat_container:
        # Display all messages
        for message in st.session_state.messages:
            role = message["role"]
            content = message["content"]
            avatar = get_user_avatar() if role == "user" else get_agent_avatar()

            with st.chat_message(role, avatar=avatar):
                st.markdown(content)

                # Show timestamp
                if "timestamp" in message:
                    st.caption(f"_{format_timestamp(message['timestamp'])}_")

    # Input area
    st.markdown("---")

    # Chat input
    user_input = st.chat_input(
        "Type your message here... (e.g., 'I have a headache and fever')",
        key="chat_input"
    )

    if user_input:
        # Validate message
        is_valid, error_msg = validate_message(user_input, settings.MAX_MESSAGE_LENGTH)

        if not is_valid:
            st.error(error_msg)
        else:
            # Send message
            send_message_to_backend(user_input)
            st.rerun()

    # Welcome message if no messages
    if len(st.session_state.messages) == 0:
        st.markdown(
            """
            ### 👋 Welcome! I'm Dr. Cloud, your AI healthcare assistant.

            I can help you with:
            - 🩺 Symptom analysis
            - 🧪 Lab result interpretation
            - 💊 Medication information
            - 🏃 Lifestyle recommendations
            - 👨‍⚕️ Specialist referrals

            **How to use:**
            1. Type your health question or symptoms in the box below
            2. Be specific about duration, severity, and any relevant details
            3. I'll analyze your input and provide guidance

            **Example questions:**
            - "I've had a persistent cough and slight fever for 3 days"
            - "Can you explain my cholesterol test results?"
            - "What medications interact with aspirin?"

            ---

            *Remember: This is for informational purposes only and not a replacement for professional medical care.*
            """
        )

    # Sidebar info
    with st.sidebar:
        st.markdown("### 💬 Current Session")

        if st.session_state.conversation_started:
            st.success("✅ Active")
            st.caption(f"Session: {st.session_state.backend_session_id[:8]}...")
            st.caption(f"Messages: {len(st.session_state.messages)}")
        else:
            st.info("No active session")

        st.markdown("---")

        # Tips
        with st.expander("💡 Tips for Better Results"):
            st.markdown(
                """
                - **Be specific** about your symptoms
                - **Mention duration** (e.g., "for 3 days")
                - **Describe severity** (mild, moderate, severe)
                - **Include context** (medications, conditions)
                - **Ask follow-up questions** for clarity
                """
            )

        # Emergency info
        with st.expander("🚨 Emergency Information"):
            st.markdown(
                """
                **Seek immediate medical attention for:**
                - Severe chest pain
                - Difficulty breathing
                - Severe bleeding
                - Loss of consciousness
                - Sudden severe headache
                - Signs of stroke

                **Call emergency services (911) immediately!**
                """
            )


def main():
    """Main chat page logic"""

    # Check authentication
    if not st.session_state.get('authentication_status'):
        st.warning("🔒 Please log in to access the chat.")
        st.stop()

    # Initialize session
    initialize_session()

    # Render chat interface
    render_chat_interface()


if __name__ == "__main__":
    main()
