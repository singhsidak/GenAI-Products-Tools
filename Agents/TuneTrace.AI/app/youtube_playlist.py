"""
YouTube Playlist Creator for TuneTrace.AI
Creates public YouTube playlists from analyzed songs in the database.
"""

import os
import pickle
from pathlib import Path
from typing import List, Dict, Optional
from urllib.parse import urlparse, parse_qs

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.auth.transport.requests import Request


# Configuration
CLIENT_SECRETS_FILE = "client_secret.json"
TOKEN_FILE = "youtube_token.pickle"
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"


class YouTubePlaylistCreator:
    """Manages YouTube playlist creation via OAuth 2.0"""
    
    def __init__(self, client_secrets_path: Optional[str] = None):
        """
        Initialize the YouTube Playlist Creator
        
        Args:
            client_secrets_path: Path to client_secret.json file
        """
        self.client_secrets_path = client_secrets_path or CLIENT_SECRETS_FILE
        self.token_path = Path(__file__).parent.parent / TOKEN_FILE
        self.youtube_service = None
    
    def get_authenticated_service(self):
        """
        Authenticates the user and returns a YouTube API service object.
        Uses stored credentials if available, otherwise initiates OAuth flow.
        """
        credentials = None
        
        # Try to load existing credentials
        if self.token_path.exists():
            try:
                with open(self.token_path, 'rb') as token:
                    credentials = pickle.load(token)
            except Exception as e:
                print(f"Error loading saved credentials: {e}")
        
        # If credentials are invalid or don't exist, get new ones
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                try:
                    credentials.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing credentials: {e}")
                    credentials = None
            
            if not credentials:
                # Check if client_secret.json exists
                client_secret_path = Path(__file__).parent.parent / self.client_secrets_path
                if not client_secret_path.exists():
                    raise FileNotFoundError(
                        f"❌ YouTube API credentials not found!\n\n"
                        f"Please follow these steps:\n"
                        f"1. Go to: https://console.cloud.google.com/apis/credentials\n"
                        f"2. Create OAuth 2.0 Client ID (Desktop app)\n"
                        f"3. Download JSON and save as: {client_secret_path}\n"
                        f"4. Enable YouTube Data API v3 in your Google Cloud project\n"
                    )
                
                # Start OAuth flow
                # Support both web and desktop app credentials
                try:
                    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                        str(client_secret_path), SCOPES
                    )
                    # Try to run on port 8080 first (common for web apps), then random port
                    try:
                        credentials = flow.run_local_server(port=8080, open_browser=True)
                    except OSError:
                        # Port 8080 in use, try random port
                        credentials = flow.run_local_server(port=0, open_browser=True)
                except Exception as e:
                    print(f"Error with OAuth flow: {e}")
                    raise
                
                # Save credentials for future use
                try:
                    with open(self.token_path, 'wb') as token:
                        pickle.dump(credentials, token)
                    print(f"✅ Credentials saved to {self.token_path}")
                except Exception as e:
                    print(f"⚠️  Could not save credentials: {e}")
        
        # Build and return the service
        self.youtube_service = googleapiclient.discovery.build(
            API_SERVICE_NAME, API_VERSION, credentials=credentials
        )
        return self.youtube_service
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """
        Extracts the video ID from a YouTube URL.
        
        Supports formats:
        - https://www.youtube.com/watch?v=VIDEO_ID
        - https://youtu.be/VIDEO_ID
        - https://www.youtube.com/embed/VIDEO_ID
        - https://www.youtube.com/v/VIDEO_ID
        """
        if not url:
            return None
        
        # Handle youtu.be short links
        if 'youtu.be' in url:
            return url.split('/')[-1].split('?')[0]
        
        # Parse the URL
        parsed = urlparse(url)
        
        if parsed.hostname in ('www.youtube.com', 'youtube.com'):
            # Handle /watch?v=VIDEO_ID
            if parsed.path == '/watch':
                video_id = parse_qs(parsed.query).get('v', [None])[0]
                if video_id:
                    return video_id
            
            # Handle /embed/VIDEO_ID
            if parsed.path.startswith('/embed/'):
                return parsed.path.split('/embed/')[1].split('?')[0]
            
            # Handle /v/VIDEO_ID
            if parsed.path.startswith('/v/'):
                return parsed.path.split('/v/')[1].split('?')[0]
        
        return None
    
    def create_playlist(
        self, 
        title: str, 
        description: str = "", 
        privacy_status: str = "public"
    ) -> Dict:
        """
        Create a new YouTube playlist.
        
        Args:
            title: Playlist title
            description: Playlist description
            privacy_status: 'public', 'private', or 'unlisted'
        
        Returns:
            Dictionary with playlist ID and details
        """
        if not self.youtube_service:
            self.get_authenticated_service()
        
        try:
            playlist_request = self.youtube_service.playlists().insert(
                part="snippet,status",
                body={
                    "snippet": {
                        "title": title,
                        "description": description,
                    },
                    "status": {
                        "privacyStatus": privacy_status
                    }
                }
            )
            playlist_response = playlist_request.execute()
            
            return {
                "success": True,
                "playlist_id": playlist_response["id"],
                "title": playlist_response["snippet"]["title"],
                "url": f"https://www.youtube.com/playlist?list={playlist_response['id']}",
                "description": playlist_response["snippet"]["description"],
                "privacy": playlist_response["status"]["privacyStatus"]
            }
        
        except googleapiclient.errors.HttpError as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": "YouTube API Error"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def add_video_to_playlist(self, playlist_id: str, video_url: str) -> Dict:
        """
        Add a single video to a playlist.
        
        Args:
            playlist_id: The YouTube playlist ID
            video_url: The YouTube video URL
        
        Returns:
            Dictionary with success status and details
        """
        if not self.youtube_service:
            self.get_authenticated_service()
        
        video_id = self.extract_video_id(video_url)
        
        if not video_id:
            return {
                "success": False,
                "error": f"Could not extract video ID from URL: {video_url}",
                "video_url": video_url
            }
        
        try:
            add_video_request = self.youtube_service.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": playlist_id,
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": video_id
                        }
                    }
                }
            )
            response = add_video_request.execute()
            
            return {
                "success": True,
                "video_id": video_id,
                "video_title": response["snippet"]["title"],
                "position": response["snippet"]["position"]
            }
        
        except googleapiclient.errors.HttpError as e:
            error_str = str(e)
            # Check for common errors
            if "videoNotFound" in error_str:
                error_msg = "Video not found or is private"
            elif "forbidden" in error_str.lower():
                error_msg = "Access forbidden (video might be restricted)"
            elif "quota" in error_str.lower():
                error_msg = "YouTube API quota exceeded"
            else:
                error_msg = error_str
            
            return {
                "success": False,
                "error": error_msg,
                "video_id": video_id,
                "video_url": video_url
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "video_id": video_id,
                "video_url": video_url
            }
    
    def create_playlist_from_urls(
        self,
        title: str,
        video_urls: List[str],
        description: str = "",
        privacy_status: str = "public"
    ) -> Dict:
        """
        Create a playlist and add multiple videos to it.
        
        Args:
            title: Playlist title
            video_urls: List of YouTube video URLs
            description: Playlist description
            privacy_status: 'public', 'private', or 'unlisted'
        
        Returns:
            Dictionary with playlist details and results
        """
        # Create the playlist
        playlist_result = self.create_playlist(title, description, privacy_status)
        
        if not playlist_result.get("success"):
            return playlist_result
        
        playlist_id = playlist_result["playlist_id"]
        
        # Add videos to playlist
        results = {
            "playlist": playlist_result,
            "videos": {
                "total": len(video_urls),
                "added": 0,
                "failed": 0,
                "details": []
            }
        }
        
        for url in video_urls:
            if not url or not url.strip():
                results["videos"]["failed"] += 1
                results["videos"]["details"].append({
                    "success": False,
                    "error": "Empty URL",
                    "video_url": url
                })
                continue
            
            add_result = self.add_video_to_playlist(playlist_id, url.strip())
            results["videos"]["details"].append(add_result)
            
            if add_result.get("success"):
                results["videos"]["added"] += 1
            else:
                results["videos"]["failed"] += 1
        
        results["success"] = True
        results["playlist_url"] = playlist_result["url"]
        
        return results


# Global instance
youtube_creator = YouTubePlaylistCreator()

