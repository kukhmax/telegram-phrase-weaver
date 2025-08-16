#!/usr/bin/env python3
"""
Simple script to create database tables without alembic
"""

import asyncio
import os
from sqlalchemy import create_engine, text

def create_tables():
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("DATABASE_URL not found")
        return
    
    # Convert asyncpg to psycopg2 if needed
    if "postgresql+asyncpg://" in database_url:
        database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
    
    print(f"Connecting to: {database_url[:50]}...")
    
    # Create engine
    engine = create_engine(database_url)
    
    # SQL to create tables
    sql_commands = [
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            telegram_id INTEGER UNIQUE,
            username VARCHAR,
            first_name VARCHAR,
            last_name VARCHAR,
            language_code VARCHAR DEFAULT 'en',
            is_premium BOOLEAN DEFAULT FALSE,
            is_bot BOOLEAN DEFAULT FALSE,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            settings JSON DEFAULT '{}'
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS decks (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            name VARCHAR,
            description VARCHAR,
            lang_from VARCHAR,
            lang_to VARCHAR,
            cards_count INTEGER DEFAULT 0,
            due_count INTEGER DEFAULT 0
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS cards (
            id SERIAL PRIMARY KEY,
            deck_id INTEGER REFERENCES decks(id),
            phrase VARCHAR,
            translation VARCHAR,
            keyword VARCHAR,
            audio_path VARCHAR,
            image_path VARCHAR,
            examples JSON,
            due_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            interval FLOAT DEFAULT 1.0,
            ease_factor FLOAT DEFAULT 2.5
        );
        """
    ]
    
    try:
        with engine.connect() as conn:
            for sql in sql_commands:
                print(f"Executing: {sql[:50]}...")
                conn.execute(text(sql))
                conn.commit()
        print("Tables created successfully!")
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    create_tables()