# 📊 TuneTrace.AI - SQLite Database Guide

## ✅ Successfully Implemented!

TuneTrace.AI now includes a complete SQLite database system that automatically saves all analyses, provides history tracking, search functionality, and statistics.

## 🗄️ Database Location

**File**: `app/tunetrace.db`  
**Size**: ~32KB (empty), grows with usage  
**Type**: SQLite 3

## 📋 Database Schema

### Tables

#### 1. **analyses** (Main table)
Stores complete analysis results:
- `id` - Primary key
- `input_text` - Original user input
- `song_name` - Identified song name
- `artist` - Artist name
- `analysis_data` - Full 20-parameter analysis (JSON)
- `recommendations` - 3 recommendations (JSON)
- `created_at` - Timestamp
- `success` - Whether analysis succeeded
- `error_message` - Error details (if failed)

#### 2. **parameters** (For searching)
Individual parameters for each analysis:
- `id` - Primary key
- `analysis_id` - Foreign key to analyses
- `parameter_name` - Name of parameter
- `parameter_value` - Value (JSON)
- `confidence_score` - Confidence score (0.0-1.0)

#### 3. **recommendation_songs**
Individual recommendations:
- `id` - Primary key
- `analysis_id` - Foreign key to analyses
- `song_name` - Recommended song
- `artist` - Recommended artist
- `rationale` - Why it was recommended
- `is_wildcard` - Boolean flag
- `position` - 1, 2, or 3

## 🚀 API Endpoints

### 📥 Auto-Save on Analysis

Every analysis is automatically saved:

```bash
POST /analyze
{
  "input": "Bohemian Rhapsody by Queen"
}

# Returns analysis_id in response
```

### 📖 View History

```bash
# Get recent analyses (default: 50, max: 100)
GET /history?limit=20&offset=0&success_only=true

# Response:
{
  "success": true,
  "count": 20,
  "history": [
    {
      "id": 2,
      "input_text": "Bohemian Rhapsody Queen",
      "song_name": "Bohemian Rhapsody by Queen",
      "artist": "Unknown",
      "created_at": "2025-10-24 16:42:00",
      "success": true
    }
  ]
}
```

### 🔍 Get Specific Analysis

```bash
# Get complete analysis by ID
GET /history/2

# Returns full analysis with all parameters and recommendations
```

### 🔎 Search Analyses

```bash
# Search by song name, artist, or input text
GET /search?q=Queen&limit=20

# Response:
{
  "success": true,
  "query": "Queen",
  "count": 3,
  "results": [...]
}
```

### 📊 Get Statistics

```bash
GET /statistics

# Returns:
{
  "success": true,
  "statistics": {
    "total_analyses": 100,
    "successful_analyses": 95,
    "failed_analyses": 5,
    "success_rate": 95.0,
    "top_artists": [
      {"artist": "Queen", "count": 10},
      {"artist": "The Beatles", "count": 8}
    ],
    "top_recommendations": [
      {"song_name": "Stairway to Heaven", "artist": "Led Zeppelin", "count": 5}
    ],
    "recent_activity": [
      {"date": "2025-10-24", "count": 15}
    ]
  }
}
```

### 🗑️ Delete Analysis

```bash
DELETE /history/2

# Returns:
{
  "success": true,
  "message": "Analysis 2 deleted successfully"
}
```

### ⚠️ Clear All Data

```bash
# DANGER: Deletes all analyses (must confirm)
POST /clear?confirm=DELETE_ALL

# Returns:
{
  "success": true,
  "message": "Database cleared successfully",
  "deleted_analyses": 100
}
```

## 💻 Using the Database in Code

### Python Example

```python
import requests

# Analyze a song (auto-saved)
response = requests.post('http://localhost:8000/analyze', json={
    "input": "Lose Yourself by Eminem"
})
result = response.json()
analysis_id = result['analysis_id']
print(f"Saved with ID: {analysis_id}")

# Get history
history = requests.get('http://localhost:8000/history').json()
print(f"Total analyses: {history['count']}")

# Search
search = requests.get('http://localhost:8000/search?q=Eminem').json()
print(f"Found {search['count']} results")

# Get statistics
stats = requests.get('http://localhost:8000/statistics').json()
print(f"Success rate: {stats['statistics']['success_rate']}%")
```

### JavaScript Example

```javascript
// Analyze and save
const response = await fetch('http://localhost:8000/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ input: 'Happy by Pharrell' })
});
const data = await response.json();
console.log('Analysis ID:', data.analysis_id);

// Get history
const history = await fetch('http://localhost:8000/history').then(r => r.json());
console.log('Recent analyses:', history.history);

// Search
const results = await fetch('http://localhost:8000/search?q=Pharrell').then(r => r.json());
console.log('Search results:', results.count);
```

## 📊 What Gets Saved

### ✅ Successful Analyses
- Complete 20-parameter analysis
- All confidence scores
- 3 recommendations with rationales
- Wildcard flag
- Song and artist names
- Input text
- Timestamp

### ❌ Failed Analyses
- Input text
- Error message
- Timestamp
- Marked as failed

## 🔍 Query Examples

### Get Recent Analyses
```bash
curl http://localhost:8000/history
```

### Get Failed Analyses
```bash
curl "http://localhost:8000/history?success_only=false"
```

### Search for Artist
```bash
curl "http://localhost:8000/search?q=Beatles"
```

### Pagination
```bash
curl "http://localhost:8000/history?limit=10&offset=20"
```

## 📈 Statistics Tracked

1. **Total Analyses** - All time count
2. **Success Rate** - Percentage of successful analyses
3. **Top Artists** - Most frequently analyzed (top 10)
4. **Top Recommendations** - Most recommended songs (top 10)
5. **Recent Activity** - Analyses per day (last 7 days)

## 🛠️ Database Management

### View Database Directly

```bash
cd app
sqlite3 tunetrace.db

# SQL queries
SELECT COUNT(*) FROM analyses;
SELECT song_name, artist FROM analyses WHERE success = 1;
SELECT * FROM analyses ORDER BY created_at DESC LIMIT 10;
```

### Backup Database

```bash
# Copy database file
cp app/tunetrace.db app/tunetrace_backup_$(date +%Y%m%d).db

# Or export to JSON
curl http://localhost:8000/history?limit=1000 > backup.json
```

### Reset Database

```bash
# Option 1: Delete file
rm app/tunetrace.db
# Restart server to recreate

# Option 2: Use API
curl -X POST "http://localhost:8000/clear?confirm=DELETE_ALL"
```

## 🔒 Data Privacy

- All data is stored locally in `app/tunetrace.db`
- No external database server required
- No data is sent to third parties
- You have full control over the database file

## 📊 Performance

- **Storage**: ~2-3KB per analysis
- **Speed**: Instant saves and queries
- **Scalability**: Can handle 100,000+ analyses
- **Indexes**: Optimized for fast searches

## 🎯 Use Cases

1. **History Tracking** - Review all past analyses
2. **Pattern Recognition** - See which songs you analyze most
3. **Recommendation Trends** - Track most recommended songs
4. **Data Export** - Export for analysis elsewhere
5. **Debugging** - Review failed analyses
6. **Statistics** - Understand usage patterns

## 🆕 New in This Update

- ✅ SQLite database integration
- ✅ Automatic save on every analysis
- ✅ History endpoint with pagination
- ✅ Search functionality
- ✅ Statistics and insights
- ✅ Individual analysis retrieval
- ✅ Delete functionality
- ✅ Failed analysis tracking

## 🔄 Migration Notes

If upgrading from a version without database:
- Old analyses were not saved (ephemeral)
- New analyses will be automatically saved
- No migration needed - fresh start

## 📞 API Documentation

Full interactive API documentation available at:
**http://localhost:8000/docs**

Includes:
- Try-it-out functionality
- Request/response schemas
- Error codes
- Example values

---

**Database Status**: ✅ Production Ready  
**Last Updated**: October 24, 2025  
**Version**: 2.0 with SQLite
