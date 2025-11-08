"""
Healthcare Assistant - Chat Interface
Interactive chat page with Dr. Cloud
"""
import streamlit as st
from datetime import datetime
import json
import re

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
            # Create session with anonymous user_id
            response = api_client.create_session(user_id='user')

            st.session_state.backend_user_id = response['user_id']
            st.session_state.backend_session_id = response['session_id']
            st.session_state.conversation_started = True

            return True

    except Exception as e:
        st.error(format_error_message(e))
        return False


def is_json_response(text: str) -> bool:
    """
    Check if the response is primarily JSON output

    Args:
        text: Response text to check

    Returns:
        True if the text appears to be JSON, False otherwise
    """
    # Strip whitespace
    text = text.strip()

    # Check for markdown code blocks (```json ... ``` or ``` ... ```)
    markdown_json_pattern = r'```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```'
    markdown_matches = re.findall(markdown_json_pattern, text, re.DOTALL)

    if markdown_matches:
        for match in markdown_matches:
            try:
                json.loads(match.strip())
                # If the code block is substantial and represents most of the response
                if len(match) > 50:
                    return True
            except json.JSONDecodeError:
                continue

    # Check if it starts and ends with JSON markers
    if (text.startswith('{') and text.endswith('}')) or (text.startswith('[') and text.endswith(']')):
        try:
            json.loads(text)
            return True
        except json.JSONDecodeError:
            pass

    # Check if it contains large JSON blocks (even if embedded in text)
    # Look for patterns like {...} or [...] that span multiple lines
    json_pattern = r'(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}|\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\])'
    matches = re.findall(json_pattern, text, re.DOTALL)

    for match in matches:
        try:
            json.loads(match)
            # If the JSON block is substantial (>100 chars) and represents most of the response
            if len(match) > 100 and len(match) / len(text) > 0.7:
                return True
        except json.JSONDecodeError:
            continue

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


def send_message_to_backend(user_message: str, is_followup: bool = False):
    """
    Send message to backend and get response

    Args:
        user_message: User's message text
        is_followup: Whether this is a follow-up to handle JSON response
    """
    # Create session if needed
    if not st.session_state.conversation_started:
        if not create_backend_session():
            return

    # Add user message to chat (only if not a followup)
    if not is_followup:
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

            # Check if response is JSON
            if is_json_response(assistant_response):
                # Don't display the JSON, show that agent is still thinking
                message_placeholder.markdown("🤔 Processing information... Let me explain this in simpler terms.")

                # Automatically send back with layperson prompt
                followup_message = f"Can you explain this to a layperson:\n\n{assistant_response}"

                # Call backend again
                followup_response = api_client.send_message(
                    user_id=st.session_state.backend_user_id,
                    session_id=st.session_state.backend_session_id,
                    message=followup_message
                )

                # Get the explained response
                explained_response = followup_response.get("response", "I apologize, but I couldn't generate a response.")

                # Display the explained response
                message_placeholder.markdown(explained_response)

                # Add the explained response to message history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": explained_response,
                    "timestamp": datetime.now(),
                    "metadata": followup_response.get("metadata", {})
                })

            else:
                # Display normal response
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

    # Initialize session
    initialize_session()

    # Render chat interface
    render_chat_interface()


if __name__ == "__main__":
    main()
