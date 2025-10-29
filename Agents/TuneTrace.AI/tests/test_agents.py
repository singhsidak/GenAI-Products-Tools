"""Unit tests for TuneTrace.AI agent."""

import json
import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tune_trace_ai.agent import TuneTraceAgent, create_agent
from tune_trace_ai.tools import (
    search_similar_songs,
    search_song_info,
    validate_json_output,
)


class TestTuneTraceAgent:
    """Test cases for TuneTraceAgent."""
    
    @patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"})
    def test_agent_initialization(self):
        """Test agent can be initialized."""
        agent = create_agent()
        assert agent is not None
        assert isinstance(agent, TuneTraceAgent)
        assert agent.model_name == "gemini-2.0-flash-exp"
    
    @patch.dict(os.environ, {}, clear=True)
    def test_agent_requires_api_key(self):
        """Test agent raises error without API key."""
        with pytest.raises(ValueError, match="GOOGLE_API_KEY"):
            TuneTraceAgent()
    
    @patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"})
    def test_parse_input_single(self):
        """Test parsing single song input."""
        agent = create_agent()
        inputs = agent._parse_input("Bohemian Rhapsody by Queen")
        assert len(inputs) == 1
        assert inputs[0] == "Bohemian Rhapsody by Queen"
    
    @patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"})
    def test_parse_input_multiple_newlines(self):
        """Test parsing multiple songs separated by newlines."""
        agent = create_agent()
        inputs = agent._parse_input("Song 1\nSong 2\nSong 3")
        assert len(inputs) == 3
        assert inputs[0] == "Song 1"
        assert inputs[1] == "Song 2"
        assert inputs[2] == "Song 3"
    
    @patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"})
    def test_parse_input_multiple_urls(self):
        """Test parsing multiple URLs separated by commas."""
        agent = create_agent()
        urls = "https://youtube.com/1, https://spotify.com/2"
        inputs = agent._parse_input(urls)
        assert len(inputs) == 2
        assert "youtube.com" in inputs[0]
        assert "spotify.com" in inputs[1]
    
    @patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"})
    def test_extract_json_from_text(self):
        """Test JSON extraction from text."""
        agent = create_agent()
        
        # Test direct JSON
        json_text = '{"key": "value"}'
        result = agent._extract_json(json_text)
        assert result == {"key": "value"}
        
        # Test JSON in code block
        markdown_text = '```json\n{"key": "value"}\n```'
        result = agent._extract_json(markdown_text)
        assert result == {"key": "value"}
        
        # Test JSON surrounded by text
        mixed_text = 'Here is the result: {"key": "value"} end'
        result = agent._extract_json(mixed_text)
        assert result == {"key": "value"}
    
    @patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"})
    def test_extract_json_invalid(self):
        """Test JSON extraction with invalid input."""
        agent = create_agent()
        result = agent._extract_json("This is not JSON")
        assert result is None


class TestTools:
    """Test cases for tools."""
    
    def test_validate_json_output_valid(self):
        """Test validation of valid JSON output."""
        valid_json = json.dumps({
            "disclaimer": "Test",
            "input_song_analysis": {
                "song_name": "Test Song",
                "artist": "Test Artist",
                "parameters": {}
            },
            "recommendations": [
                {"song_name": "Rec 1", "artist": "Artist 1", "rationale": "Because"},
                {"song_name": "Rec 2", "artist": "Artist 2", "rationale": "Because"},
                {"song_name": "Rec 3", "artist": "Artist 3", "rationale": "Because"}
            ]
        })
        
        result = validate_json_output(valid_json)
        assert result["valid"] is True
        assert result["error"] is None
        assert result["data"] is not None
    
    def test_validate_json_output_missing_keys(self):
        """Test validation with missing keys."""
        invalid_json = json.dumps({
            "disclaimer": "Test"
            # Missing input_song_analysis and recommendations
        })
        
        result = validate_json_output(invalid_json)
        assert result["valid"] is False
        assert "Missing required keys" in result["error"]
    
    def test_validate_json_output_invalid_recommendations(self):
        """Test validation with invalid recommendations."""
        invalid_json = json.dumps({
            "disclaimer": "Test",
            "input_song_analysis": {
                "song_name": "Test",
                "artist": "Test",
                "parameters": {}
            },
            "recommendations": [
                {"song_name": "Rec 1"}  # Missing artist and rationale
            ]
        })
        
        result = validate_json_output(invalid_json)
        assert result["valid"] is False
        assert "must have song_name, artist, and rationale" in result["error"]
    
    def test_validate_json_output_malformed(self):
        """Test validation with malformed JSON."""
        result = validate_json_output("not valid json {")
        assert result["valid"] is False
        assert "Invalid JSON" in result["error"]


class TestIntegration:
    """Integration tests (require API key)."""
    
    @pytest.mark.skipif(
        not os.environ.get("GOOGLE_API_KEY"),
        reason="Requires GOOGLE_API_KEY environment variable"
    )
    def test_full_analysis_integration(self):
        """Test full analysis workflow (integration test)."""
        agent = create_agent()
        result = agent.analyze_song("Happy by Pharrell Williams")
        
        # Basic structure checks
        assert isinstance(result, dict)
        
        # Check for either successful analysis or graceful error
        if "error" not in result:
            assert "input_song_analysis" in result or "multiple_songs" in result
    
    @pytest.mark.skipif(
        not os.environ.get("GOOGLE_API_KEY"),
        reason="Requires GOOGLE_API_KEY environment variable"
    )
    def test_batch_analysis_integration(self):
        """Test batch analysis workflow (integration test)."""
        agent = create_agent()
        result = agent.analyze_batch(["Song 1", "Song 2"])
        
        assert isinstance(result, dict)
        assert "batch_analysis" in result
        assert result["count"] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])



