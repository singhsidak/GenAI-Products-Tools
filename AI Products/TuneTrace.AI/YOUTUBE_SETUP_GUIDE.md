# 🎵 YouTube Playlist Creation Setup Guide

This guide will help you set up YouTube API credentials to create playlists directly from TuneTrace.AI.

---

## ⚠️ **Important Note**

The API key you provided (`AIzaSyAInlPV_LABgZwsIOBRXddVOZHLj8CeMgM`) is a **YouTube Data API v3 read-only key**. This allows searching for videos but **CANNOT create playlists**.

To create playlists, you need **OAuth 2.0 credentials** (not just an API key).

---

## 📋 **Prerequisites**

- Google Cloud Console account
- YouTube channel (the account you'll authenticate with)

---

## 🔧 **Setup Steps**

### **Step 1: Enable YouTube Data API v3**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Go to **"APIs & Services"** → **"Library"**
4. Search for **"YouTube Data API v3"**
5. Click **"Enable"**

### **Step 2: Create OAuth 2.0 Credentials**

1. In Google Cloud Console, go to **"APIs & Services"** → **"Credentials"**
2. Click **"+ CREATE CREDENTIALS"** → **"OAuth client ID"**
3. If prompted, configure the OAuth consent screen:
   - Choose **"External"** (unless you have a Google Workspace account)
   - Fill in required fields:
     - **App name**: `TuneTrace.AI`
     - **User support email**: Your email
     - **Developer contact**: Your email
   - Click **"Save and Continue"**
   - On **"Scopes"** page, click **"Save and Continue"** (no scopes needed here)
   - On **"Test users"** page, add your email as a test user
   - Click **"Save and Continue"**
4. Back in **"Credentials"**, click **"+ CREATE CREDENTIALS"** → **"OAuth client ID"**
5. Choose **"Desktop app"** as the application type
6. Name it: `TuneTrace.AI Desktop Client`
7. Click **"Create"**

### **Step 3: Download Credentials**

1. After creating the OAuth client, a dialog will appear
2. Click **"DOWNLOAD JSON"**
3. Save the file as `client_secret.json`
4. Move it to your TuneTrace.AI project root directory:
   ```bash
   mv ~/Downloads/client_secret_*.json /Users/sidaksingh/Desktop/ADK/google-adk/adk-samples/python/agents/TuneTrace.AI/client_secret.json
   ```

### **Step 4: Install Dependencies**

```bash
cd /Users/sidaksingh/Desktop/ADK/google-adk/adk-samples/python/agents/TuneTrace.AI
pip install -e .
```

This will install:
- `google-api-python-client>=2.108.0`
- `google-auth-oauthlib>=1.2.0`
- `google-auth-httplib2>=0.2.0`

---

## ✅ **Verify Setup**

### **Option 1: Check via API**

1. Start the servers:
   ```bash
   ./run_web.sh
   ```

2. Visit: http://localhost:8000/youtube-auth-status

3. You should see:
   ```json
   {
     "authenticated": false,
     "credentials_configured": true,
     "message": "Authentication required"
   }
   ```

### **Option 2: Test Authentication**

1. Open TuneTrace.AI: http://localhost:3000
2. Analyze a song
3. Click **"🎵 Create YouTube Playlist"**
4. Enter a playlist name
5. A browser window will open asking you to:
   - Sign in to your Google account
   - Grant TuneTrace.AI permission to manage your YouTube playlists
6. After authorization, credentials will be saved to `youtube_token.pickle`
7. Future playlist creations won't require re-authentication

---

## 🎯 **How It Works**

### **First-Time Authentication**

1. Click **"🎵 Create YouTube Playlist"**
2. Browser opens → Sign in to Google
3. Grant permissions to TuneTrace.AI
4. Credentials saved locally to `youtube_token.pickle`
5. Playlist created from ALL analyzed songs in your history

### **Subsequent Uses**

1. Click **"🎵 Create YouTube Playlist"**
2. No browser window (uses saved credentials)
3. Playlist created instantly

---

## 📁 **File Structure**

After setup, you should have:

```
TuneTrace.AI/
├── client_secret.json          ← OAuth credentials (required)
├── youtube_token.pickle         ← Saved auth token (auto-generated)
├── app/
│   ├── main.py                  ← Backend with /create-youtube-playlist endpoint
│   └── youtube_playlist.py      ← YouTube API integration
├── frontend/
│   └── src/
│       ├── components/
│       │   └── ResultsDisplay.tsx  ← UI with button
│       └── lib/
│           └── api.ts              ← API client functions
└── .env                          ← API keys
```

---

## 🚨 **Troubleshooting**

### **Error: `client_secret.json` not found**

**Solution**: Follow Step 3 above to download and place the file.

### **Error: "Access blocked: This app's request is invalid"**

**Solution**: 
1. Go to OAuth consent screen in Google Cloud Console
2. Add your email as a **test user**
3. Or publish your app (if you want others to use it)

### **Error: "The project is not configured for YouTube Data API"**

**Solution**: Follow Step 1 to enable the API.

### **Error: "Quota exceeded"**

**Solution**: 
- YouTube Data API has daily quotas
- Each playlist creation uses ~50 quota points
- Each video addition uses ~50 quota points
- Default quota: 10,000 points/day (≈100 videos/day)
- Request quota increase in Google Cloud Console if needed

### **Token Expired**

If you see authentication errors after some time:
1. Delete `youtube_token.pickle`
2. Click **"🎵 Create YouTube Playlist"** again
3. Re-authenticate when prompted

---

## 🎨 **Feature Overview**

### **What Gets Added to the Playlist?**

- ✅ **All analyzed songs** from your TuneTrace.AI history
- ✅ **Input songs** (songs you analyzed)
- ✅ **Recommended songs** (AI recommendations)
- ✅ Automatically removes duplicates
- ✅ Preserves order of analysis

### **Playlist Settings**

- **Privacy**: Always **public**
- **Title**: User-defined
- **Description**: User-defined or auto-generated
- **Videos**: All songs from database with valid YouTube URLs

---

## 🔐 **Security Notes**

1. **`client_secret.json`**:
   - Contains OAuth client ID and secret
   - Should **NOT** be committed to git
   - Already in `.gitignore`

2. **`youtube_token.pickle`**:
   - Contains your authenticated session
   - Should **NOT** be shared
   - Already in `.gitignore`

3. **API Key** (in `.env`):
   - Read-only key for YouTube searches
   - Can be committed (if public project) or kept private

---

## 📊 **API Endpoints**

### **POST `/create-youtube-playlist`**

Create a YouTube playlist from all analyzed songs.

**Request:**
```json
{
  "title": "My TuneTrace.AI Playlist",
  "description": "Generated from analysis",
  "source": "all"
}
```

**Response:**
```json
{
  "success": true,
  "playlist_url": "https://www.youtube.com/playlist?list=PLxxx",
  "playlist_id": "PLxxx",
  "videos": {
    "total": 50,
    "added": 48,
    "failed": 2,
    "details": [...]
  }
}
```

### **GET `/youtube-auth-status`**

Check if YouTube API is configured and authenticated.

**Response:**
```json
{
  "authenticated": true,
  "credentials_configured": true,
  "message": "YouTube API is ready"
}
```

---

## 🎉 **Ready to Use!**

Once setup is complete:

1. **Analyze songs** (build your history)
2. Click **"🎵 Create YouTube Playlist"**
3. Enter playlist details
4. Get a public YouTube playlist with all your analyzed songs!

---

## 📞 **Need Help?**

If you encounter issues:

1. Check the terminal output for detailed error messages
2. Verify all files are in the correct locations
3. Ensure YouTube Data API v3 is enabled
4. Make sure you're added as a test user (if app is not published)

---

**Happy playlist creating! 🎵**

