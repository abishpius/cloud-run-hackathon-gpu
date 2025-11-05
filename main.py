"""
Healthcare Assistant FastAPI Backend for Cloud Run

This module provides a FastAPI backend service for the Healthcare Assistant agent system.
It exposes REST endpoints for interacting with the Dr. Cloud Primary Care Agent and its sub-agents.
"""

import os
import uuid
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from google.genai import types
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService

from Healthcare_Assistant.agent import root_agent

# Load environment variables
load_dotenv()

# Configuration
APP_NAME = os.getenv("APP_NAME", "healthcare-assistant-app")
PORT = int(os.getenv("PORT", "8080"))

# Global service instances
session_service: Optional[InMemorySessionService] = None
artifact_service: Optional[InMemoryArtifactService] = None
runner: Optional[Runner] = None


# Pydantic models for request/response
class HealthCheckResponse(BaseModel):
    """Health check response model"""
    status: str = Field(default="healthy", description="Service health status")
    service: str = Field(default="healthcare-assistant", description="Service name")


class NewSessionRequest(BaseModel):
    """Request model for creating a new session"""
    user_id: Optional[str] = Field(default=None, description="User ID (auto-generated if not provided)")
    session_id: Optional[str] = Field(default=None, description="Session ID (auto-generated if not provided)")


class NewSessionResponse(BaseModel):
    """Response model for new session creation"""
    user_id: str = Field(..., description="User ID for this session")
    session_id: str = Field(..., description="Session ID for this conversation")
    message: str = Field(default="Session created successfully", description="Status message")


class ChatMessage(BaseModel):
    """Request model for sending a chat message"""
    user_id: str = Field(..., description="User ID")
    session_id: str = Field(..., description="Session ID")
    message: str = Field(..., description="User message/query")


class ChatResponse(BaseModel):
    """Response model for chat messages"""
    user_id: str
    session_id: str
    response: str
    metadata: Optional[Dict[str, Any]] = None


class SessionStateResponse(BaseModel):
    """Response model for session state"""
    user_id: str
    session_id: str
    state: Dict[str, Any]


class EventStreamItem(BaseModel):
    """Model for streaming event items"""
    type: str = Field(..., description="Event type (e.g., 'thinking', 'response', 'tool_call')")
    content: Optional[str] = Field(default=None, description="Event content/message")
    author: Optional[str] = Field(default=None, description="Event author (agent name)")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional event metadata")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Initializes services on startup and cleans up on shutdown.
    """
    global session_service, artifact_service, runner

    # Startup
    print("Initializing Healthcare Assistant services...")

    # Initialize session and artifact services
    session_service = InMemorySessionService()
    artifact_service = InMemoryArtifactService()

    # Initialize the runner with the root agent
    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
        artifact_service=artifact_service
    )

    print("Healthcare Assistant services initialized successfully!")

    yield

    # Shutdown
    print("Shutting down Healthcare Assistant services...")


# Initialize FastAPI app
app = FastAPI(
    title="Healthcare Assistant API",
    description="REST API for Dr. Cloud Primary Care Agent - A multi-agent healthcare assistant system",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routes
@app.get("/", response_model=HealthCheckResponse)
async def root():
    """Root endpoint - health check"""
    return HealthCheckResponse()


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint for Cloud Run"""
    if runner is None or session_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Services not initialized"
        )
    return HealthCheckResponse()


@app.post("/api/v1/session/new", response_model=NewSessionResponse)
async def create_new_session(request: NewSessionRequest):
    """
    Create a new session for a user.

    - Generates user_id and session_id if not provided
    - Initializes session in the session service
    - Returns session identifiers
    """
    if session_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Session service not initialized"
        )

    # Generate IDs if not provided
    user_id = request.user_id or f"user_{uuid.uuid4().hex[:8]}"
    session_id = request.session_id or f"session_{uuid.uuid4().hex[:8]}"

    # Create session
    session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id
    )

    return NewSessionResponse(
        user_id=user_id,
        session_id=session_id
    )


@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """
    Send a message to the healthcare assistant and get a complete response.

    - Non-streaming endpoint
    - Processes all events and returns final response
    - Auto-creates session if it doesn't exist
    """
    global session_service, artifact_service, runner

    # Initialize services if not already done (handles cold starts)
    if session_service is None:
        session_service = InMemorySessionService()
    if artifact_service is None:
        artifact_service = InMemoryArtifactService()
    if runner is None:
        runner = Runner(
            agent=root_agent,
            app_name=APP_NAME,
            session_service=session_service,
            artifact_service=artifact_service
        )

    try:
        # Always try to create the session (it's safer than checking if it exists)
        try:
            session_service.create_session(
                app_name=APP_NAME,
                user_id=message.user_id,
                session_id=message.session_id
            )
        except Exception:
            # Session might already exist, that's fine
            pass

        # Create user content
        user_content = types.Content(
            role='user',
            parts=[types.Part(text=message.message)]
        )

        # Run agent and collect final response
        final_response = ""
        metadata = {}

        async for event in runner.run_async(
            user_id=message.user_id,
            session_id=message.session_id,
            new_message=user_content
        ):
            # Capture final response
            if event.is_final_response() and event.content and event.content.parts:
                final_response = event.content.parts[0].text

                # Capture any metadata from the event
                if hasattr(event, 'metadata'):
                    metadata = event.metadata

        if not final_response:
            final_response = "I apologize, but I couldn't generate a response. Please try again."

        return ChatResponse(
            user_id=message.user_id,
            session_id=message.session_id,
            response=final_response,
            metadata=metadata
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing message: {str(e)}"
        )


@app.post("/api/v1/chat/stream")
async def chat_stream(message: ChatMessage):
    """
    Send a message to the healthcare assistant and stream the response events.

    - Streaming endpoint using Server-Sent Events (SSE)
    - Returns events as they occur during agent processing
    - Auto-creates session if it doesn't exist
    """
    global session_service, artifact_service, runner

    # Initialize services if not already done (handles cold starts)
    if session_service is None:
        session_service = InMemorySessionService()
    if artifact_service is None:
        artifact_service = InMemoryArtifactService()
    if runner is None:
        runner = Runner(
            agent=root_agent,
            app_name=APP_NAME,
            session_service=session_service,
            artifact_service=artifact_service
        )

    async def event_generator():
        """Generate Server-Sent Events from agent execution"""
        try:
            # Always try to create the session (it's safer than checking if it exists)
            try:
                session_service.create_session(
                    app_name=APP_NAME,
                    user_id=message.user_id,
                    session_id=message.session_id
                )
            except Exception:
                # Session might already exist, that's fine
                pass

            # Create user content
            user_content = types.Content(
                role='user',
                parts=[types.Part(text=message.message)]
            )

            # Stream events from agent
            async for event in runner.run_async(
                user_id=message.user_id,
                session_id=message.session_id,
                new_message=user_content
            ):
                # Extract event information
                event_data = {
                    "type": str(event.type) if hasattr(event, 'type') else "unknown",
                    "author": event.author if hasattr(event, 'author') else None,
                    "content": None,
                    "metadata": {}
                }

                # Extract content if available
                if event.content and event.content.parts:
                    event_data["content"] = event.content.parts[0].text

                # Add is_final flag
                if hasattr(event, 'is_final_response'):
                    event_data["metadata"]["is_final"] = event.is_final_response()

                # Stream the event as JSON
                yield f"data: {EventStreamItem(**event_data).model_dump_json()}\n\n"

            # Send completion signal
            yield f"data: {EventStreamItem(type='complete', content='Stream completed').model_dump_json()}\n\n"

        except Exception as e:
            error_event = EventStreamItem(
                type="error",
                content=f"Error: {str(e)}",
                metadata={"error": str(e)}
            )
            yield f"data: {error_event.model_dump_json()}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@app.get("/api/v1/session/state", response_model=SessionStateResponse)
async def get_session_state(user_id: str, session_id: str):
    """
    Retrieve the current state of a session.

    - Returns all state data stored in the session
    - Useful for debugging and understanding conversation context
    """
    if session_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Session service not initialized"
        )

    try:
        session = session_service.get_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id
        )

        if session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session not found: {session_id}"
            )

        return SessionStateResponse(
            user_id=user_id,
            session_id=session_id,
            state=dict(session.state) if session.state else {}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving session state: {str(e)}"
        )


@app.delete("/api/v1/session")
async def delete_session(user_id: str, session_id: str):
    """
    Delete a session.

    - Removes session data from the session service
    - Use when a conversation is complete or to clean up
    """
    if session_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Session service not initialized"
        )

    try:
        session_service.delete_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id
        )

        return JSONResponse(
            content={
                "message": "Session deleted successfully",
                "user_id": user_id,
                "session_id": session_id
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting session: {str(e)}"
        )


# Run the application
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=PORT,
        reload=True,  # Set to False in production
        log_level="info"
    )
