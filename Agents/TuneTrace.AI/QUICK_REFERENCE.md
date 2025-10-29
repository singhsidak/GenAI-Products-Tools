# 🚀 TuneTrace.AI - Quick Reference

## ✅ All Requirements Implemented

1. ✅ **Automatic .env API Key Loading** - No user input required
2. ✅ **Tabular Database** - Input, output, parameters, confidence scores
3. ✅ **Data Appending** - All queries add new rows (no override)

---

## 🎯 Quick Start

### Start the Backend
```bash
cd TuneTrace.AI/app
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Expected Output**:
```
✅ Loaded API key from .env file
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## 📊 View Tabular Data

### 1. Get All Data in Tabular Format
```bash
curl http://localhost:8000/table
```

**Returns**: Complete table with all analyses, parameters, values, and confidence scores

### 2. Get Parameters Table
```bash
curl "http://localhost:8000/table/parameters?limit=100"
```

**Returns**: 
```json
{
  "success": true,
  "count": 39,
  "data": [
    {
      "id": 1,
      "analysis_id": 1,
      "input_text": "Bohemian Rhapsody by Queen",
      "song_name": "Bohemian Rhapsody by Queen",
      "artist": "Unknown",
      "parameter_name": "Intangible Vibe",
      "parameter_value": "Epic, theatrical...",
      "confidence_score": 0.95,
      "created_at": "2025-10-24 16:52:37"
    },
    ...
  ]
}
```

### 3. Get Parameters for Specific Analysis
```bash
curl http://localhost:8000/table/parameters/1
```

**Returns**: All 20 parameters for analysis ID 1

---

## 🎵 Analyze Songs

### Analyze a Single Song
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"input": "Song Name by Artist"}'
```

**Returns**:
```json
{
  "success": true,
  "analysis_id": 3,
  "data": {
    "input_song_analysis": {...},
    "recommendations": [...]
  }
}
```

---

## 📈 Database Information

### View Statistics
```bash
curl http://localhost:8000/statistics
```

**Returns**:
```json
{
  "total_analyses": 2,
  "successful_analyses": 2,
  "total_parameters": 39,
  "success_rate": 100.0,
  "top_artists": [...],
  "top_recommendations": [...],
  "recent_activity": [...]
}
```

### View History
```bash
curl "http://localhost:8000/history?limit=10"
```

### Search
```bash
curl "http://localhost:8000/search?q=Queen"
```

---

## 📊 Database Tables

### Table 1: `analyses`
Main analysis records with metadata

### Table 2: `parameters` ⭐
**This is the main tabular view you requested**

| Column | Description |
|--------|-------------|
| `id` | Unique parameter ID |
| `analysis_id` | Links to analysis |
| `parameter_name` | Parameter name (e.g., "Tempo (BPM)") |
| `parameter_value` | Value of the parameter (OUTPUT) |
| `confidence_score` | AI confidence (0.0 to 1.0) |

**Access via**: `GET /table/parameters`

### Table 3: `recommendation_songs`
Individual recommendations for each analysis

---

## 🎯 Example Workflow

```bash
# 1. Start backend (API key auto-loads from .env)
cd TuneTrace.AI/app && uvicorn main:app --port 8000 --reload

# 2. Analyze first song (auto-saved)
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"input": "Bohemian Rhapsody by Queen"}'
# → analysis_id: 1

# 3. Analyze second song (appended, not overridden)
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"input": "Stairway to Heaven by Led Zeppelin"}'
# → analysis_id: 2

# 4. View all parameters in tabular format
curl http://localhost:8000/table/parameters

# 5. Check statistics
curl http://localhost:8000/statistics
# Shows: 2 analyses, 39 parameters (both saved, no override)
```

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `.env` | Contains `GOOGLE_API_KEY` (auto-loaded) |
| `app/tunetrace.db` | SQLite database (all data stored here) |
| `app/main.py` | FastAPI backend with tabular endpoints |
| `app/database/db.py` | Database management |
| `tune_trace_ai/agent.py` | AI agent with .env auto-loading |

---

## 🔧 All Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Service information |
| GET | `/health` | Health check + API key status |
| POST | `/analyze` | Analyze song (auto-saved) |
| GET | `/history` | Analysis history |
| GET | `/search?q=query` | Search analyses |
| GET | `/statistics` | Usage statistics |
| **GET** | **`/table`** | **Complete tabular view** ⭐ |
| **GET** | **`/table/parameters`** | **Parameters table** ⭐ |
| **GET** | **`/table/parameters/{id}`** | **Single analysis parameters** ⭐ |

---

## ✅ Verification Checklist

- [ ] Backend starts with "✅ Loaded API key from .env file"
- [ ] `/health` shows `"api_key_configured": true`
- [ ] First analysis gets `analysis_id: 1`
- [ ] Second analysis gets `analysis_id: 2` (not 1!)
- [ ] `/statistics` shows both analyses
- [ ] `/table/parameters` shows all parameters with confidence scores

---

## 🎉 All Requirements Met!

| Requirement | Status |
|-------------|--------|
| 1. Auto-load API key from .env | ✅ DONE |
| 2. Tabular database format | ✅ DONE |
| 3. Data appending (no override) | ✅ DONE |

---

## 📚 Documentation

- **`IMPLEMENTATION_COMPLETE.md`** - Detailed implementation guide
- **`DATABASE_GUIDE.md`** - Database documentation
- **`QUICK_REFERENCE.md`** - This file
- **`WEB_GUIDE.md`** - Web interface guide
- **`START_HERE.md`** - Quick start

---

**Everything is ready to use! 🚀**

Backend: `http://localhost:8000`  
Database: `app/tunetrace.db`  
API Key: Auto-loaded from `.env`



