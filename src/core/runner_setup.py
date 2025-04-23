# -*- coding: utf-8 -*-
"""
Sets up and configures the ADK Runner and SessionService.

Initializes the core components for running the agent system.

Relevant ADK Classes:
- google.adk.runners.Runner
- google.adk.sessions.SessionService (and its implementations like InMemorySessionService)
"""

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService, SessionService
from google.adk.agents import Agent

# Placeholder for SessionService instance (defaulting to InMemory)
# TODO: Allow configuration for different SessionService types (Database, VertexAI)
session_service: SessionService = InMemorySessionService()

def setup_runner(root_agent: Agent, app_name: str) -> Runner:
    """
    Initializes and returns an ADK Runner instance.

    Args:
        root_agent: The root agent instance for the application.
        app_name: The name of the application.

    Returns:
        An initialized Runner instance.
    """
    print(f"Setting up Runner for app: {app_name} with agent: {root_agent.name}")
    runner = Runner(
        agent=root_agent,
        app_name=app_name,
        session_service=session_service # Use the configured session service
    )
    print("Runner setup complete.")
    return runner

# --- Placeholder for potential SessionService configuration logic ---
# def configure_session_service(config):
#     pass
