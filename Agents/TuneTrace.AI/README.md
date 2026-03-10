# 🎵 TuneTrace.AI - Advanced Music Analysis & Recommendation System

TuneTrace.AI is a sophisticated agentic AI system that analyzes songs using a comprehensive 20-parameter rubric and provides intelligent music recommendations. Powered by Google's Gemini 2.0, it combines deep musicological analysis with real-time internet access to deliver personalized song discoveries.

## ✨ Key Features

- **🔍 Multi-Input Support**: Analyze songs by name, artist, URL (YouTube, Spotify, SoundCloud), or multiple inputs at once
- **📊 20-Parameter Analysis**: Comprehensive evaluation across subjective, core musical, advanced sonic, and contextual dimensions
- **🎯 Smart Recommendations**: 2 direct matches + 1 "wildcard" suggestion for enhanced music discovery
- **🌐 Internet-Enabled**: Real-time access to current music information via Google Search grounding
- **🤖 Agentic Architecture**: Self-directed tool usage for gathering information and validating outputs
- **📈 Confidence Scoring**: Each parameter includes a confidence score (0.0-1.0) for transparency
- **🎨 Bias Mitigation**: Built-in diversity considerations for artist demographics and subgenres

## 🎯 The 20-Parameter Rubric

### HIGH Priority (Core Identity)
1. **Intangible Vibe** - The overall feeling and aesthetic
2. **Genre / Subgenre** - Musical style classification
3. **Mood / Tone** - Primary emotional character
4. **Tempo (BPM)** - Speed and energy level

### MEDIUM Priority (Musical Characteristics)
5. **Vocal Style** - Delivery manner
6. **Lyrical Themes** - Subject matter and narrative
7. **Instrumentation** - Key instruments and sounds
8. **Timbre & Texture** - Sound quality and character
9. **Rhythm / Groove** - Rhythmic pattern and feel
10. **Occasion / Activity** - Real-world usage context

### LOW Priority (Technical & Contextual)
11. **Song Structure** - Section arrangement
12. **Dynamic Range** - Volume variation
13. **Harmonic Complexity** - Chord progression intricacy
14. **Instrumentation Density** - Number of layers
15. **Stereo Imaging** - Spatial audio placement
16. **Use of Effects** - Audio processing techniques
17. **Era / Decade** - Time period influence
18. **Geographic Origin** - Regional sound characteristics
19. **Sampling / Intertextuality** - Use of other recordings

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- Google API Key with Gemini 2.0 access

### Installation

```bash
# Clone or navigate to the TuneTrace.AI directory
cd TuneTrace.AI

# Install dependencies
pip install -e .

# Set your Google API key
export GOOGLE_API_KEY="your-api-key-here"
```

### Basic Usage

#### Python API

```python
from tune_trace_ai import create_agent

# Create the agent
agent = create_agent()

# Analyze a single song
result = agent.analyze_song("Bohemian Rhapsody by Queen")

# Analyze by URL
result = agent.analyze_song("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

# Analyze multiple songs
result = agent.analyze_song("""
Lose Yourself by Eminem
https://open.spotify.com/track/xyz
Stairway to Heaven
""")

# Batch analysis
results = agent.analyze_batch([
    "Song 1",
    "Song 2",
    "https://youtube.com/watch?v=xyz"
])

# Print results
import json
print(json.dumps(result, indent=2))
```

#### Command Line

```bash
# Analyze a song
python -m tune_trace_ai.agent "Bohemian Rhapsody by Queen"

# Analyze by URL
python -m tune_trace_ai.agent "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

## 📋 Output Format

The system outputs a structured JSON object:

```json
{
  "disclaimer": "This analysis is AI-generated and may contain subjective or estimated information.",
  "input_song_analysis": {
    "song_name": "Song Title",
    "artist": "Artist Name",
    "parameters": {
      "Intangible Vibe": {
        "value": "Description of the vibe",
        "confidence_score": 0.95
      },
      "Genre / Subgenre": {
        "value": {
          "genre": "Main Genre",
          "subgenre": "Specific Subgenre"
        },
        "confidence_score": 1.0
      }
      // ... all 20 parameters
    }
  },
  "recommendations": [
    {
      "song_name": "Similar Song 1",
      "artist": "Artist Name",
      "rationale": "Explanation referencing 2+ parameters from rubric"
    },
    {
      "song_name": "Similar Song 2",
      "artist": "Different Artist",
      "rationale": "Explanation with parameter references"
    },
    {
      "song_name": "Wildcard Song",
      "artist": "Another Artist",
      "rationale": "[WILDCARD] Differs in 2+ HIGH categories but shares key vibe/mood"
    }
  ]
}
```

## 🔧 Configuration

### Environment Variables

```bash
# Required
export GOOGLE_API_KEY="your-gemini-api-key"

# Optional (defaults shown)
export TUNETRACE_MODEL="gemini-2.0-flash-exp"
```

### Model Selection

```python
# Use a different Gemini model
agent = create_agent(model_name="gemini-2.0-flash-exp")
```

## 🏗️ Architecture

TuneTrace.AI uses an agentic architecture with the following components:

1. **Main Agent** (`agent.py`): Orchestrates the analysis workflow
2. **Tool System** (`tools.py`): Provides internet access and search capabilities
   - `search_song_info`: Google Search for song details
   - `fetch_song_from_url`: Extract info from URLs
   - `search_similar_songs`: Find matching tracks
3. **Prompt System** (`prompt.py`): Contains rubric and instructions
4. **Analysis Engine**: Processes 20 parameters with confidence scoring
5. **Recommendation Engine**: Generates 2 direct + 1 wildcard matches

### Agentic Workflow

```
User Input → Parse Input(s) → Agent Loop:
                                 ├─ Use Tools (search, fetch)
                                 ├─ Analyze 20 Parameters
                                 ├─ Generate Recommendations
                                 └─ Validate JSON Output
                                      ↓
                               Formatted JSON Response
```

## 🎼 Example Analysis

**Input**: "Shook Ones, Pt. II by Mobb Deep"

**Output Highlights**:
- **Intangible Vibe**: "Gritty, tense, late-night on a dangerous city street" (confidence: 1.0)
- **Genre**: Hip-Hop / East Coast Hardcore Hip-Hop (confidence: 1.0)
- **Recommendations**:
  1. C.R.E.A.M. by Wu-Tang Clan (similar mood and era)
  2. Gimme the Loot by The Notorious B.I.G. (matching vibe and themes)
  3. **[WILDCARD]** Teardrop by Massive Attack (different genre but same dark, anxious mood)

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=tune_trace_ai tests/

# Test deployment
python deployment/test_deployment.py
```

## 📦 Deployment

```bash
# Deploy to production
python deployment/deploy.py

# Test deployed agent
python deployment/test_deployment.py
```

## 🤝 Contributing

Contributions are welcome! Areas for enhancement:
- Additional music platforms (Apple Music, Tidal, Bandcamp)
- Audio analysis integration (librosa, essentia)
- User preference learning
- Playlist generation
- Multi-language support

## 🛠️ Troubleshooting

### Common Issues

**Issue**: "GOOGLE_API_KEY environment variable must be set"
- **Solution**: Export your API key: `export GOOGLE_API_KEY="your-key"`

**Issue**: "Failed to generate valid JSON output"
- **Solution**: The model may need more context. Try providing more specific input (song + artist)

**Issue**: "Error searching for song"
- **Solution**: Check internet connectivity and API key validity

## 📄 License

This project is part of the Google ADK samples collection.

## 🙏 Acknowledgments

- Built with Google Gemini 2.0 Flash
- Inspired by musicology research and recommendation systems
- Part of the Google Agent Development Kit (ADK) samples

## 📧 Support

For issues and questions:
- GitHub Issues: [Create an issue]
- Documentation: See this README
- Examples: Check `tests/` directory

---

**TuneTrace.AI v2.0** - Discover music through intelligent analysis 🎵✨



