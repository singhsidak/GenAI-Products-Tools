"""FastAPI backend for TuneTrace.AI web interface."""

import json
import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ Loaded API key from .env file")
else:
    # Try loading from current directory
    load_dotenv()

# Add parent directory to Python path
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import uuid

from tune_trace_ai import create_agent
from app.database import get_db
from app.downloads import download_manager
from app.youtube_playlist import youtube_creator

app = FastAPI(title="TuneTrace.AI API", version="2.0.0")

# CORS configuration for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SongInput(BaseModel):
    """Request model for song analysis."""
    input: str
    description: str = ""


class BatchInput(BaseModel):
    """Request model for batch analysis."""
    songs: list[str]


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "TuneTrace.AI",
        "version": "2.0.0",
        "description": "Music Analysis & Recommendation System with SQLite Storage",
        "endpoints": {
            "/analyze": "Analyze a single song (auto-saved to database)",
            "/more-recommendations": "Get additional 6 recommendations for a song",
            "/batch": "Analyze multiple songs",
            "/history": "Get analysis history",
            "/history/{id}": "Get specific analysis by ID",
            "/search": "Search analyses by query",
            "/statistics": "Get usage statistics and insights",
            "/table": "Get all data in tabular format",
            "/table/parameters": "Get parameters table with values & confidence scores",
            "/table/parameters/{analysis_id}": "Get parameters for specific analysis",
            "/download-playlist": "Start downloading a playlist (POST)",
            "/download-progress/{id}": "Stream download progress via SSE",
            "/download-status/{id}": "Get current download status",
            "/create-youtube-playlist": "Create a YouTube playlist from analyzed songs (POST)",
            "/youtube-auth-status": "Check YouTube API authentication status",
            "/examples": "Get example songs",
            "/health": "Health check",
            "/docs": "Interactive API documentation"
        },
        "features": {
            "persistent_storage": True,
            "database": "SQLite",
            "auto_save": True,
            "tabular_view": True
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    api_key = os.environ.get("GOOGLE_API_KEY")
    return {
        "status": "healthy",
        "api_key_configured": bool(api_key),
        "service": "TuneTrace.AI"
    }


@app.post("/analyze")
async def analyze_song(song_input: SongInput) -> dict[str, Any]:
    """
    Analyze a song and get recommendations.
    
    Args:
        song_input: Song name, artist, or URL
        
    Returns:
        Complete analysis with 20 parameters and 3 recommendations
    """
    try:
        # Check for API key
        if not os.environ.get("GOOGLE_API_KEY"):
            raise HTTPException(
                status_code=500,
                detail="GOOGLE_API_KEY environment variable not set"
            )
        
        # Create agent and analyze
        agent = create_agent()
        result = agent.analyze_song(song_input.input)
        
        # Get database instance
        db = get_db()
        
        # Check for errors in result
        if "error" in result and "input_song_analysis" not in result:
            # Save failed analysis
            analysis_id = db.save_analysis(
                input_text=song_input.input,
                result=result,
                success=False
            )
            
            return {
                "success": False,
                "error": result["error"] if isinstance(result, dict) else str(result),
                "input": song_input.input,
                "analysis_id": analysis_id
            }
        
        # Save successful analysis
        analysis_id = db.save_analysis(
            input_text=song_input.input,
            result=result,
            success=True
        )
        
        return {
            "success": True,
            "data": result,
            "input": song_input.input,
            "analysis_id": analysis_id
        }
        
    except Exception as e:
        # Log the error for debugging
        import traceback
        traceback.print_exc()
        
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@app.post("/batch")
async def batch_analyze(batch_input: BatchInput) -> dict[str, Any]:
    """
    Analyze multiple songs in batch.
    
    Args:
        batch_input: List of song names, artists, or URLs
        
    Returns:
        Batch analysis results
    """
    try:
        # Check for API key
        if not os.environ.get("GOOGLE_API_KEY"):
            raise HTTPException(
                status_code=500,
                detail="GOOGLE_API_KEY environment variable not set"
            )
        
        # Create agent and analyze
        agent = create_agent()
        result = agent.analyze_batch(batch_input.songs)
        
        return {
            "success": True,
            "data": result,
            "count": len(batch_input.songs)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Batch analysis failed: {str(e)}"
        )


@app.post("/more-recommendations")
async def get_more_recommendations(song_input: SongInput) -> dict[str, Any]:
    """
    Get additional recommendations for a song.
    Similar to /analyze but focuses on generating fresh recommendations.
    
    Args:
        song_input: Song name, artist, or URL
        
    Returns:
        6 new recommendations with full parameter analysis
    """
    try:
        # Check for API key
        if not os.environ.get("GOOGLE_API_KEY"):
            raise HTTPException(
                status_code=500,
                detail="GOOGLE_API_KEY environment variable not set"
            )
        
        # Create agent and analyze to get fresh recommendations
        agent = create_agent()
        result = agent.analyze_song(song_input.input)
        
        # Check for errors in result
        if "error" in result and "input_song_analysis" not in result:
            return {
                "success": False,
                "error": result["error"] if isinstance(result, dict) else str(result),
                "input": song_input.input
            }
        
        return {
            "success": True,
            "data": result,
            "input": song_input.input,
            "message": "Generated new recommendations"
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate more recommendations: {str(e)}"
        )


@app.get("/examples")
async def get_examples():
    """Get example songs for testing."""
    return {
        "examples": [
            {
                "name": "Lose Yourself by Eminem",
                "description": "High-energy motivational rap"
            },
            {
                "name": "Bohemian Rhapsody by Queen",
                "description": "Classic rock opera"
            },
            {
                "name": "Blinding Lights by The Weeknd",
                "description": "Modern synth-pop"
            },
            {
                "name": "Smells Like Teen Spirit by Nirvana",
                "description": "Grunge rock anthem"
            },
            {
                "name": "https://www.youtube.com/watch?v=_Yhyp-_hX2s",
                "description": "URL input example"
            }
        ]
    }


@app.get("/history")
async def get_history(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    success_only: bool = Query(True)
):
    """
    Get analysis history.
    
    Args:
        limit: Maximum number of results (1-100)
        offset: Number of results to skip
        success_only: Only return successful analyses
        
    Returns:
        List of past analyses
    """
    db = get_db()
    history = db.get_history(limit=limit, offset=offset, success_only=success_only)
    
    return {
        "success": True,
        "count": len(history),
        "limit": limit,
        "offset": offset,
        "history": history
    }


@app.get("/history/{analysis_id}")
async def get_analysis_by_id(analysis_id: int):
    """
    Get a specific analysis by ID.
    
    Args:
        analysis_id: ID of the analysis
        
    Returns:
        Complete analysis details
    """
    db = get_db()
    analysis = db.get_analysis(analysis_id)
    
    if not analysis:
        raise HTTPException(
            status_code=404,
            detail=f"Analysis {analysis_id} not found"
        )
    
    return {
        "success": True,
        "analysis": analysis
    }


@app.get("/search")
async def search_analyses(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Search analyses by song name, artist, or input text.
    
    Args:
        q: Search query
        limit: Maximum number of results
        
    Returns:
        Matching analyses
    """
    db = get_db()
    results = db.search_analyses(query=q, limit=limit)
    
    return {
        "success": True,
        "query": q,
        "count": len(results),
        "results": results
    }


@app.get("/statistics")
async def get_statistics():
    """
    Get database statistics and insights.
    
    Returns:
        Usage statistics, top artists, recommendations, etc.
    """
    db = get_db()
    stats = db.get_statistics()
    
    return {
        "success": True,
        "statistics": stats
    }


@app.delete("/history/{analysis_id}")
async def delete_analysis(analysis_id: int):
    """
    Delete a specific analysis.
    
    Args:
        analysis_id: ID of the analysis to delete
        
    Returns:
        Success confirmation
    """
    db = get_db()
    deleted = db.delete_analysis(analysis_id)
    
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Analysis {analysis_id} not found"
        )
    
    return {
        "success": True,
        "message": f"Analysis {analysis_id} deleted successfully"
    }


@app.post("/clear")
async def clear_database(confirm: str = Query("", description="Type 'DELETE_ALL' to confirm")):
    """
    Clear all data from database (use with caution!).
    
    Args:
        confirm: Must be 'DELETE_ALL' to proceed
        
    Returns:
        Number of deleted records
    """
    if confirm != "DELETE_ALL":
        raise HTTPException(
            status_code=400,
            detail="Must provide confirm='DELETE_ALL' to clear database"
        )
    
    db = get_db()
    result = db.clear_all()
    
    return {
        "success": True,
        "message": "Database cleared successfully",
        **result
    }


@app.get("/table")
async def get_table_view():
    """
    Get ALL data in complete tabular format.
    Returns input, output, parameters, values, and confidence scores.
    
    Perfect for viewing in Excel or data analysis tools.
    Each row shows: analysis_id, input_text, song_name, artist, 
    created_at, success, parameter_name, parameter_value, confidence_score
    """
    db = get_db()
    data = db.get_all_data_tabular()
    
    return {
        "success": True,
        "description": "Complete tabular view of all analyses",
        **data
    }


@app.get("/table/parameters")
async def get_parameters_table(
    limit: int = Query(100, ge=1, le=1000, description="Maximum rows to return")
):
    """
    Get parameters table showing all parameter values and confidence scores.
    
    Args:
        limit: Maximum number of rows to return (default: 100)
        
    Returns:
        Tabular data of all parameters with:
        - analysis_id: Which analysis this belongs to
        - input_text: Original user input
        - song_name: Analyzed song name
        - artist: Song artist
        - parameter_name: Name of the parameter (e.g., "Tempo (BPM)")
        - parameter_value: Value of the parameter
        - confidence_score: AI confidence (0.0 to 1.0)
        - created_at: Timestamp
    """
    db = get_db()
    data = db.get_parameters_table(limit=limit)
    
    return {
        "success": True,
        "count": len(data),
        "limit": limit,
        "data": data,
        "columns": [
            "id",
            "analysis_id",
            "input_text",
            "song_name",
            "artist",
            "parameter_name",
            "parameter_value",
            "confidence_score",
            "created_at"
        ]
    }


@app.get("/table/parameters/{analysis_id}")
async def get_parameters_for_analysis(analysis_id: int):
    """
    Get all parameters for a specific analysis in tabular format.
    Shows all 20 parameters with their values and confidence scores.
    
    Args:
        analysis_id: ID of the analysis
        
    Returns:
        Tabular data of parameters for the specified analysis
    """
    db = get_db()
    data = db.get_parameters_table(analysis_id=analysis_id)
    
    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"No parameters found for analysis {analysis_id}"
        )
    
    return {
        "success": True,
        "analysis_id": analysis_id,
        "count": len(data),
        "data": data,
        "columns": [
            "id",
            "analysis_id",
            "input_text",
            "song_name",
            "artist",
            "parameter_name",
            "parameter_value",
            "confidence_score",
            "created_at"
        ]
    }


# ================== DOWNLOAD ENDPOINTS ==================

class DownloadPlaylistRequest(BaseModel):
    """Request model for playlist download"""
    playlist_name: str
    songs: list[dict[str, str]]  # List of {title, artist, youtube_url}
    download_type: str = 'audio'  # 'audio' or 'video'


@app.post("/download-playlist")
async def start_playlist_download(request: DownloadPlaylistRequest) -> dict[str, Any]:
    """
    Start a playlist download and return a download ID.
    Client should then connect to /download-progress/{download_id} for updates.
    
    Request body:
    {
        "playlist_name": "My Awesome Playlist",
        "songs": [
            {"title": "Song 1", "artist": "Artist 1", "youtube_url": "https://..."},
            {"title": "Song 2", "artist": "Artist 2", "youtube_url": "https://..."}
        ]
    }
    
    Returns:
    {
        "success": true,
        "download_id": "unique-id",
        "message": "Download started"
    }
    """
    try:
        # Generate unique download ID
        download_id = str(uuid.uuid4())
        
        # Validate songs have required fields
        for song in request.songs:
            if not all(k in song for k in ['title', 'artist', 'youtube_url']):
                raise HTTPException(
                    status_code=400,
                    detail="Each song must have 'title', 'artist', and 'youtube_url' fields"
                )
            
            if not song['youtube_url']:
                raise HTTPException(
                    status_code=400,
                    detail=f"Song '{song['title']}' is missing YouTube URL"
                )
        
        # Start download in background
        asyncio.create_task(
            download_manager.download_playlist(
                download_id=download_id,
                playlist_name=request.playlist_name,
                songs=[{
                    'title': s['title'],
                    'artist': s['artist'],
                    'url': s['youtube_url']
                } for s in request.songs],
                download_type=request.download_type,  # 'audio' or 'video'
                progress_callback=None  # Will be handled by SSE endpoint
            )
        )
        
        return {
            "success": True,
            "download_id": download_id,
            "message": "Download started",
            "total_songs": len(request.songs)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start download: {str(e)}"
        )


@app.get("/download-progress/{download_id}")
async def download_progress_stream(download_id: str):
    """
    SSE endpoint for real-time download progress.
    Client connects to this to receive progress updates.
    
    Returns Server-Sent Events stream with progress updates.
    """
    
    async def event_stream():
        """Generate SSE events for download progress"""
        try:
            # Wait for download to start
            max_wait = 30
            waited = 0
            while waited < max_wait:
                status = download_manager.get_download_status(download_id)
                if status:
                    break
                await asyncio.sleep(0.5)
                waited += 0.5
            
            if not status:
                yield f"data: {json.dumps({'type': 'error', 'message': 'Download not found'})}\n\n"
                return
            
            # Send initial status
            yield f"data: {json.dumps({'type': 'connected', 'download_id': download_id})}\n\n"
            
            # Monitor progress
            last_status = None
            completed = False
            
            while not completed:
                status = download_manager.get_download_status(download_id)
                
                if not status:
                    yield f"data: {json.dumps({'type': 'error', 'message': 'Download lost'})}\n\n"
                    break
                
                # Send update if status changed
                if status != last_status:
                    yield f"data: {json.dumps(status)}\n\n"
                    last_status = dict(status)
                
                # Check if completed
                if status.get('status') == 'completed':
                    completed = True
                    yield f"data: {json.dumps({'type': 'complete', 'data': status})}\n\n"
                    break
                
                await asyncio.sleep(1)
        
        except asyncio.CancelledError:
            yield f"data: {json.dumps({'type': 'disconnected'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.get("/download-status/{download_id}")
async def get_download_status(download_id: str) -> dict[str, Any]:
    """
    Get current status of a download (non-streaming).
    
    Returns:
    {
        "success": true,
        "status": { ... download status ... }
    }
    """
    status = download_manager.get_download_status(download_id)
    
    if not status:
        raise HTTPException(
            status_code=404,
            detail="Download not found"
        )
    
    return {
        "success": True,
        "status": status
    }


# ================== YOUTUBE PLAYLIST ENDPOINTS ==================

class CreateYouTubePlaylistRequest(BaseModel):
    """Request model for YouTube playlist creation"""
    title: str
    description: str = ""
    source: str = "all"  # 'all' (all history), 'current' (current analysis), or list of IDs


@app.post("/create-youtube-playlist")
async def create_youtube_playlist(request: CreateYouTubePlaylistRequest) -> dict[str, Any]:
    """
    Create a public YouTube playlist from analyzed songs.
    
    Request body:
    {
        "title": "My TuneTrace.AI Playlist",
        "description": "Generated from TuneTrace.AI analysis",
        "source": "all"  // 'all' for all history, 'current' for current analysis
    }
    
    Returns:
    {
        "success": true,
        "playlist_url": "https://www.youtube.com/playlist?list=...",
        "playlist_id": "...",
        "videos": {
            "total": 10,
            "added": 8,
            "failed": 2,
            "details": [...]
        }
    }
    """
    try:
        db = get_db()
        
        # Fetch all analyzed songs from database
        if request.source == "all":
            # Get all analyses from history
            analyses = db.get_all_analyses(limit=1000)  # Limit to 1000 most recent
            
            if not analyses:
                raise HTTPException(
                    status_code=404,
                    detail="No analyzed songs found in database"
                )
            
            # Extract YouTube URLs from analyses
            video_urls = []
            for analysis in analyses:
                data = analysis.get('data', {})
                
                # Get input song URL
                input_song = data.get('input_song_analysis', {})
                if input_song.get('youtube_url'):
                    video_urls.append(input_song['youtube_url'])
                
                # Get recommendation URLs
                recommendations = data.get('recommendations', [])
                for rec in recommendations:
                    if rec.get('youtube_url'):
                        video_urls.append(rec['youtube_url'])
            
            # Remove duplicates while preserving order
            seen = set()
            unique_urls = []
            for url in video_urls:
                if url and url not in seen:
                    seen.add(url)
                    unique_urls.append(url)
            
            video_urls = unique_urls
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported source: {request.source}. Use 'all' for now."
            )
        
        if not video_urls:
            raise HTTPException(
                status_code=404,
                detail="No YouTube URLs found in analyzed songs"
            )
        
        # Create the playlist
        print(f"\n{'='*60}")
        print(f"🎵 Creating YouTube Playlist: '{request.title}'")
        print(f"{'='*60}")
        print(f"   Description: {request.description}")
        print(f"   Total videos: {len(video_urls)}")
        print(f"   Privacy: public")
        
        result = youtube_creator.create_playlist_from_urls(
            title=request.title,
            video_urls=video_urls,
            description=request.description or f"Generated by TuneTrace.AI - {len(video_urls)} songs",
            privacy_status="public"
        )
        
        if result.get("success"):
            print(f"\n✅ Playlist created successfully!")
            print(f"   URL: {result['playlist_url']}")
            print(f"   Added: {result['videos']['added']}/{result['videos']['total']} videos")
            if result['videos']['failed'] > 0:
                print(f"   Failed: {result['videos']['failed']} videos")
        
        return result
    
    except HTTPException:
        raise
    except FileNotFoundError as e:
        # OAuth credentials not found
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create YouTube playlist: {str(e)}"
        )


@app.get("/youtube-auth-status")
async def youtube_auth_status() -> dict[str, Any]:
    """
    Check if YouTube API credentials are configured.
    
    Returns:
    {
        "authenticated": true/false,
        "message": "..."
    }
    """
    try:
        token_path = Path(__file__).parent.parent / "youtube_token.pickle"
        client_secret_path = Path(__file__).parent.parent / "client_secret.json"
        
        return {
            "authenticated": token_path.exists(),
            "credentials_configured": client_secret_path.exists(),
            "message": "YouTube API is ready" if token_path.exists() else "Authentication required"
        }
    except Exception as e:
        return {
            "authenticated": False,
            "credentials_configured": False,
            "message": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

