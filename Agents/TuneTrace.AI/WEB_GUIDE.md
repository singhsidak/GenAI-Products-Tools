# 🌐 TuneTrace.AI Web Interface Guide

Complete guide to running TuneTrace.AI as a full-stack web application.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                  WEB APPLICATION                     │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────┐           ┌──────────────────┐   │
│  │   Frontend   │  ◄──────► │   Backend API    │   │
│  │  React + TS  │   HTTP    │   FastAPI        │   │
│  │  Port: 3000  │           │   Port: 8000     │   │
│  └──────────────┘           └─────────┬────────┘   │
│        │                              │             │
│        │                              ▼             │
│        │                    ┌─────────────────┐    │
│        │                    │  TuneTrace.AI   │    │
│        │                    │  Agent Engine   │    │
│        │                    └─────────────────┘    │
│        │                              │             │
│        ▼                              ▼             │
│  ┌──────────────┐           ┌─────────────────┐   │
│  │   Browser    │           │  Google Gemini  │   │
│  │  localhost   │           │  + Search API   │   │
│  └──────────────┘           └─────────────────┘   │
│                                                      │
└─────────────────────────────────────────────────────┘
```

## 🚀 Quick Start (3 Commands)

```bash
# 1. Install dependencies
make install

# 2. Set API key
export GOOGLE_API_KEY="your-google-api-key"

# 3. Run the app
make dev
```

That's it! Open http://localhost:3000 in your browser.

## 📦 Installation

### Prerequisites

- Python 3.10+
- Node.js 18+ and npm
- Google API Key ([Get one here](https://aistudio.google.com/app/apikey))

### Step-by-Step Setup

```bash
# Navigate to TuneTrace.AI directory
cd TuneTrace.AI

# Install all dependencies (backend + frontend)
make install

# Or install separately:
pip install -e ".[dev]"           # Backend
pip install fastapi uvicorn pydantic
cd frontend && npm install         # Frontend
```

## 🔧 Configuration

### Environment Variables

```bash
# Required
export GOOGLE_API_KEY="your-api-key-here"

# Optional
export PORT=8000                    # Backend port (default: 8000)
export VITE_API_URL="http://localhost:8000"  # API URL for frontend
```

Or create a `.env` file:

```bash
cp env.example .env
# Edit .env with your settings
```

## 🎮 Running the Application

### Full Stack (Recommended)

```bash
make dev
```

This starts both:
- Backend API at http://localhost:8000
- Frontend at http://localhost:3000

### Backend Only

```bash
make dev-backend
```

Access API docs at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Frontend Only

```bash
make dev-frontend
```

Runs React development server on http://localhost:3000

## 🌟 Features

### Frontend Features

- **Modern UI**: Beautiful dark-themed interface
- **Real-time Analysis**: Live updates as AI processes the song
- **Interactive Results**: 
  - Expandable parameter sections
  - Color-coded confidence scores
  - Highlighted wildcard recommendations
- **Example Songs**: Quick-select popular songs to try
- **Responsive**: Works on desktop, tablet, and mobile

### Backend API Endpoints

#### `POST /analyze`
Analyze a single song.

**Request:**
```json
{
  "input": "Lose Yourself by Eminem",
  "description": ""
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "input_song_analysis": { ... },
    "recommendations": [ ... ]
  }
}
```

#### `POST /batch`
Analyze multiple songs.

**Request:**
```json
{
  "songs": [
    "Song 1",
    "Song 2",
    "Song 3"
  ]
}
```

#### `GET /health`
Health check endpoint.

#### `GET /examples`
Get example songs for testing.

## 🎨 Using the Web Interface

### 1. Enter a Song

Three ways to input:
- **Song + Artist**: "Lose Yourself by Eminem"
- **URL**: "https://youtube.com/watch?v=xyz"
- **Multiple Songs**: Separate by newlines

### 2. Click "Analyze Song"

The AI agent will:
- Search for song information online
- Analyze across 20 parameters
- Generate 3 recommendations

### 3. View Results

Results show:
- **Song Info**: Title and artist
- **Core Analysis**: 4 high-priority parameters
- **Musical Characteristics**: 6 medium-priority parameters
- **Recommendations**: 2 direct + 1 wildcard
- **All Parameters**: Expandable section with complete analysis

### 4. Confidence Scores

Each parameter has a color-coded confidence score:
- 🟢 Green (90%+): High confidence
- 🟡 Yellow (70-89%): Medium confidence
- 🔴 Red (<70%): Low confidence

## 🛠️ Development

### Project Structure

```
TuneTrace.AI/
├── app/                      # Backend (FastAPI)
│   ├── __init__.py
│   └── main.py              # API endpoints
│
├── frontend/                 # Frontend (React + TypeScript)
│   ├── src/
│   │   ├── components/      # React components
│   │   │   ├── Header.tsx
│   │   │   ├── AnalysisForm.tsx
│   │   │   └── ResultsDisplay.tsx
│   │   ├── lib/
│   │   │   └── api.ts       # API client
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── vite.config.ts
│   └── index.html
│
├── tune_trace_ai/           # Core agent engine
│   ├── agent.py
│   ├── tools.py
│   └── prompt.py
│
└── Makefile                 # Build commands
```

### Available Make Commands

```bash
make help              # Show all commands
make install           # Install dependencies
make dev               # Run full stack
make dev-backend       # Backend only
make dev-frontend      # Frontend only
make build             # Build for production
make test              # Run tests
make clean             # Clean artifacts
```

### Hot Reloading

Both frontend and backend support hot reloading:
- Frontend: Changes to `.tsx`/`.css` files auto-reload
- Backend: Changes to `.py` files auto-restart

## 🏗️ Production Build

### Build Frontend

```bash
make build
```

Output: `frontend/dist/`

### Serve Production Build

```bash
# Install serve globally
npm install -g serve

# Serve the built frontend
cd frontend && serve -s dist -p 3000
```

### Deploy Backend

```bash
# Production server with gunicorn
pip install gunicorn

# Run with multiple workers
cd app
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 🧪 Testing

### Test Backend API

```bash
# Health check
curl http://localhost:8000/health

# Analyze a song
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"input": "Bohemian Rhapsody by Queen"}'

# Get examples
curl http://localhost:8000/examples
```

### Run Integration Tests

```bash
make test-integration
```

## 🐛 Troubleshooting

### Backend Issues

**"GOOGLE_API_KEY environment variable not set"**
```bash
export GOOGLE_API_KEY="your-key"
```

**"Port 8000 already in use"**
```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9

# Or use different port
PORT=8001 make dev-backend
```

### Frontend Issues

**"Cannot connect to backend"**
- Check backend is running on port 8000
- Check `vite.config.ts` proxy settings
- Try: `VITE_API_URL="http://localhost:8000" npm run dev`

**"npm install fails"**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### CORS Issues

If you see CORS errors:
1. Check `app/main.py` CORS settings
2. Ensure frontend proxy is configured in `vite.config.ts`
3. For production, update `allow_origins` to specific domains

## 📊 Performance

### Response Times
- Health check: <50ms
- Song analysis: 5-15 seconds
- Batch (3 songs): 20-30 seconds

### Optimization Tips

1. **Caching**: Implement Redis for repeated queries
2. **Async**: Use FastAPI async endpoints
3. **CDN**: Serve static frontend files from CDN
4. **Rate Limiting**: Add rate limiting middleware
5. **Load Balancing**: Use multiple backend workers

## 🔒 Security

### Production Checklist

- [ ] Remove `allow_origins=["*"]` from CORS
- [ ] Add authentication/API keys
- [ ] Implement rate limiting
- [ ] Use HTTPS
- [ ] Set secure headers
- [ ] Validate all inputs
- [ ] Monitor API usage
- [ ] Set up logging

## 📱 Mobile Support

The web interface is fully responsive:
- Adapts to mobile screens
- Touch-friendly buttons
- Optimized layouts
- Fast loading

## 🎯 API Integration

Use the backend API in your own apps:

```python
import requests

# Analyze a song
response = requests.post(
    "http://localhost:8000/analyze",
    json={"input": "Your Song"}
)
result = response.json()
```

```javascript
// JavaScript/TypeScript
const response = await fetch('http://localhost:8000/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ input: 'Your Song' })
});
const result = await response.json();
```

## 🚀 Quick Reference

| Command | What It Does |
|---------|-------------|
| `make install` | Install all dependencies |
| `make dev` | Run full stack (backend + frontend) |
| `make dev-backend` | Run API server only |
| `make dev-frontend` | Run React app only |
| `make build` | Build frontend for production |
| `make test` | Run all tests |
| `make clean` | Remove build artifacts |

## 📚 Additional Resources

- Backend API: http://localhost:8000/docs
- Frontend: http://localhost:3000
- Main README: [README.md](README.md)
- Architecture: [ARCHITECTURE.md](ARCHITECTURE.md)
- Quick Start: [QUICKSTART.md](QUICKSTART.md)

---

**TuneTrace.AI Web v2.0** - Modern music analysis at your fingertips! 🎵✨



