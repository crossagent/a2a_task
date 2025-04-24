# -*- coding: utf-8 -*-
"""
Defines tools for facilitating human-in-the-loop interactions.

Uses LongRunningFunctionTool to pause execution and wait for human input via events.
"""

import uuid
from typing import Any, Dict, Generator, Optional
from google.adk.tools import LongRunningFunctionTool, ToolContext
from google.adk.events import EventActions

# Constants for state keys and event types (adjust as needed)
STATE_DATA_CRITIQUE = "data_collection_critique" # Key holding the critic's output
STATE_HUMAN_RESPONSE = "human_interaction_response" # Key to store the final human response
EVENT_HUMAN_CONFIRMATION_NEEDED = "human_confirmation_needed"
EVENT_HUMAN_INPUT_NEEDED = "human_input_needed"
EVENT_HUMAN_RESPONSE_RECEIVED = "human_response_received" # Event type expected from UI/Orchestrator

def request_human_review_generator(
    critique: Dict[str, str], context: ToolContext
) -> Generator[Dict[str, Any], None, Dict[str, Any]]:
    """
    Generator function for requesting human review or input based on critique.

    Args:
        critique: A dictionary containing 'status' ('complete' or 'incomplete')
                  and 'feedback' from the DataCollectionCriticAgent.
        context: The ToolContext providing access to state and event actions.

    Yields:
        Intermediate status updates (e.g., {"status": "waiting_for_confirmation"}).

    Returns:
        A dictionary containing the human's response (e.g.,
        {"decision": "approved"} or {"supplementary_data": {...}}).
    """
    status = critique.get("status")
    feedback = critique.get("feedback", "No feedback provided.")
    interaction_id = str(uuid.uuid4()) # Unique ID for this interaction

    print(f"Human Interaction Tool: Received critique - Status: {status}, Feedback: {feedback}")

    if status == "complete":
        # Request human confirmation
        print(f"Human Interaction Tool: Requesting confirmation (ID: {interaction_id})")
        EventActions.emit(
            type=EVENT_HUMAN_CONFIRMATION_NEEDED,
            data={
                "interaction_id": interaction_id,
                "message": f"Data review complete. Please confirm:\n\n{feedback}",
                "options": ["Approve", "Reject"] # Example options for UI
            },
            context=context,
        )
        yield {"status": "waiting_for_confirmation", "interaction_id": interaction_id}
        print(f"Human Interaction Tool: Waiting for confirmation response (ID: {interaction_id})")

        # --- Wait for human response event ---
        # This part assumes the Orchestrator or an event handler will catch
        # the EVENT_HUMAN_RESPONSE_RECEIVED event with the user's decision
        # and potentially update the state or trigger the generator's continuation.
        # In a real ADK setup, the framework handles resuming the generator
        # when the corresponding event is processed. For now, we simulate the return.
        # The actual mechanism depends on how event handling is implemented.

        # Placeholder: In a real scenario, the framework would resume here
        # after receiving the EVENT_HUMAN_RESPONSE_RECEIVED event.
        # We'll simulate receiving an 'approved' response for now.
        # The actual response would come from the event data.
        human_decision = "approved" # Simulated response
        print(f"Human Interaction Tool: Received simulated confirmation response: {human_decision} (ID: {interaction_id})")
        return {"decision": human_decision} # Return the decision

    elif status == "incomplete":
        # Request human input
        print(f"Human Interaction Tool: Requesting supplementary input (ID: {interaction_id})")
        EventActions.emit(
            type=EVENT_HUMAN_INPUT_NEEDED,
            data={
                "interaction_id": interaction_id,
                "message": f"Data review found issues. Please provide the missing/corrected information:\n\n{feedback}",
                # UI might present specific fields based on feedback
            },
            context=context,
        )
        yield {"status": "waiting_for_input", "interaction_id": interaction_id}
        print(f"Human Interaction Tool: Waiting for supplementary input (ID: {interaction_id})")

        # --- Wait for human response event ---
        # Similar to the confirmation case, waiting for EVENT_HUMAN_RESPONSE_RECEIVED
        # containing the supplementary data.

        # Placeholder simulation
        supplementary_data = {"deadline": "2025-12-31", "priority": "High"} # Simulated input
        print(f"Human Interaction Tool: Received simulated supplementary input: {supplementary_data} (ID: {interaction_id})")
        return {"supplementary_data": supplementary_data} # Return the input data

    else:
        # Invalid status from critique
        print(f"Human Interaction Tool: Invalid status '{status}' received. Skipping interaction.")
        return {"error": f"Invalid critique status: {status}"}


# Create the LongRunningFunctionTool instance
human_review_tool = LongRunningFunctionTool(
    func=request_human_review_generator,
    name="HumanReviewTool",
    description="Initiates human interaction for data confirmation or supplementation based on prior critique.",
    output_key=STATE_HUMAN_RESPONSE # Save the final human response to state
)

print("Human Interaction Tool (HumanReviewTool) created.")

# --- Example Usage (Conceptual) ---
# In an agent or workflow:
# critique_result = context.state.get(STATE_DATA_CRITIQUE)
# if critique_result:
#    human_response = human_review_tool(critique=critique_result, context=context)
#    # Process human_response based on 'decision' or 'supplementary_data'
