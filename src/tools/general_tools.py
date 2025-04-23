# -*- coding: utf-8 -*-
"""
Defines general-purpose Tools that can be used by various agents.

Examples include tools for basic text processing, calculations, or simple lookups.

Relevant ADK Classes:
- google.adk.tools.ToolContext: May be used to access session state if needed.
- (These are standard Python functions used *by* Agents).
"""

from google.adk.tools import ToolContext
import datetime

# Placeholder for general tool functions

def get_current_datetime(time_zone: str = "UTC") -> dict:
    """
    Retrieves the current date and time, optionally for a specific timezone.

    Args:
        time_zone (str, optional): The timezone identifier (e.g., 'UTC', 'America/New_York').
                                   Defaults to 'UTC'. Support depends on the system's timezone data.

    Returns:
        dict: A dictionary containing the current date, time, and timezone,
              or an error message.
              Example success: {'status': 'success', 'datetime': '...', 'timezone': 'UTC'}
              Example error: {'status': 'error', 'error_message': 'Invalid timezone'}
    """
    print(f"--- Tool: get_current_datetime called for timezone: {time_zone} ---")
    try:
        # Basic implementation for UTC, needs pytz for full timezone support
        if time_zone.upper() == "UTC":
            now = datetime.datetime.now(datetime.timezone.utc)
            dt_string = now.strftime("%Y-%m-%d %H:%M:%S %Z%z")
            return {"status": "success", "datetime": dt_string, "timezone": "UTC"}
        else:
            # TODO: Implement proper timezone handling using a library like pytz
            return {"status": "error", "error_message": f"Timezone '{time_zone}' not implemented yet. Use UTC."}
    except Exception as e:
        print(f"--- Tool Error: get_current_datetime failed: {e} ---")
        return {"status": "error", "error_message": f"Failed to get datetime: {e}"}

# --- Example Usage (for testing) ---
# if __name__ == '__main__':
#     print(get_current_datetime())
#     print(get_current_datetime(time_zone="America/New_York")) # Expect error unless pytz is added
