# -*- coding: utf-8 -*-
"""
Defines Tools for analysis tasks.

Examples include text classification, keyword extraction, sentiment analysis, etc.
These might be used by the Parser, Classifier, or Expert agents.

Relevant ADK Classes:
- google.adk.tools.ToolContext: May be used to access session state if needed.
- (These are standard Python functions used *by* Agents).
"""

from google.adk.tools import ToolContext
from typing import Dict, Any, List, Optional

# Placeholder for analysis tool functions

def classify_text(text: str, categories: List[str], tool_context: Optional[ToolContext] = None) -> Dict[str, Any]:
    """
    Classifies the input text into one of the provided categories.
    (Placeholder - requires an actual classification model or logic).

    Args:
        text (str): The text to classify.
        categories (List[str]): A list of possible categories.
        tool_context (ToolContext, optional): Provides access to session state.

    Returns:
        dict: Contains 'status' ('success' or 'error'), and either 'classification'
              (the chosen category) or 'error_message'.
    """
    print(f"--- Tool: classify_text called for text: '{text[:50]}...' ---")
    # TODO: Implement actual classification logic (e.g., using an ML model, keyword matching, or another LLM call)
    # Placeholder logic: Just return the first category for now
    if not text or not categories:
        return {"status": "error", "error_message": "Text or categories missing."}

    try:
        # Replace with real classification
        chosen_category = categories[0]
        print(f"--- Tool Success: Classified as '{chosen_category}' (Placeholder) ---")
        return {"status": "success", "classification": chosen_category}
    except Exception as e:
        error_msg = f"Classification failed: {e}"
        print(f"--- Tool Error: {error_msg} ---")
        return {"status": "error", "error_message": error_msg}


def extract_keywords(text: str, max_keywords: int = 5, tool_context: Optional[ToolContext] = None) -> Dict[str, Any]:
    """
    Extracts keywords from the input text.
    (Placeholder - requires an actual keyword extraction algorithm).

    Args:
        text (str): The text to extract keywords from.
        max_keywords (int, optional): The maximum number of keywords to return. Defaults to 5.
        tool_context (ToolContext, optional): Provides access to session state.

    Returns:
        dict: Contains 'status' ('success' or 'error'), and either 'keywords'
              (a list of strings) or 'error_message'.
    """
    print(f"--- Tool: extract_keywords called for text: '{text[:50]}...' ---")
    # TODO: Implement actual keyword extraction logic (e.g., TF-IDF, RAKE, spaCy)
    # Placeholder logic: Split text and take first few words
    if not text:
        return {"status": "error", "error_message": "Input text missing."}

    try:
        # Replace with real extraction
        words = text.lower().split()
        keywords = list(set(words))[:max_keywords] # Very basic placeholder
        print(f"--- Tool Success: Extracted keywords: {keywords} (Placeholder) ---")
        return {"status": "success", "keywords": keywords}
    except Exception as e:
        error_msg = f"Keyword extraction failed: {e}"
        print(f"--- Tool Error: {error_msg} ---")
        return {"status": "error", "error_message": error_msg}

# --- Example Usage (for testing) ---
# if __name__ == '__main__':
#     sample_text = "This is a sample text about task classification and keyword extraction using ADK."
#     categories = ["Technical", "Documentation", "Meeting"]
#     print(classify_text(sample_text, categories))
#     print(extract_keywords(sample_text))
