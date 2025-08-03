"""
Database Manager for ADF Monitoring System
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from config import config

@dataclass
class PipelineRun:
    """Pipeline run data structure"""
    run_id: str
    pipeline_name: str
    status: str
    start_time: datetime
    end_time: Optional[datetime]
    error_message: Optional[str]
    factory_name: str

@dataclass
class MonitoringAction:
    """Monitoring action data structure"""
    action_id: str
    run_id: str
    action_type: str  # 'retry', 'alert', 'manual_intervention'
    ai_analysis: Optional[str]
    decision_reason: str
    action_taken: bool
    timestamp: datetime

class DatabaseManager:
    """Manages SQLite database for ADF monitoring"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or config.database.database_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Pipeline runs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pipeline_runs (
                    run_id TEXT PRIMARY KEY,
                    pipeline_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP,
                    error_message TEXT,
                    factory_name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Monitoring actions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS monitoring_actions (
                    action_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    ai_analysis TEXT,
                    decision_reason TEXT NOT NULL,
                    action_taken BOOLEAN NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (run_id) REFERENCES pipeline_runs (run_id)
                )
            ''')
            
            # Error patterns table for learning
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS error_patterns (
                    pattern_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    error_pattern TEXT NOT NULL,
                    suggested_action TEXT NOT NULL,
                    success_rate REAL DEFAULT 0.0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def insert_pipeline_run(self, pipeline_run: PipelineRun) -> bool:
        """Insert or update pipeline run"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO pipeline_runs 
                    (run_id, pipeline_name, status, start_time, end_time, error_message, factory_name)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    pipeline_run.run_id,
                    pipeline_run.pipeline_name,
                    pipeline_run.status,
                    pipeline_run.start_time,
                    pipeline_run.end_time,
                    pipeline_run.error_message,
                    pipeline_run.factory_name
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error inserting pipeline run: {e}")
            return False
    
    def insert_monitoring_action(self, action: MonitoringAction) -> bool:
        """Insert monitoring action"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO monitoring_actions 
                    (action_id, run_id, action_type, ai_analysis, decision_reason, action_taken, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    action.action_id,
                    action.run_id,
                    action.action_type,
                    action.ai_analysis,
                    action.decision_reason,
                    action.action_taken,
                    action.timestamp
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error inserting monitoring action: {e}")
            return False
    
    def get_failed_runs_last_hours(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get failed pipeline runs from last N hours"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM pipeline_runs 
                    WHERE status = 'Failed' 
                    AND start_time >= datetime('now', '-{} hours')
                    ORDER BY start_time DESC
                '''.format(hours))
                
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error getting failed runs: {e}")
            return []
    
    def get_retry_history(self, pipeline_name: str, hours: int = 168) -> List[Dict[str, Any]]:
        """Get retry history for a pipeline (last week by default)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT ma.*, pr.pipeline_name 
                    FROM monitoring_actions ma
                    JOIN pipeline_runs pr ON ma.run_id = pr.run_id
                    WHERE pr.pipeline_name = ? 
                    AND ma.action_type = 'retry'
                    AND ma.timestamp >= datetime('now', '-{} hours')
                    ORDER BY ma.timestamp DESC
                '''.format(hours), (pipeline_name,))
                
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error getting retry history: {e}")
            return []
    
    def update_error_pattern_success_rate(self, error_pattern: str, success: bool):
        """Update success rate for error pattern"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if pattern exists
                cursor.execute('SELECT success_rate FROM error_patterns WHERE error_pattern = ?', (error_pattern,))
                result = cursor.fetchone()
                
                if result:
                    # Update existing pattern
                    current_rate = result[0]
                    new_rate = (current_rate + (1.0 if success else 0.0)) / 2
                    cursor.execute('''
                        UPDATE error_patterns 
                        SET success_rate = ?, last_updated = CURRENT_TIMESTAMP 
                        WHERE error_pattern = ?
                    ''', (new_rate, error_pattern))
                else:
                    # Insert new pattern
                    cursor.execute('''
                        INSERT INTO error_patterns (error_pattern, suggested_action, success_rate)
                        VALUES (?, ?, ?)
                    ''', (error_pattern, 'retry', 1.0 if success else 0.0))
                
                conn.commit()
        except Exception as e:
            print(f"Error updating error pattern: {e}")
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # Total runs today
                cursor.execute('''
                    SELECT COUNT(*) FROM pipeline_runs 
                    WHERE DATE(start_time) = DATE('now')
                ''')
                stats['total_runs_today'] = cursor.fetchone()[0]
                
                # Failed runs today
                cursor.execute('''
                    SELECT COUNT(*) FROM pipeline_runs 
                    WHERE status = 'Failed' AND DATE(start_time) = DATE('now')
                ''')
                stats['failed_runs_today'] = cursor.fetchone()[0]
                
                # Success rate
                if stats['total_runs_today'] > 0:
                    stats['success_rate_today'] = ((stats['total_runs_today'] - stats['failed_runs_today']) / stats['total_runs_today']) * 100
                else:
                    stats['success_rate_today'] = 100.0
                
                # Auto-retries today
                cursor.execute('''
                    SELECT COUNT(*) FROM monitoring_actions 
                    WHERE action_type = 'retry' AND DATE(timestamp) = DATE('now')
                ''')
                stats['auto_retries_today'] = cursor.fetchone()[0]
                
                return stats
        except Exception as e:
            print(f"Error getting dashboard stats: {e}")
            return {}

# Global database manager instance
db_manager = DatabaseManager()
