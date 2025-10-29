# 🎵 Final OAuth Setup Step

You're almost ready! Just one more configuration needed.

---

## ⚠️ **Important: Add Redirect URI**

Your OAuth credentials are configured as a **Web application**, so you need to add authorized redirect URIs.

### **Step-by-Step:**

1. **Go to Google Cloud Console:**
   - Visit: https://console.cloud.google.com/apis/credentials
   - Select project: `tuneweaver-474509`

2. **Edit Your OAuth 2.0 Client:**
   - Find your OAuth client: `400030773119-a8jm5ncn8uukb43m02000a3v91n7mns6`
   - Click the **edit (pencil) icon**

3. **Add Authorized Redirect URIs:**
   - Scroll down to **"Authorized redirect URIs"**
   - Click **"+ ADD URI"**
   - Add these **two URIs** (one at a time):
   
   ```
   http://localhost:8080/
   ```
   
   ```
   http://localhost:8080/oauth2callback
   ```

4. **Save:**
   - Click **"SAVE"** at the bottom
   - Wait ~5 seconds for changes to propagate

---

## ✅ **Test the Feature**

Once you've added the redirect URIs:

### **Option 1: Via Web UI (Recommended)**

1. Open: http://localhost:3000
2. Analyze any song (e.g., "Lose Yourself by Eminem")
3. Scroll down and click: **"🎵 Create YouTube Playlist"**
4. Enter playlist title: `TuneTrace.AI Test Playlist`
5. Enter description: `Testing playlist creation`
6. **Browser will open** asking you to sign in with: `singhsidak70@gmail.com`
7. Grant permissions
8. Done! Playlist created!

### **Option 2: Via API (Direct Test)**

```bash
curl -X POST http://localhost:8000/create-youtube-playlist \
  -H "Content-Type: application/json" \
  -d '{
    "title": "TuneTrace.AI Test",
    "description": "Created via API",
    "source": "all"
  }'
```

---

## 🎯 **What Will Happen**

### **First Time (Authentication):**

1. You click "Create Playlist"
2. Browser opens → https://accounts.google.com/o/oauth2/auth...
3. Sign in with: `singhsidak70@gmail.com`
4. You'll see: **"TuneTrace.AI wants to access your Google Account"**
5. Permissions requested:
   - ✅ Manage your YouTube playlists
6. Click **"Continue"** or **"Allow"**
7. Browser redirects to: `http://localhost:8080/oauth2callback`
8. You'll see: **"The authentication flow has completed."**
9. Close the browser tab
10. **Playlist created!** Opens automatically in new tab

### **Future Times:**

- No browser window
- Instant playlist creation
- Uses saved token from `youtube_token.pickle`

---

## 🚨 **Troubleshooting**

### **Error: "redirect_uri_mismatch"**

**Cause**: Redirect URI not added in Google Cloud Console

**Solution**: 
1. Add both URIs listed above
2. Make sure there are **no trailing slashes** except for the first one
3. Wait 5-10 seconds after saving

### **Error: "Access blocked: This app's request is invalid"**

**Cause**: Your email not added as test user

**Solution**:
1. Go to: https://console.cloud.google.com/apis/credentials/consent
2. Under **"Test users"**, click **"+ ADD USERS"**
3. Add: `singhsidak70@gmail.com`
4. Click **"SAVE"**

### **Error: "insufficient authentication scopes"**

**Cause**: Wrong scope requested

**Solution**: 
- The code uses: `https://www.googleapis.com/auth/youtube.force-ssl`
- This is correct for playlist management
- If you see this, delete `youtube_token.pickle` and re-authenticate

---

## 📊 **Current Status**

| Item | Status |
|------|--------|
| OAuth Credentials | ✅ Configured (`client_secret.json`) |
| YouTube Data API v3 | ✅ Enabled |
| Test User | ✅ Added (`singhsidak70@gmail.com`) |
| Redirect URIs | ⏳ **Needs your action** |
| Backend | ✅ Running (http://localhost:8000) |
| Frontend | ✅ Running (http://localhost:3000) |

---

## 🎉 **Almost There!**

Just add those 2 redirect URIs and you're ready to create YouTube playlists! 🚀

**Total time: ~2 minutes**

---

## 📞 **Need Help?**

- **Redirect URI format**: Must be **exact**, including `http://` and port `:8080`
- **Multiple URIs**: You need **both** URIs (with and without `/oauth2callback`)
- **Wait time**: Changes take 5-10 seconds to propagate
- **Test user**: Must be the same email you'll authenticate with

---

**Once redirect URIs are added, click the button in TuneTrace.AI and you're done! 🎵**

