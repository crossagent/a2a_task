# -*- coding: utf-8 -*-
"""
Defines an example Loop Agent: Detail Collector Loop.

This agent manages an interactive loop to collect necessary details for a task,
typically by coordinating a sub-agent that asks questions and processing user responses.

Relevant ADK Classes:
- google.adk.agents.LoopAgent: Base class for managing the loop logic.
- google.adk.agents.Agent: The sub-agent responsible for generating questions/processing answers.
- google.adk.sessions.Session: Accessing state to check data completeness and store collected info.
- google.adk.events.Event: Receiving user responses, signaling loop continuation/termination.
- google.adk.events.EventActions: Using `escalate=True` to request user input.
"""

from google.adk.agents import LoopAgent, Agent
from google.adk.sessions import Session
from google.adk.events import Event, EventActions
from typing import Optional, Dict, Any

# Placeholder for the Detail Collector Loop Agent definition

class DetailCollectorLoop(LoopAgent):
    """
    Manages an interactive loop to collect task details.

    Coordinates a sub-agent to ask targeted questions until sufficient
    information is gathered, using session state to track progress.
    """
    def __init__(
        self,
        name: str = "DetailCollectorLoop",
        description: str = "Interactively collects necessary task details from the user.",
        sub_agent: Optional[Agent] = None, # Agent that generates questions/processes answers
        state_keys_to_check: Optional[list[str]] = None, # Keys in state indicating completeness
        max_loops: int = 5, # Prevent infinite loops
        **kwargs
    ):
        super().__init__(name=name, description=description, sub_agent=sub_agent, **kwargs)
        self._state_keys_to_check = state_keys_to_check or []
        self._max_loops = max_loops
        self._loop_count = 0

    async def _should_loop(self, last_event: Event, session: Session) -> bool:
        """Determine if the loop should continue."""
        self._loop_count += 1
        if self._loop_count > self._max_loops:
            print(f"[{self.name}] Max loops ({self._max_loops}) reached. Exiting loop.")
            # TODO: Potentially set a state flag indicating incomplete collection
            session.state["temp:detail_collection_status"] = "max_loops_reached"
            return False

        # Check if required state keys are present and non-empty
        if self._state_keys_to_check:
            all_present = True
            for key in self._state_keys_to_check:
                if not session.state.get(key): # Check if key exists and has a value
                    print(f"[{self.name}] State key '{key}' missing or empty. Continuing loop.")
                    all_present = False
                    break
            if all_present:
                print(f"[{self.name}] All required state keys present. Exiting loop.")
                session.state["temp:detail_collection_status"] = "complete"
                return False
        else:
            # If no keys specified, maybe rely on sub-agent signal or user input?
            # For now, loop until max_loops if no keys are defined.
            print(f"[{self.name}] No state keys to check defined. Continuing loop (count: {self._loop_count}).")

        # Default: continue looping if conditions above aren't met
        return True

    async def _prepare_loop_turn(self, last_event: Event, session: Session) -> Optional[EventActions]:
        """Prepare actions for the next loop iteration (e.g., ask user)."""
        print(f"[{self.name}] Preparing loop turn {self._loop_count}.")
        # This is where the sub-agent would typically be invoked to generate
        # the next question based on the current state.
        # For this placeholder, we might just signal escalation to get input.
        # In a real implementation, the sub-agent's response would form the content.

        # Placeholder: Assume we always need user input in this basic loop
        # A real implementation would involve running the sub_agent here.
        print(f"[{self.name}] Escalating to request user input for missing details.")
        return EventActions(escalate=True) # Request user input via Orchestrator

    async def _process_loop_result(self, loop_event: Event, session: Session) -> None:
        """Process the result of the loop turn (e.g., user's answer)."""
        print(f"[{self.name}] Processing loop result.")
        # This is where the sub-agent would process the user's response (loop_event.content)
        # and update the session state accordingly.
        if loop_event.content and loop_event.content.parts:
            user_response = loop_event.content.parts[0].text
            print(f"[{self.name}] Received user response: '{user_response[:100]}...'")
            # TODO: Implement logic to parse response and update state keys
            # Example: session.state['collected_detail_X'] = parsed_value
            session.state[f"temp:last_user_response_in_loop_{self._loop_count}"] = user_response # Store raw response temporarily
        else:
            print(f"[{self.name}] No content found in loop event.")


def create_detail_collector_loop(
    sub_agent: Agent, # The agent doing the asking/processing
    state_keys_to_check: list[str],
    max_loops: int = 5
) -> DetailCollectorLoop:
    """
    Factory function to create the Detail Collector Loop Agent.

    Args:
        sub_agent: The agent responsible for generating questions and processing answers.
        state_keys_to_check: List of keys in session state that indicate completion.
        max_loops: Maximum number of interaction loops allowed.

    Returns:
        An instance of DetailCollectorLoop.
    """
    loop_agent = DetailCollectorLoop(
        sub_agent=sub_agent,
        state_keys_to_check=state_keys_to_check,
        max_loops=max_loops
    )
    print(f"Detail Collector Loop Agent created, checking keys: {state_keys_to_check}")
    return loop_agent

# --- Example Usage (for testing) ---
# if __name__ == '__main__':
#     # Need a dummy sub-agent
#     dummy_questioner = Agent(name="Questioner", description="Asks questions.")
#     loop = create_detail_collector_loop(
#         sub_agent=dummy_questioner,
#         state_keys_to_check=["task_deadline", "task_priority"]
#     )
#     # Add test code here, simulating running the loop via a Runner
#     pass
