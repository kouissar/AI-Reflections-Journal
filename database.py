import sqlite3
import os
import logging
import streamlit as st
import pandas as pd
from textblob import TextBlob
from datetime import datetime
import json

# Set up logging
logger = logging.getLogger(__name__)

class ReflectionDB:
    def __init__(self):
        try:
            self.db_path = os.path.join(os.getcwd(), 'reflections.db')
            logger.info(f"Connecting to database at: {self.db_path}")
            
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            logger.info("Database connection established")
            self.create_tables()
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            st.error(f"Database initialization error: {str(e)}")
    
    def create_tables(self):
        try:
            logger.info("Creating tables if they don't exist...")
            cursor = self.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    content TEXT NOT NULL,
                    mood INTEGER NOT NULL,
                    mood_factors TEXT,
                    sentiment REAL,
                    entry_type TEXT NOT NULL,
                    ai_insight TEXT,
                    weather_data TEXT
                )
            ''')
            self.conn.commit()
            logger.info("Tables created successfully")
        except Exception as e:
            logger.error(f"Error creating tables: {str(e)}")
            st.error(f"Error creating tables: {str(e)}")

    def update_entry(self, entry_id, content, mood, mood_factors, ai_insight=None):
        try:
            sentiment = TextBlob(content).sentiment.polarity
            cursor = self.conn.cursor()
            
            cursor.execute('''
                UPDATE entries 
                SET content = ?, mood = ?, mood_factors = ?, sentiment = ?, ai_insight = ?
                WHERE id = ?
            ''', (content, mood, mood_factors, sentiment, ai_insight, entry_id))
            self.conn.commit()
            logger.info(f"Entry {entry_id} updated successfully")
            return True
        except Exception as e:
            logger.error(f"Error updating entry: {str(e)}")
            st.error(f"Error updating entry: {str(e)}")
            return False

    def delete_entry(self, entry_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM entries WHERE id = ?', (entry_id,))
            self.conn.commit()
            logger.info(f"Entry {entry_id} deleted successfully")
            return True
        except Exception as e:
            logger.error(f"Error deleting entry: {str(e)}")
            st.error(f"Error deleting entry: {str(e)}")
            return False
    
    def add_entry(self, content, mood, mood_factors, ai_insight=None, weather_data=None, entry_type="text"):
        try:
            sentiment = TextBlob(content).sentiment.polarity
            cursor = self.conn.cursor()
            
            cursor.execute('''
                INSERT INTO entries (
                    date, content, mood, mood_factors, 
                    sentiment, entry_type, ai_insight, weather_data
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(), content, mood, mood_factors,
                sentiment, entry_type, ai_insight, 
                json.dumps(weather_data) if weather_data else None
            ))
            self.conn.commit()
            
            cursor.execute('SELECT COUNT(*) FROM entries')
            count = cursor.fetchone()[0]
            logger.info(f"Total entries after insert: {count}")
            
            return True
        except Exception as e:
            logger.error(f"Error adding entry: {str(e)}")
            st.error(f"Error saving entry: {str(e)}")
            return False
    
    def get_entries(self, limit=10):
        try:
            query = 'SELECT * FROM entries ORDER BY date DESC LIMIT ?'
            logger.info(f"Fetching entries with query: {query}, limit: {limit}")
            
            df = pd.read_sql_query(query, self.conn, params=(limit,))
            logger.info(f"Retrieved {len(df)} entries")
            return df
        except Exception as e:
            logger.error(f"Error getting entries: {str(e)}")
            st.error(f"Error retrieving entries: {str(e)}")
            return pd.DataFrame() 