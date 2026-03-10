"""Tools for TuneTrace.AI music analysis system."""

import json
from typing import Any


def validate_json_output(json_str: str) -> dict[str, Any]:
    """
    Validate that the output is proper JSON and contains required fields.
    
    Args:
        json_str: The JSON string to validate
        
    Returns:
        Dictionary with validation results
    """
    try:
        data = json.loads(json_str)
        
        required_keys = ["disclaimer", "input_song_analysis", "recommendations"]
        missing_keys = [key for key in required_keys if key not in data]
        
        if missing_keys:
            return {
                "valid": False,
                "error": f"Missing required keys: {missing_keys}",
                "data": None
            }
        
        # Check input_song_analysis structure
        if "parameters" not in data["input_song_analysis"]:
            return {
                "valid": False,
                "error": "Missing 'parameters' in input_song_analysis",
                "data": None
            }
        
        # Check recommendations structure
        if not isinstance(data["recommendations"], list) or len(data["recommendations"]) != 3:
            return {
                "valid": False,
                "error": "Recommendations must be a list of exactly 3 items",
                "data": None
            }
        
        for rec in data["recommendations"]:
            if not all(key in rec for key in ["song_name", "artist", "rationale"]):
                return {
                    "valid": False,
                    "error": "Each recommendation must have song_name, artist, and rationale",
                    "data": None
                }
        
        return {
            "valid": True,
            "error": None,
            "data": data
        }
        
    except json.JSONDecodeError as e:
        return {
            "valid": False,
            "error": f"Invalid JSON: {str(e)}",
            "data": None
        }
    except Exception as e:
        return {
            "valid": False,
            "error": f"Validation error: {str(e)}",
            "data": None
        }
