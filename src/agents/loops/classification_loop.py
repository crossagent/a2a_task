# -*- coding: utf-8 -*-
"""
Defines an example Loop Agent: Classification Confirmation Loop.

This agent manages an interactive loop to confirm or refine the classification
(e.g., type, priority) of a task or item with the user.

Relevant ADK Classes:
- google.adk.agents.LoopAgent: Base class for managing the loop logic.
- google.adk.agents.Agent: The sub-agent responsible for proposing classification and processing feedback.
- google.adk.sessions.Session: Accessing state for proposed/confirmed classification.
- google.adk.events.Event: Receiving user confirmation/correction.
- google.adk.events.EventActions: Using `escalate=True` to present classification and request feedback.
"""

from google.adk.agents import LoopAgent, Agent
from google.adk.sessions import Session
from google.adk.events import Event, EventActions
from typing import Optional, Dict, Any

# Placeholder for the Classification Confirmation Loop Agent definition

class ClassificationLoop(LoopAgent):
    """
    Manages an interactive loop to confirm task classification with the user.

    Coordinates a sub-agent to propose a classification and processes user
    feedback until confirmation is received or a limit is reached.
    """
    def __init__(
        self,
        name: str = "ClassificationLoop",
        description: str = "Interactively confirms or refines task classification with the user.",
        sub_agent: Optional[Agent] = None, # Agent that proposes classification/processes feedback
        confirmation_key: str = "classification_confirmed", # State key to check for loop exit
        max_loops: int = 3, # Limit refinement attempts
        **kwargs
    ):
        super().__init__(name=name, description=description, sub_agent=sub_agent, **kwargs)
        self._confirmation_key = confirmation_key
        self._max_loops = max_loops
        self._loop_count = 0

    async def _should_loop(self, last_event: Event, session: Session) -> bool:
        """Determine if the loop should continue."""
        self._loop_count += 1
        if self._loop_count > self._max_loops:
            print(f"[{self.name}] Max loops ({self._max_loops}) reached. Exiting loop.")
            # TODO: Set state indicating classification might not be fully confirmed
            session.state["temp:classification_status"] = "max_loops_reached"
            return False

        # Check if the confirmation key is set to True in state
        if session.state.get(self._confirmation_key) is True:
            print(f"[{self.name}] State key '{self._confirmation_key}' is True. Exiting loop.")
            session.state["temp:classification_status"] = "confirmed"
            return False
        else:
            print(f"[{self.name}] State key '{self._confirmation_key}' not True. Continuing loop (count: {self._loop_count}).")
            return True

    async def _prepare_loop_turn(self, last_event: Event, session: Session) -> Optional[EventActions]:
        """Prepare actions for the next loop iteration (e.g., present classification)."""
        print(f"[{self.name}] Preparing loop turn {self._loop_count}.")
        # This is where the sub-agent would run to:
        # 1. Analyze data in state.
        # 2. Propose a classification (or refine based on last_event feedback).
        # 3. Generate text presenting the classification and asking for confirmation/correction.
        # The sub-agent's response content would be used below.

        # Placeholder: Assume sub-agent ran and proposed classification stored in state
        proposed_classification = session.state.get("temp:proposed_classification", "N/A")
        feedback_request = (
            f"Proposed classification: {proposed_classification}. "
            "Please confirm if this is correct, or provide corrections."
        )
        print(f"[{self.name}] Escalating to present classification and request feedback.")
        # Use EventActions to send the message and request input
        # In a real scenario, the content would come from the sub_agent's run result.
        from google.genai.types import Content, Part
        return EventActions(
            escalate=True,
            # content=Content(parts=[Part(text=feedback_request)]) # Ideally set by sub-agent run
        )


    async def _process_loop_result(self, loop_event: Event, session: Session) -> None:
        """Process the user's confirmation or correction."""
        print(f"[{self.name}] Processing loop result (user feedback).")
        # This is where the sub-agent would process the user's response (loop_event.content)
        # to update the classification in the state and potentially set the
        # self._confirmation_key to True if confirmed.
        if loop_event.content and loop_event.content.parts:
            user_feedback = loop_event.content.parts[0].text
            print(f"[{self.name}] Received user feedback: '{user_feedback[:100]}...'")
            # TODO: Implement logic (likely in sub-agent) to parse feedback,
            # update 'temp:proposed_classification' or final classification state key,
            # and set session.state[self._confirmation_key] = True if confirmed.
            # For placeholder, assume confirmation on any response for now:
            if "confirm" in user_feedback.lower() or "yes" in user_feedback.lower():
                 session.state[self._confirmation_key] = True
                 print(f"[{self.name}] User confirmed. Setting '{self._confirmation_key}' to True.")
            else:
                 # Store feedback for sub-agent to refine in next loop turn
                 session.state["temp:classification_feedback"] = user_feedback
                 print(f"[{self.name}] User provided feedback. Loop will continue.")

        else:
            print(f"[{self.name}] No content found in loop event (feedback).")


def create_classification_loop(
    sub_agent: Agent, # The agent proposing classification/processing feedback
    confirmation_key: str = "classification_confirmed",
    max_loops: int = 3
) -> ClassificationLoop:
    """
    Factory function to create the Classification Confirmation Loop Agent.

    Args:
        sub_agent: The agent responsible for proposing/refining classification.
        confirmation_key: The state key indicating user confirmation.
        max_loops: Maximum number of refinement loops allowed.

    Returns:
        An instance of ClassificationLoop.
    """
    loop_agent = ClassificationLoop(
        sub_agent=sub_agent,
        confirmation_key=confirmation_key,
        max_loops=max_loops
    )
    print(f"Classification Loop Agent created, waiting for state key: '{confirmation_key}'")
    return loop_agent

# --- Example Usage (for testing) ---
# if __name__ == '__main__':
#     # Need a dummy sub-agent
#     dummy_classifier = Agent(name="Classifier", description="Proposes classifications.")
#     loop = create_classification_loop(sub_agent=dummy_classifier)
#     # Add test code here
#     pass
