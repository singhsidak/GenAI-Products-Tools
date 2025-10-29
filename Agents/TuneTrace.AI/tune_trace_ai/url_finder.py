"""
YouTube URL Finder using Google Search (no API keys required)
Uses Python requests to search and extract first YouTube URL
"""

import re
import requests
from urllib.parse import quote_plus
from typing import Optional


def find_youtube_url_via_search(song_name: str, artist: str) -> Optional[str]:
    """
    Find YouTube URL by constructing a direct YouTube search URL.
    Uses yt-dlp's ytsearch format which is most reliable.
    
    Args:
        song_name: Name of the song
        artist: Name of the artist
        
    Returns:
        YouTube URL or search query string
    """
    try:
        # Create search query
        query = f"{artist} {song_name} official audio"
        
        print(f"🔍 Creating search for: {query}")
        
        # Try to construct YouTube search URL
        # Format: https://www.youtube.com/results?search_query=...
        encoded_query = quote_plus(query)
        youtube_search_url = f"https://www.youtube.com/results?search_query={encoded_query}"
        
        # Make request to get first video from results
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        try:
            response = requests.get(youtube_search_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # Look for video IDs in the response
                video_id_pattern = r'"videoId":"([\w-]{11})"'
                matches = re.findall(video_id_pattern, response.text)
                
                if matches:
                    # Get first video ID and construct URL
                    video_id = matches[0]
                    url = f"https://www.youtube.com/watch?v={video_id}"
                    print(f"✓ Found URL: {url}")
                    return url
        except:
            pass
        
        # Fallback: Return yt-dlp search format
        # This will work directly with yt-dlp
        print(f"→ Using yt-dlp search format")
        return f"ytsearch1:{query}"
            
    except Exception as e:
        # Return search format as last resort
        query = f"{artist} {song_name} official audio"
        print(f"⚠ Error, using search format: {str(e)[:50]}")
        return f"ytsearch1:{query}"


def add_youtube_urls_to_result(result: dict) -> dict:
    """
    Add YouTube URLs to analysis result by searching Google.
    
    Args:
        result: Analysis result dictionary
        
    Returns:
        Updated result with YouTube URLs
    """
    try:
        # Add URL to input song
        if 'input_song_analysis' in result:
            input_song = result['input_song_analysis']
            song_name = input_song.get('song_name', '')
            artist = input_song.get('artist', '')
            
            if song_name and artist:
                url = find_youtube_url_via_search(song_name, artist)
                result['input_song_analysis']['youtube_url'] = url or ""
        
        # Add URLs to recommendations
        if 'recommendations' in result:
            for i, rec in enumerate(result['recommendations'], 1):
                song_name = rec.get('song_name', '')
                artist = rec.get('artist', '')
                
                if song_name and artist:
                    print(f"\n🎵 Finding URL for recommendation {i}/{len(result['recommendations'])}")
                    url = find_youtube_url_via_search(song_name, artist)
                    rec['youtube_url'] = url or ""
        
        return result
        
    except Exception as e:
        print(f"Warning: Failed to add YouTube URLs: {str(e)}")
        return result

