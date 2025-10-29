"""Main agent for TuneTrace.AI music analysis and recommendation system."""

import json
import os
import re
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai import types

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    # Try loading from current directory
    load_dotenv()

from tune_trace_ai.prompt import (
    MUSIC_ANALYSIS_RUBRIC,
    OUTPUT_EXAMPLE,
    SYSTEM_PROMPT,
    get_analysis_prompt,
)
from tune_trace_ai.url_finder import add_youtube_urls_to_result


class TuneTraceAgent:
    """
    TuneTrace.AI Agent - Expert musicologist and data analyst.
    
    This agent analyzes songs based on a 20-parameter rubric and provides
    intelligent recommendations including a wildcard suggestion.
    """
    
    def __init__(self, model_name: str = "gemini-2.0-flash-exp"):
        """
        Initialize the TuneTrace.AI agent.
        
        Args:
            model_name: The Gemini model to use for analysis
        """
        api_key = os.environ.get("GOOGLE_API_KEY")
        
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable must be set")
        
        genai.configure(api_key=api_key)
        
        # Configure model with JSON response mode
        generation_config = {
            "temperature": 0.7,
            "response_mime_type": "application/json",
        }
        
        self.model = genai.GenerativeModel(
            model_name,
            generation_config=generation_config
        )
        self.system_instruction = SYSTEM_PROMPT.format(rubric=MUSIC_ANALYSIS_RUBRIC)
        
    def analyze_song(self, song_input: str) -> dict[str, Any]:
        """
        Analyze a song and generate recommendations.
        
        Args:
            song_input: Song name, artist, URL, or any combination
            
        Returns:
            Dictionary containing the complete analysis and recommendations in JSON format
        """
        # Check if input contains multiple songs/URLs
        inputs = self._parse_input(song_input)
        
        if len(inputs) > 1:
            # Handle multiple songs
            results = []
            for single_input in inputs:
                result = self._analyze_single_song(single_input)
                results.append(result)
            return {
                "multiple_songs": True,
                "count": len(results),
                "results": results
            }
        else:
            # Single song analysis
            return self._analyze_single_song(inputs[0])
    
    def _parse_input(self, song_input: str) -> list[str]:
        """Parse the input to handle multiple songs/URLs."""
        # Simple parsing: split by newlines or comma
        if '\n' in song_input:
            inputs = [s.strip() for s in song_input.split('\n') if s.strip()]
        elif ',' in song_input and ('http' in song_input or 'www' in song_input):
            # Multiple URLs separated by comma
            inputs = [s.strip() for s in song_input.split(',') if s.strip()]
        else:
            inputs = [song_input.strip()]
        
        return inputs
    
    def _analyze_single_song(self, song_input: str) -> dict[str, Any]:
        """
        Analyze a single song.
        
        Args:
            song_input: Single song name, artist, or URL
            
        Returns:
            Complete analysis and recommendations
        """
        try:
            # Create the full prompt with system instruction and user input
            full_prompt = f"""{self.system_instruction}

---

Now analyze this song:

{song_input}

Remember to output ONLY valid JSON in the exact format specified, with all 20 parameters and 3 recommendations.
"""
            
            # Generate response
            response = self.model.generate_content(full_prompt)
            
            # Extract JSON from response
            json_result = self._extract_json(response.text)
            
            if json_result:
                # Add YouTube URLs using Python Google Search
                print("\n🔍 Finding YouTube URLs via Google Search...")
                json_result = add_youtube_urls_to_result(json_result)
                return json_result
            else:
                return {
                    "error": "Failed to generate valid JSON output",
                    "raw_response": response.text[:500] if response.text else "No response"
                }
            
        except Exception as e:
            return {
                "error": f"Error during analysis: {str(e)}",
                "input": song_input
            }
    
    def _extract_json(self, text: str) -> dict[str, Any] | None:
        """
        Extract JSON from text response.
        
        Args:
            text: The text containing JSON
            
        Returns:
            Parsed JSON dictionary or None if extraction failed
        """
        if not text:
            return None
            
        try:
            # Try to parse the entire text as JSON
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # Try to find JSON in code blocks
        if "```json" in text:
            try:
                start = text.find("```json") + 7
                end = text.find("```", start)
                json_str = text[start:end].strip()
                return json.loads(json_str)
            except (json.JSONDecodeError, ValueError):
                pass
        
        # Try to find JSON between curly braces
        try:
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                json_str = text[start:end]
                return json.loads(json_str)
        except (json.JSONDecodeError, ValueError):
            pass
        
        return None
    
    def analyze_batch(self, song_list: list[str]) -> dict[str, Any]:
        """
        Analyze multiple songs in batch.
        
        Args:
            song_list: List of song names, artists, or URLs
            
        Returns:
            Dictionary containing all analyses
        """
        results = []
        
        for song_input in song_list:
            result = self._analyze_single_song(song_input)
            results.append({
                "input": song_input,
                "analysis": result
            })
        
        return {
            "batch_analysis": True,
            "count": len(results),
            "results": results
        }


def create_agent(model_name: str = "gemini-2.0-flash-exp") -> TuneTraceAgent:
    """
    Create and return a TuneTrace.AI agent instance.
    
    Args:
        model_name: The Gemini model to use
        
    Returns:
        Initialized TuneTraceAgent instance
    """
    return TuneTraceAgent(model_name=model_name)


def main():
    """Main entry point for testing the agent."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m tune_trace_ai.agent '<song name>' or '<url>'")
        sys.exit(1)
    
    song_input = ' '.join(sys.argv[1:])
    
    print("🎵 TuneTrace.AI - Music Analysis & Recommendation System")
    print("=" * 70)
    print(f"Analyzing: {song_input}")
    print("=" * 70)
    
    agent = create_agent()
    result = agent.analyze_song(song_input)
    
    # Pretty print the result
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
