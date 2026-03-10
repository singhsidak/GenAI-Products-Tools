# 🚀 TuneTrace.AI Quick Start Guide

Get up and running with TuneTrace.AI in under 5 minutes!

## Prerequisites

- Python 3.10+
- Google API Key ([Get one here](https://aistudio.google.com/app/apikey))

## Installation

```bash
# Navigate to the TuneTrace.AI directory
cd TuneTrace.AI

# Install the package
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

## Configuration

```bash
# Set your Google API key
export GOOGLE_API_KEY="your-api-key-here"

# Optional: Copy and customize environment file
cp env.example .env
# Edit .env with your preferred settings
```

## Basic Usage

### 1. Command Line

```bash
# Analyze a song by name and artist
python -m tune_trace_ai.agent "Lose Yourself by Eminem"

# Analyze from a URL
python -m tune_trace_ai.agent "https://www.youtube.com/watch?v=_Yhyp-_hX2s"

# Multiple songs (separate by newlines)
python -m tune_trace_ai.agent "Song 1
Song 2
Song 3"
```

### 2. Python Code

```python
from tune_trace_ai import create_agent
import json

# Create the agent
agent = create_agent()

# Analyze a song
result = agent.analyze_song("Bohemian Rhapsody by Queen")

# Print the results
print(json.dumps(result, indent=2))

# Access specific parts
if "input_song_analysis" in result:
    analysis = result["input_song_analysis"]
    print(f"Song: {analysis['song_name']} by {analysis['artist']}")
    
    # Check the vibe
    vibe = analysis["parameters"]["Intangible Vibe"]
    print(f"Vibe: {vibe['value']} (confidence: {vibe['confidence_score']})")
    
    # Get recommendations
    for i, rec in enumerate(result["recommendations"], 1):
        print(f"\n{i}. {rec['song_name']} by {rec['artist']}")
        print(f"   Why: {rec['rationale']}")
```

### 3. Batch Processing

```python
from tune_trace_ai import create_agent

agent = create_agent()

# Analyze multiple songs at once
songs = [
    "Happy by Pharrell Williams",
    "Blinding Lights by The Weeknd",
    "https://open.spotify.com/track/xyz"
]

results = agent.analyze_batch(songs)

# Process results
for item in results["results"]:
    print(f"Input: {item['input']}")
    print(f"Analysis: {item['analysis']}")
```

## Testing

```bash
# Run deployment tests
python deployment/test_deployment.py

# Run unit tests
pytest tests/

# Run evaluation suite
python eval/test_eval.py
```

## Common Examples

### Example 1: Hip-Hop Analysis

```python
agent = create_agent()
result = agent.analyze_song("Shook Ones, Pt. II by Mobb Deep")

# Expected output includes:
# - Genre: Hip-Hop / East Coast Hardcore Hip-Hop
# - Mood: Anxious, Aggressive, Menacing
# - 3 recommendations including a wildcard
```

### Example 2: URL Analysis

```python
agent = create_agent()
result = agent.analyze_song("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

# Analyzes the song from the YouTube URL
```

### Example 3: Multiple Songs

```python
agent = create_agent()
result = agent.analyze_song("""
Billie Jean by Michael Jackson
Thriller by Michael Jackson
Beat It by Michael Jackson
""")

# Handles multiple songs automatically
print(f"Analyzed {result['count']} songs")
```

## Output Structure

Every successful analysis returns:

```json
{
  "disclaimer": "AI-generated analysis disclaimer",
  "input_song_analysis": {
    "song_name": "...",
    "artist": "...",
    "parameters": {
      "Intangible Vibe": { "value": "...", "confidence_score": 0.0-1.0 },
      "Genre / Subgenre": { "value": {...}, "confidence_score": 0.0-1.0 },
      // ... 18 more parameters
    }
  },
  "recommendations": [
    {
      "song_name": "Direct Match 1",
      "artist": "...",
      "rationale": "Why this matches (2+ parameter references)"
    },
    {
      "song_name": "Direct Match 2",
      "artist": "...",
      "rationale": "..."
    },
    {
      "song_name": "Wildcard",
      "artist": "...",
      "rationale": "[WILDCARD] Different genre but similar vibe..."
    }
  ]
}
```

## Understanding the Results

### Confidence Scores

- `1.0` = Highly confident
- `0.7-0.9` = Confident
- `0.5-0.7` = Moderate confidence
- `<0.5` = Low confidence

### Recommendations

1. **First two** = Direct style matches
2. **Third (Wildcard)** = Different in 2+ HIGH categories but shares key vibe/mood

### Parameters

- **HIGH priority** (4): Intangible Vibe, Genre/Subgenre, Mood/Tone, Tempo
- **MEDIUM priority** (6): Vocal Style, Lyrics, Instrumentation, Timbre, Rhythm, Occasion
- **LOW priority** (9): Structure, Dynamics, Harmony, Density, Imaging, Effects, Era, Geography, Sampling

## Troubleshooting

### "GOOGLE_API_KEY environment variable must be set"

```bash
export GOOGLE_API_KEY="your-actual-key-here"
```

### "Failed to generate valid JSON output"

- Try being more specific: Include both song name AND artist
- Check internet connection
- Verify API key is valid

### Import errors

```bash
# Make sure you installed the package
pip install -e .

# Or add to Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/TuneTrace.AI"
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [tests/test_agents.py](tests/test_agents.py) for more examples
- Run [eval/test_eval.py](eval/test_eval.py) to see the system in action
- Explore the 20-parameter rubric in detail

## Support

For issues, questions, or contributions:
- Review the main README.md
- Check the example code in tests/
- Examine the evaluation suite in eval/

---

**Happy music discovering! 🎵**



