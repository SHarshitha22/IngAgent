import sqlite3
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

class Database:
    """SQLite database operations for PR review system"""
    
    def __init__(self, db_path: str = "review.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            # Agent outputs table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS agent_outputs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pr_number INTEGER NOT NULL,
                    agent_name TEXT NOT NULL,
                    output_data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(pr_number, agent_name)
                )
            ''')
            
            # Approvals table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS approvals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pr_number INTEGER NOT NULL,
                    approval_step INTEGER NOT NULL,
                    approved BOOLEAN NOT NULL,
                    comment_author TEXT,
                    comment_text TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(pr_number, approval_step)
                )
            ''')
            
            # Halted pipeline table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS halted (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pr_number INTEGER NOT NULL,
                    step_name TEXT NOT NULL,
                    reason TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(pr_number)
                )
            ''')
            
            conn.commit()
    
    def save_agent_output(self, pr_number: int, agent_name: str, output_data: Dict[str, Any]):
        """Save agent output to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO agent_outputs (pr_number, agent_name, output_data)
                VALUES (?, ?, ?)
            ''', (pr_number, agent_name, json.dumps(output_data)))
            conn.commit()
    
    def get_agent_output(self, pr_number: int, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get agent output from database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT output_data FROM agent_outputs 
                WHERE pr_number = ? AND agent_name = ?
            ''', (pr_number, agent_name))
            
            result = cursor.fetchone()
            return json.loads(result[0]) if result else None
    
    def save_approval(self, pr_number: int, approval_step: int, approved: bool, 
                     comment_author: str = None, comment_text: str = None):
        """Save approval decision"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO approvals (pr_number, approval_step, approved, comment_author, comment_text)
                VALUES (?, ?, ?, ?, ?)
            ''', (pr_number, approval_step, approved, comment_author, comment_text))
            conn.commit()
    
    def get_approval(self, pr_number: int, approval_step: int) -> Optional[Dict[str, Any]]:
        """Get approval decision"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT approved, comment_author, comment_text, created_at 
                FROM approvals WHERE pr_number = ? AND approval_step = ?
            ''', (pr_number, approval_step))
            
            result = cursor.fetchone()
            if result:
                return {
                    'approved': bool(result[0]),
                    'comment_author': result[1],
                    'comment_text': result[2],
                    'created_at': result[3]
                }
            return None
    
    def halt_pipeline(self, pr_number: int, step_name: str, reason: str = None):
        """Mark pipeline as halted"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO halted (pr_number, step_name, reason)
                VALUES (?, ?, ?)
            ''', (pr_number, step_name, reason))
            conn.commit()
    
    def is_pipeline_halted(self, pr_number: int) -> bool:
        """Check if pipeline is halted"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT 1 FROM halted WHERE pr_number = ?
            ''', (pr_number,))
            return cursor.fetchone() is not None
    
    def get_all_agent_outputs(self, pr_number: int) -> Dict[str, Any]:
        """Get all agent outputs for a PR"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT agent_name, output_data FROM agent_outputs 
                WHERE pr_number = ? ORDER BY created_at
            ''', (pr_number,))
            
            results = {}
            for agent_name, output_data in cursor.fetchall():
                results[agent_name] = json.loads(output_data)
            return results