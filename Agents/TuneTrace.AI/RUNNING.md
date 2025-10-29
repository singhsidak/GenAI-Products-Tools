# 🚀 TuneTrace.AI - Running Guide

## ✅ Application is Currently Running!

### Server Status
- **Backend API**: http://localhost:8000 ✅
- **Frontend UI**: http://localhost:3000 ✅
- **API Docs**: http://localhost:8000/docs ✅

### Process IDs
Check running processes:
```bash
ps aux | grep -E "(main.py|vite)" | grep -v grep
```

### Quick Access
Open in browser:
```bash
# MacOS
open http://localhost:3000

# Linux
xdg-open http://localhost:3000
```

---

## 🛑 Stop Servers

```bash
# Kill both servers
lsof -ti:8000 | xargs kill -9  # Backend
lsof -ti:3000 | xargs kill -9  # Frontend
```

---

## 🔄 Restart Servers

**Option 1: Using Make (Recommended)**
```bash
cd /Users/sidaksingh/Desktop/ADK/google-adk/adk-samples/python/agents/TuneTrace.AI
make dev
```

**Option 2: Manual Start**
```bash
# Terminal 1 - Backend (API key auto-loads from .env)
cd /Users/sidaksingh/Desktop/ADK/google-adk/adk-samples/python/agents/TuneTrace.AI
cd app && python main.py

# Terminal 2 - Frontend
cd /Users/sidaksingh/Desktop/ADK/google-adk/adk-samples/python/agents/TuneTrace.AI/frontend
npm run dev
```

**Option 3: Background Processes**
```bash
cd /Users/sidaksingh/Desktop/ADK/google-adk/adk-samples/python/agents/TuneTrace.AI
cd app && python main.py > /tmp/tunetrace_backend.log 2>&1 &
cd ../frontend && npm run dev > /tmp/tunetrace_frontend.log 2>&1 &
```

**Note:** API key is automatically loaded from `.env` file - no manual export needed!

---

## 🧪 Test the Application

### Health Check
```bash
curl http://localhost:8000/health
```

### Analyze a Song
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"input": "Lose Yourself by Eminem"}'
```

### Via Frontend Proxy
```bash
curl -X POST http://localhost:3000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"input": "Blinding Lights by The Weeknd"}'
```

---

## 🎯 Using the Web Interface

1. **Open**: http://localhost:3000
2. **Enter a song**: "Song Name by Artist" or paste a URL
3. **Click**: "Analyze Song"
4. **Wait**: 10-15 seconds for AI analysis
5. **View**: Complete 20-parameter analysis + 3 recommendations

### Example Songs to Try
- Lose Yourself by Eminem
- Bohemian Rhapsody by Queen
- Blinding Lights by The Weeknd
- Smells Like Teen Spirit by Nirvana
- Happy by Pharrell Williams

---

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/analyze` | POST | Analyze a song |
| `/batch` | POST | Analyze multiple songs |
| `/history` | GET | Get analysis history |
| `/examples` | GET | Get example songs |
| `/docs` | GET | Interactive API docs |

Full documentation: http://localhost:8000/docs

---

## 🔧 Troubleshooting

### Port Already in Use
```bash
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9
```

### API Key Not Set
API key auto-loads from `.env` file. If you see this error:
1. Check `.env` file exists in project root
2. Verify it contains: `GOOGLE_API_KEY=AIzaSyA1G5FLA0LRj1qa5nC_mQeeJL-1R_-ICh8`
3. Backend (`app/main.py`) and frontend scripts automatically load it

### Check Logs
```bash
# If running in background
tail -f /tmp/tunetrace_backend.log
tail -f /tmp/tunetrace_frontend.log
```

### Frontend Not Connecting
1. Check backend is running: `curl http://localhost:8000/health`
2. Check frontend proxy in `frontend/vite.config.ts`
3. Clear browser cache and reload

---

## ✅ Recent Fixes Applied

1. **Error Handling**: Fixed backend error when AI fails to generate JSON
2. **JSON Mode**: Configured Gemini to always return valid JSON
3. **Persistence**: All changes are permanent in code

See `FIXES_SUMMARY.md` for detailed information.

---

## 🎵 Enjoy Your Music Discovery!

The application is fully functional and ready to analyze songs and provide intelligent recommendations powered by Google Gemini 2.0.

**Last Updated**: October 27, 2025
**Status**: ✅ Fully Operational

