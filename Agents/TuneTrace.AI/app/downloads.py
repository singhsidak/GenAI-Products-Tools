"""
Download manager for playlist downloads using yt-dlp.
Handles sequential downloads with progress tracking.
"""

import os
import asyncio
from pathlib import Path
from typing import Dict, List, Optional
import yt_dlp
from datetime import datetime


class DownloadManager:
    """Manages playlist downloads with progress tracking"""
    
    def __init__(self, base_playlist_dir: str = "playlists"):
        self.base_dir = Path(__file__).parent.parent / base_playlist_dir
        self.base_dir.mkdir(exist_ok=True)
        self.active_downloads: Dict[str, Dict] = {}
    
    def get_playlist_dir(self, playlist_name: str) -> Path:
        """Get or create playlist directory"""
        playlist_dir = self.base_dir / playlist_name
        playlist_dir.mkdir(parents=True, exist_ok=True)
        return playlist_dir
    
    async def download_playlist(
        self,
        download_id: str,
        playlist_name: str,
        songs: List[Dict[str, str]],
        download_type: str = 'audio',  # 'audio' or 'video'
        progress_callback=None
    ):
        """
        Download multiple songs sequentially
        
        Args:
            download_id: Unique ID for this download session
            playlist_name: Name of the playlist folder
            songs: List of dicts with 'title', 'artist', 'url' keys
            progress_callback: Async callback for progress updates
        """
        playlist_dir = self.get_playlist_dir(playlist_name)
        
        total_songs = len(songs)
        
        # Initialize download tracking
        self.active_downloads[download_id] = {
            "status": "starting",
            "total": total_songs,
            "current": 0,
            "current_song": None,
            "completed": [],
            "failed": [],
            "started_at": datetime.now().isoformat()
        }
        
        if progress_callback:
            await progress_callback({
                "type": "started",
                "download_id": download_id,
                "total_songs": total_songs,
                "playlist_name": playlist_name
            })
        
        # Download each song sequentially
        for index, song in enumerate(songs, 1):
            song_title = f"{song['artist']} - {song['title']}"
            
            self.active_downloads[download_id].update({
                "status": "downloading",
                "current": index,
                "current_song": song_title
            })
            
            if progress_callback:
                await progress_callback({
                    "type": "song_start",
                    "download_id": download_id,
                    "song_index": index,
                    "song_title": song_title,
                    "total_songs": total_songs
                })
            
            try:
                # Check if URL is provided and valid
                song_url = song.get('url', '').strip()
                
                # If no URL provided, go straight to search
                if not song_url or song_url == '':
                    print(f"No URL provided for {song_title}, using search")
                    song_url = None
                
                # Download the song
                success = await self._download_song(
                    song_url,
                    playlist_dir,
                    song_title,
                    song['title'],
                    song['artist'],
                    download_id,
                    download_type,
                    progress_callback
                )
                
                if success:
                    self.active_downloads[download_id]["completed"].append(song_title)
                    if progress_callback:
                        await progress_callback({
                            "type": "song_complete",
                            "download_id": download_id,
                            "song_index": index,
                            "song_title": song_title,
                            "status": "success"
                        })
                else:
                    self.active_downloads[download_id]["failed"].append(song_title)
                    if progress_callback:
                        await progress_callback({
                            "type": "song_complete",
                            "download_id": download_id,
                            "song_index": index,
                            "song_title": song_title,
                            "status": "failed"
                        })
            
            except Exception as e:
                self.active_downloads[download_id]["failed"].append(song_title)
                if progress_callback:
                    await progress_callback({
                        "type": "song_error",
                        "download_id": download_id,
                        "song_index": index,
                        "song_title": song_title,
                        "error": str(e)
                    })
        
        # Final status
        self.active_downloads[download_id]["status"] = "completed"
        self.active_downloads[download_id]["completed_at"] = datetime.now().isoformat()
        
        if progress_callback:
            await progress_callback({
                "type": "complete",
                "download_id": download_id,
                "total_songs": total_songs,
                "successful": len(self.active_downloads[download_id]["completed"]),
                "failed": len(self.active_downloads[download_id]["failed"]),
                "playlist_path": str(playlist_dir)
            })
        
        return self.active_downloads[download_id]
    
    def _generate_search_url(self, song_title: str, artist: str) -> str:
        """Generate YouTube search URL as fallback"""
        query = f"{song_title} {artist} official audio".replace(' ', '+')
        return f"ytsearch1:{query}"
    
    async def _download_song(
        self,
        url: str | None,
        output_dir: Path,
        song_title: str,
        title: str,
        artist: str,
        download_id: str,
        download_type: str,
        progress_callback=None
    ) -> bool:
        """Download a single song using yt-dlp (EXACT method from youtube_downloader.py)"""
        
        def progress_hook(d):
            """yt-dlp progress hook"""
            if d['status'] == 'downloading':
                # Extract progress info
                if 'downloaded_bytes' in d and 'total_bytes' in d:
                    percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                elif '_percent_str' in d:
                    percent_str = d['_percent_str'].strip().replace('%', '')
                    try:
                        percent = float(percent_str)
                    except:
                        percent = 0
                else:
                    percent = 0
                
                # Schedule async callback
                if progress_callback:
                    asyncio.create_task(progress_callback({
                        "type": "song_progress",
                        "download_id": download_id,
                        "song_title": song_title,
                        "progress": round(percent, 1),
                        "speed": d.get('speed', 0),
                        "eta": d.get('eta', 0)
                    }))
        
        # EXACT configurations from youtube_downloader.py
        if download_type == 'video':
            # VIDEO: Lines 76-87 from youtube_downloader.py
            ydl_opts = {
                'format': 'bestvideo+bestaudio/best',
                'outtmpl': str(output_dir / '%(title)s.%(ext)s'),
                'merge_output_format': 'mp4',
                'quiet': False,
                'no_warnings': False,
                'progress_hooks': [progress_hook],
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }],
            }
            file_extension = 'mp4'
        else:
            # AUDIO: Lines 118-129 from youtube_downloader.py
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': str(output_dir / '%(title)s.%(ext)s'),
                'quiet': False,
                'no_warnings': False,
                'progress_hooks': [progress_hook],
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '320',  # 320kbps - Highest MP3 quality
                }],
            }
            file_extension = 'mp3'
        
        # Track which files exist BEFORE download
        existing_files = set(output_dir.glob(f'*.{file_extension}'))
        
        def do_download(download_url):
            """Download using YT-Downloads method - .download() not extract_info()"""
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Use .download() like YT-Downloads does (lines 91-92, 132-134)
                ydl.download([download_url])
                return True
        
        loop = asyncio.get_event_loop()
        
        # If no URL provided, go straight to search
        if url is None or url == '':
            print(f"📌 No URL provided for {song_title}, using YouTube search...")
            search_query = self._generate_search_url(title, artist)
            print(f"   Search query: {search_query}")
            try:
                await loop.run_in_executor(None, do_download, search_query)
                
                # Wait for FFmpeg processing
                await asyncio.sleep(3)
                
                # Find NEW files that weren't there before
                current_files = set(output_dir.glob(f'*.{file_extension}'))
                new_files = current_files - existing_files
                
                if new_files:
                    new_file = list(new_files)[0]  # Get the newly created file
                    print(f"✅ Successfully downloaded via search: {song_title}")
                    print(f"   File: {new_file.name}")
                    print(f"   Size: {new_file.stat().st_size / (1024*1024):.2f} MB")
                    return True
                else:
                    print(f"❌ No NEW {file_extension.upper()} file found after search download")
                    print(f"   Expected new file, but none appeared in {output_dir}")
                    return False
                    
            except Exception as e:
                print(f"❌ Search download failed for {song_title}: {str(e)[:150]}")
                return False
        
        # Try the provided URL first
        try:
            print(f"📥 Attempting {'VIDEO' if download_type == 'video' else 'AUDIO'} download: {song_title}")
            print(f"   URL: {url}")
            
            # Download using YT-Downloads method (.download())
            await loop.run_in_executor(None, do_download, url)
            
            # Wait for FFmpeg processing
            await asyncio.sleep(3)
            
            # Find NEW files that weren't there before
            current_files = set(output_dir.glob(f'*.{file_extension}'))
            new_files = current_files - existing_files
            
            if new_files:
                new_file = list(new_files)[0]  # Get the newly created file
                print(f"✅ Successfully downloaded: {song_title}")
                print(f"   File: {new_file.name}")
                print(f"   Size: {new_file.stat().st_size / (1024*1024):.2f} MB")
                return True
            else:
                print(f"⚠️  Download completed but no NEW {file_extension.upper()} file found")
                print(f"   Existing files: {len(existing_files)}, Current files: {len(current_files)}")
                raise Exception(f"No NEW {file_extension.upper()} file created after download")
                
        except Exception as e:
            error_msg = str(e)
            print(f"\n{'='*60}")
            print(f"⚠️  DIRECT URL FAILED for: {song_title}")
            print(f"{'='*60}")
            print(f"   URL: {url}")
            print(f"   Error Type: {type(e).__name__}")
            print(f"   Error Message: {error_msg[:200]}")
            
            # Check for common errors
            if "Video unavailable" in error_msg:
                print(f"   ⚠️  Video is unavailable (removed, private, or region-locked)")
            elif "Signature extraction failed" in error_msg:
                print(f"   ⚠️  YouTube signature extraction issue (try updating yt-dlp)")
            elif "Requested format is not available" in error_msg:
                print(f"   ⚠️  The requested format is not available for this video")
            elif "HTTP Error 403" in error_msg or "Forbidden" in error_msg:
                print(f"   ⚠️  Access forbidden (might be region-locked or bot-detected)")
            
            # Try fallback: YouTube search
            print(f"\n🔄 Trying search fallback for: {song_title}")
            search_query = self._generate_search_url(title, artist)
            print(f"   Search query: {search_query}")
            try:
                await loop.run_in_executor(None, do_download, search_query)
                
                # Wait for FFmpeg processing
                await asyncio.sleep(3)
                
                # Find NEW files that weren't there before
                current_files = set(output_dir.glob(f'*.{file_extension}'))
                new_files = current_files - existing_files
                
                if new_files:
                    new_file = list(new_files)[0]  # Get the newly created file
                    print(f"✅ Successfully downloaded via search: {song_title}")
                    print(f"   File: {new_file.name}")
                    print(f"   Size: {new_file.stat().st_size / (1024*1024):.2f} MB")
                    return True
                else:
                    print(f"❌ Search fallback: No NEW {file_extension.upper()} file created")
                    print(f"   Existing files: {len(existing_files)}, Current files: {len(current_files)}")
                    return False
                    
            except Exception as e2:
                print(f"❌ Search fallback also failed:")
                print(f"   Error: {str(e2)[:150]}")
                return False
    
    def get_download_status(self, download_id: str) -> Optional[Dict]:
        """Get current status of a download"""
        return self.active_downloads.get(download_id)


# Global download manager instance
download_manager = DownloadManager()

