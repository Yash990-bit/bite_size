"""
Local Persistent Storage for BiteSize Agent (SQLite).
Preserves user sessions, completed micro-steps, historical streaks, and dopamine scores.
100% private and stored locally on the user's machine.
"""
import sqlite3
import json
import os
from typing import List, Dict, Any, Optional
from pathlib import Path


class LocalStorage:
    def __init__(self, db_path: str = "bitesize_history.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_name TEXT,
                    original_dump TEXT,
                    perceived_mountain TEXT,
                    core_blocker TEXT,
                    total_steps INTEGER,
                    completed_steps INTEGER,
                    dopamine_earned INTEGER
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS completed_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    step_id TEXT,
                    title TEXT,
                    domain TEXT,
                    seconds_spent INTEGER,
                    dopamine_points INTEGER,
                    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(session_id) REFERENCES sessions(id)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_profile (
                    user_name TEXT PRIMARY KEY,
                    all_time_dopamine INTEGER DEFAULT 0,
                    highest_streak INTEGER DEFAULT 0,
                    total_conquered_tasks INTEGER DEFAULT 0
                )
            """)
            conn.commit()

    def save_session(self, session_id: str, user_name: str, dump: str, plan_dict: Dict[str, Any]):
        friction = plan_dict.get("friction_analysis", {})
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO sessions 
                (id, user_name, original_dump, perceived_mountain, core_blocker, total_steps, completed_steps, dopamine_earned)
                VALUES (?, ?, ?, ?, ?, ?, 0, 0)
            """, (
                session_id,
                user_name,
                dump,
                friction.get("perceived_mountain", ""),
                friction.get("core_blocker", ""),
                plan_dict.get("total_steps", 0)
            ))
            conn.commit()

    def record_step_completion(self, session_id: str, user_name: str, step_data: Dict[str, Any], dopamine_points: int):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO completed_tasks (session_id, step_id, title, domain, seconds_spent, dopamine_points)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                step_data.get("id", ""),
                step_data.get("title", ""),
                step_data.get("domain", ""),
                step_data.get("estimated_seconds", 120),
                dopamine_points
            ))
            cursor.execute("""
                UPDATE sessions 
                SET completed_steps = completed_steps + 1,
                    dopamine_earned = dopamine_earned + ?
                WHERE id = ?
            """, (dopamine_points, session_id))
            
            # Update user profile
            cursor.execute("""
                INSERT INTO user_profile (user_name, all_time_dopamine, total_conquered_tasks)
                VALUES (?, ?, 1)
                ON CONFLICT(user_name) DO UPDATE SET
                    all_time_dopamine = all_time_dopamine + ?,
                    total_conquered_tasks = total_conquered_tasks + 1
            """, (user_name, dopamine_points, dopamine_points))
            conn.commit()

    def get_user_stats(self, user_name: str = "Mayank") -> Dict[str, Any]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT all_time_dopamine, highest_streak, total_conquered_tasks FROM user_profile WHERE user_name = ?", (user_name,))
            row = cursor.fetchone()
            if row:
                return {
                    "user_name": user_name,
                    "all_time_dopamine": row[0],
                    "highest_streak": row[1],
                    "total_conquered_tasks": row[2]
                }
            return {
                "user_name": user_name,
                "all_time_dopamine": 0,
                "highest_streak": 0,
                "total_conquered_tasks": 0
            }
