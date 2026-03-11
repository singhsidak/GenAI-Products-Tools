"""SQLite database for storing TuneTrace.AI analyses."""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


class Database:
    """SQLite database manager for TuneTrace.AI."""
    
    def __init__(self, db_path: str = "tunetrace.db"):
        """Initialize database connection."""
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize database schema."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create analyses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                input_text TEXT NOT NULL,
                song_name TEXT,
                artist TEXT,
                analysis_data TEXT NOT NULL,
                recommendations TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN DEFAULT 1,
                error_message TEXT
            )
        """)
        
        # Create parameters table for easier searching
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS parameters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER NOT NULL,
                parameter_name TEXT NOT NULL,
                parameter_value TEXT,
                confidence_score REAL,
                FOREIGN KEY (analysis_id) REFERENCES analyses(id)
            )
        """)
        
        # Create recommendations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recommendation_songs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER NOT NULL,
                song_name TEXT NOT NULL,
                artist TEXT NOT NULL,
                rationale TEXT NOT NULL,
                is_wildcard BOOLEAN DEFAULT 0,
                position INTEGER NOT NULL,
                FOREIGN KEY (analysis_id) REFERENCES analyses(id)
            )
        """)
        
        # Create indexes for better performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_analyses_created 
            ON analyses(created_at DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_analyses_song 
            ON analyses(song_name, artist)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_parameters_name 
            ON parameters(parameter_name)
        """)
        
        conn.commit()
        conn.close()
    
    def save_analysis(
        self,
        input_text: str,
        result: dict[str, Any],
        success: bool = True
    ) -> int:
        """
        Save analysis result to database.
        
        Args:
            input_text: Original user input
            result: Complete analysis result
            success: Whether analysis was successful
            
        Returns:
            ID of saved analysis
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Extract data from result
        if success and "input_song_analysis" in result:
            analysis = result["input_song_analysis"]
            song_name = analysis.get("song_name", "Unknown")
            artist = analysis.get("artist", "Unknown")
            parameters = analysis.get("parameters", {})
            recommendations = result.get("recommendations", [])
            error_message = None
        else:
            song_name = None
            artist = None
            parameters = {}
            recommendations = []
            error_message = result.get("error", "Unknown error")
        
        # Insert main analysis record
        cursor.execute("""
            INSERT INTO analyses 
            (input_text, song_name, artist, analysis_data, recommendations, success, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            input_text,
            song_name,
            artist,
            json.dumps(parameters),
            json.dumps(recommendations),
            success,
            error_message
        ))
        
        analysis_id = cursor.lastrowid
        
        # Insert parameters
        if parameters:
            # Handle both dict and list formats
            if isinstance(parameters, dict):
                for param_name, param_data in parameters.items():
                    if isinstance(param_data, dict):
                        cursor.execute("""
                            INSERT INTO parameters 
                            (analysis_id, parameter_name, parameter_value, confidence_score)
                            VALUES (?, ?, ?, ?)
                        """, (
                            analysis_id,
                            param_name,
                            json.dumps(param_data.get("value")),
                            param_data.get("confidence_score")
                        ))
            elif isinstance(parameters, list):
                # If parameters is a list, skip it (malformed data)
                print(f"Warning: Parameters is a list instead of dict for analysis {analysis_id}")
        
        # Insert recommendations
        if recommendations:
            for idx, rec in enumerate(recommendations, 1):
                is_wildcard = "[WILDCARD]" in rec.get("rationale", "")
                cursor.execute("""
                    INSERT INTO recommendation_songs 
                    (analysis_id, song_name, artist, rationale, is_wildcard, position)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    analysis_id,
                    rec.get("song_name", "Unknown"),
                    rec.get("artist", "Unknown"),
                    rec.get("rationale", ""),
                    is_wildcard,
                    idx
                ))
        
        conn.commit()
        conn.close()
        
        return analysis_id
    
    def get_analysis(self, analysis_id: int) -> Optional[dict[str, Any]]:
        """Get a specific analysis by ID."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM analyses WHERE id = ?", (analysis_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return None
        
        result = dict(row)
        result["analysis_data"] = json.loads(result["analysis_data"])
        result["recommendations"] = json.loads(result["recommendations"])
        
        conn.close()
        return result
    
    def get_all_analyses(
        self,
        limit: int = 1000,
        success_only: bool = True
    ) -> list[dict[str, Any]]:
        """
        Get all analyses with full data (for YouTube playlist creation).
        
        Args:
            limit: Maximum number of analyses to return
            success_only: Only return successful analyses
        
        Returns:
            List of analysis dictionaries with parsed JSON data
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM analyses"
        
        if success_only:
            query += " WHERE success = 1"
        
        query += " ORDER BY created_at DESC LIMIT ?"
        
        cursor.execute(query, (limit,))
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            result = dict(row)
            # Parse JSON fields
            try:
                analysis_data = json.loads(result["analysis_data"])
                recommendations = json.loads(result["recommendations"])
                
                # Create input_song_analysis with proper structure
                # (song metadata, not parameters)
                input_song_analysis = {
                    "song_name": result.get("song_name", ""),
                    "artist": result.get("artist", ""),
                    "youtube_url": analysis_data.get("youtube_url", "") if isinstance(analysis_data, dict) else ""
                }
                
                # Create a 'data' field that matches the expected format
                result["data"] = {
                    "input_song_analysis": input_song_analysis,
                    "recommendations": recommendations
                }
                
                # Keep the raw data too
                result["analysis_data"] = analysis_data
                result["recommendations"] = recommendations
                
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                # Skip malformed entries
                print(f"Skipping malformed analysis entry: {e}")
                continue
            
            results.append(result)
        
        conn.close()
        return results
    
    def get_history(
        self,
        limit: int = 50,
        offset: int = 0,
        success_only: bool = True
    ) -> list[dict[str, Any]]:
        """Get analysis history."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT id, input_text, song_name, artist, created_at, success, error_message
            FROM analyses
        """
        
        if success_only:
            query += " WHERE success = 1"
        
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        
        cursor.execute(query, (limit, offset))
        rows = cursor.fetchall()
        
        results = [dict(row) for row in rows]
        conn.close()
        
        return results
    
    def search_analyses(
        self,
        query: str,
        limit: int = 20
    ) -> list[dict[str, Any]]:
        """Search analyses by song name, artist, or input text."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        search_pattern = f"%{query}%"
        
        cursor.execute("""
            SELECT id, input_text, song_name, artist, created_at, success
            FROM analyses
            WHERE (song_name LIKE ? OR artist LIKE ? OR input_text LIKE ?)
            AND success = 1
            ORDER BY created_at DESC
            LIMIT ?
        """, (search_pattern, search_pattern, search_pattern, limit))
        
        rows = cursor.fetchall()
        results = [dict(row) for row in rows]
        conn.close()
        
        return results
    
    def get_parameters_table(
        self, 
        analysis_id: Optional[int] = None,
        limit: int = 100
    ) -> list[dict[str, Any]]:
        """
        Get parameters in tabular format.
        
        Args:
            analysis_id: Optional - filter by specific analysis
            limit: Maximum number of rows to return
            
        Returns:
            List of parameters in tabular format with all details
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if analysis_id:
            cursor.execute("""
                SELECT 
                    p.id,
                    p.analysis_id,
                    a.input_text,
                    a.song_name,
                    a.artist,
                    p.parameter_name,
                    p.parameter_value,
                    p.confidence_score,
                    a.created_at
                FROM parameters p
                JOIN analyses a ON p.analysis_id = a.id
                WHERE p.analysis_id = ?
                ORDER BY p.id ASC
            """, (analysis_id,))
        else:
            cursor.execute("""
                SELECT 
                    p.id,
                    p.analysis_id,
                    a.input_text,
                    a.song_name,
                    a.artist,
                    p.parameter_name,
                    p.parameter_value,
                    p.confidence_score,
                    a.created_at
                FROM parameters p
                JOIN analyses a ON p.analysis_id = a.id
                ORDER BY a.created_at DESC, p.id ASC
                LIMIT ?
            """, (limit,))
        
        rows = cursor.fetchall()
        results = []
        
        for row in rows:
            row_dict = dict(row)
            # Parse JSON value if it's a string
            try:
                row_dict["parameter_value"] = json.loads(row_dict["parameter_value"])
            except:
                pass
            results.append(row_dict)
        
        conn.close()
        return results
    
    def get_all_data_tabular(self) -> dict[str, Any]:
        """
        Get ALL data in complete tabular format.
        Returns input, output, parameters, values, and confidence scores.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get all analyses with parameters
        cursor.execute("""
            SELECT 
                a.id as analysis_id,
                a.input_text,
                a.song_name,
                a.artist,
                a.created_at,
                a.success,
                p.parameter_name,
                p.parameter_value,
                p.confidence_score
            FROM analyses a
            LEFT JOIN parameters p ON a.id = p.analysis_id
            ORDER BY a.created_at DESC, p.id ASC
        """)
        
        rows = cursor.fetchall()
        results = []
        
        for row in rows:
            row_dict = dict(row)
            # Parse JSON value if it's a string
            try:
                if row_dict["parameter_value"]:
                    row_dict["parameter_value"] = json.loads(row_dict["parameter_value"])
            except:
                pass
            results.append(row_dict)
        
        conn.close()
        return {
            "total_rows": len(results),
            "data": results,
            "columns": [
                "analysis_id",
                "input_text",
                "song_name",
                "artist",
                "created_at",
                "success",
                "parameter_name",
                "parameter_value",
                "confidence_score"
            ]
        }
    
    def get_statistics(self) -> dict[str, Any]:
        """Get database statistics."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total analyses
        cursor.execute("SELECT COUNT(*) as count FROM analyses")
        total = cursor.fetchone()["count"]
        
        # Successful analyses
        cursor.execute("SELECT COUNT(*) as count FROM analyses WHERE success = 1")
        successful = cursor.fetchone()["count"]
        
        # Failed analyses
        cursor.execute("SELECT COUNT(*) as count FROM analyses WHERE success = 0")
        failed = cursor.fetchone()["count"]
        
        # Total parameters stored
        cursor.execute("SELECT COUNT(*) as count FROM parameters")
        total_parameters = cursor.fetchone()["count"]
        
        # Most analyzed artists
        cursor.execute("""
            SELECT artist, COUNT(*) as count
            FROM analyses
            WHERE success = 1 AND artist IS NOT NULL
            GROUP BY artist
            ORDER BY count DESC
            LIMIT 10
        """)
        top_artists = [dict(row) for row in cursor.fetchall()]
        
        # Most recommended songs
        cursor.execute("""
            SELECT song_name, artist, COUNT(*) as count
            FROM recommendation_songs
            GROUP BY song_name, artist
            ORDER BY count DESC
            LIMIT 10
        """)
        top_recommendations = [dict(row) for row in cursor.fetchall()]
        
        # Recent activity (last 7 days)
        cursor.execute("""
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM analyses
            WHERE created_at >= datetime('now', '-7 days')
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        """)
        recent_activity = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            "total_analyses": total,
            "successful_analyses": successful,
            "failed_analyses": failed,
            "total_parameters": total_parameters,
            "success_rate": (successful / total * 100) if total > 0 else 0,
            "top_artists": top_artists,
            "top_recommendations": top_recommendations,
            "recent_activity": recent_activity
        }
    
    def delete_analysis(self, analysis_id: int) -> bool:
        """Delete an analysis and its related records."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Delete related records first
        cursor.execute("DELETE FROM parameters WHERE analysis_id = ?", (analysis_id,))
        cursor.execute("DELETE FROM recommendation_songs WHERE analysis_id = ?", (analysis_id,))
        
        # Delete main analysis
        cursor.execute("DELETE FROM analyses WHERE id = ?", (analysis_id,))
        
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return deleted
    
    def clear_all(self) -> dict[str, int]:
        """Clear all data from database (use with caution!)."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as count FROM analyses")
        analyses_count = cursor.fetchone()["count"]
        
        cursor.execute("DELETE FROM recommendation_songs")
        cursor.execute("DELETE FROM parameters")
        cursor.execute("DELETE FROM analyses")
        
        conn.commit()
        conn.close()
        
        return {
            "deleted_analyses": analyses_count
        }


# Singleton database instance
_db_instance: Optional[Database] = None


def get_db() -> Database:
    """Get or create database instance."""
    global _db_instance
    if _db_instance is None:
        db_path = Path(__file__).parent.parent / "tunetrace.db"
        _db_instance = Database(str(db_path))
    return _db_instance

