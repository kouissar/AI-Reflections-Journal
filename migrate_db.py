import sqlite3
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_database():
    try:
        # Connect to the database
        db_path = os.path.join(os.getcwd(), 'reflections.db')
        logger.info(f"Connecting to database at: {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if column exists
        cursor.execute("PRAGMA table_info(entries)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'ai_insight' not in columns:
            logger.info("Adding ai_insight column to entries table...")
            
            # Add the new column
            cursor.execute('''
                ALTER TABLE entries
                ADD COLUMN ai_insight TEXT
            ''')
            
        if 'weather_data' not in columns:
            logger.info("Adding weather_data column to entries table...")
            cursor.execute('ALTER TABLE entries ADD COLUMN weather_data TEXT')
            
        conn.commit()
        logger.info("Database migration completed successfully")
        
        conn.close()
        
    except Exception as e:
        logger.error(f"Error during database migration: {str(e)}")
        raise e

if __name__ == "__main__":
    try:
        migrate_database()
        print("Migration completed successfully!")
    except Exception as e:
        print(f"Migration failed: {str(e)}") 