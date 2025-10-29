# 🚀 TuneTrace.AI - START HERE

## Quick Start (Web Interface)

Get the web app running in 3 simple steps:

### Step 1: Install Dependencies

```bash
cd TuneTrace.AI
make install
```

Or manually:
```bash
# Backend
pip install -e ".[dev]"
pip install fastapi uvicorn pydantic

# Frontend
cd frontend && npm install
```

### Step 2: Set Your API Key

The API key is already configured in the `.env` file!

If you need to update it, edit the `.env` file:
```bash
GOOGLE_API_KEY=your-google-api-key-here
```

Get a new key from: https://aistudio.google.com/app/apikey

**Note:** The app automatically loads the API key from `.env` - no need to export it manually!

### Step 3: Run the App

**Option A: Using Make (Recommended)**
```bash
make dev
```

**Option B: Using the Shell Script**
```bash
./run_web.sh
```

**Option C: Run Separately**
```bash
# Terminal 1 - Backend
cd app && python main.py

# Terminal 2 - Frontend
cd frontend && npm run dev
```

### Step 4: Open Your Browser

Navigate to: **http://localhost:3000**

The API docs are available at: **http://localhost:8000/docs**

## 🎯 What You Can Do

1. **Enter a song** - Type song name, artist, or paste a URL
2. **Click "Analyze Song"** - AI analyzes in 10-15 seconds
3. **View results** - See 20-parameter analysis + 3 recommendations
4. **Try examples** - Click example chips for quick testing

## 📚 Need More Help?

- **Web Guide**: See [WEB_GUIDE.md](WEB_GUIDE.md) for complete web docs
- **Quick Start**: See [QUICKSTART.md](QUICKSTART.md) for CLI usage
- **Full Docs**: See [README.md](README.md) for everything
- **Architecture**: See [ARCHITECTURE.md](ARCHITECTURE.md) for technical details

## 🐛 Troubleshooting

**"GOOGLE_API_KEY not set"**
The app should auto-load from `.env` file. If it doesn't work:
1. Check that `.env` file exists in the project root
2. Verify the file contains: `GOOGLE_API_KEY=your-key`
3. Or manually export: `export GOOGLE_API_KEY="your-key"`

**"Port already in use"**
```bash
# Kill existing processes
lsof -ti:8000 | xargs kill -9  # Backend
lsof -ti:3000 | xargs kill -9  # Frontend
```

**"npm install fails"**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**"Cannot connect to backend"**
- Make sure backend is running on port 8000
- Check `frontend/vite.config.ts` proxy settings

## 🎨 Using the Interface

### Input Options

```
1. Song + Artist:
   "Lose Yourself by Eminem"

2. YouTube URL:
   "https://www.youtube.com/watch?v=xyz"

3. Spotify URL:
   "https://open.spotify.com/track/xyz"

4. Multiple Songs (one per line):
   Song 1
   Song 2
   Song 3
```

### Understanding Results

**Parameter Colors:**
- 🟢 Green badge (90%+) = High confidence
- 🟡 Yellow badge (70-89%) = Medium confidence  
- 🔴 Red badge (<70%) = Low confidence

**Recommendations:**
- **#1 & #2** = Direct style matches
- **#3 with 🎲** = Wildcard (cross-genre discovery)

### Features

- ✅ Real-time AI analysis
- ✅ 20-parameter music rubric
- ✅ Confidence scoring
- ✅ Wildcard recommendations
- ✅ Mobile responsive
- ✅ Dark mode UI

## 🎯 Example Usage Flow

```
1. Open http://localhost:3000
2. Click "Lose Yourself by Eminem" (example chip)
3. Click "Analyze Song"
4. Wait 10-15 seconds
5. View complete analysis with recommendations
6. Expand "View All 20 Parameters" for details
```

## 💡 Pro Tips

1. **Be Specific**: Include both song name AND artist for best results
2. **URLs Work**: Paste YouTube/Spotify URLs directly
3. **Batch Mode**: Enter multiple songs (one per line)
4. **Confidence Scores**: Higher = more certain analysis
5. **Wildcard**: Third recommendation is always cross-genre

## 📊 What Gets Analyzed

### HIGH Priority (Core Identity)
- Intangible Vibe
- Genre / Subgenre
- Mood / Tone
- Tempo (BPM)

### MEDIUM Priority (Musical Characteristics)
- Vocal Style
- Lyrical Themes
- Instrumentation
- Timbre & Texture
- Rhythm / Groove
- Occasion / Activity

### LOW Priority (Technical & Context)
- Song Structure
- Dynamic Range
- Harmonic Complexity
- Instrumentation Density
- Stereo Imaging
- Use of Effects
- Era / Decade
- Geographic Origin
- Sampling / Intertextuality

## 🌐 Backend API

While the web interface is running, you can also use the API directly:

```bash
# Analyze a song
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"input": "Your Song"}'

# Get examples
curl http://localhost:8000/examples

# Health check
curl http://localhost:8000/health
```

API docs: http://localhost:8000/docs

## 🚀 You're Ready!

Everything is set up. Just run:

```bash
make dev
```

Then open http://localhost:3000 and start discovering music! 🎵✨

---

**TuneTrace.AI v2.0** - Powered by Google Gemini 2.0


