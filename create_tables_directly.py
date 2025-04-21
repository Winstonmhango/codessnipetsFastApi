import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath("."))

try:
    # Import the database connection
    from sqlalchemy import create_engine, text
    import os

    # Get database URL from environment
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print('ERROR: DATABASE_URL environment variable not set')
        sys.exit(1)

    # Create engine
    engine = create_engine(db_url)

    # Create tables directly with SQL
    with engine.connect() as conn:
        # Create User table if it doesn't exist
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS users (
            id VARCHAR PRIMARY KEY,
            email VARCHAR UNIQUE NOT NULL,
            username VARCHAR UNIQUE NOT NULL,
            first_name VARCHAR,
            last_name VARCHAR,
            hashed_password VARCHAR NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            is_superuser BOOLEAN DEFAULT FALSE,
            total_points INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            experience INTEGER DEFAULT 0,
            streak INTEGER DEFAULT 0,
            longest_streak INTEGER DEFAULT 0,
            preferences JSONB,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE
        )
        """))
        
        # Create other tables as needed
        # ...
        
        # Create marketing tables
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS newsletter_subscriptions (
            id VARCHAR PRIMARY KEY,
            email VARCHAR UNIQUE NOT NULL,
            name VARCHAR,
            is_active BOOLEAN DEFAULT TRUE,
            subscribed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            unsubscribed_at TIMESTAMP WITH TIME ZONE,
            source VARCHAR,
            synced_to_kit BOOLEAN DEFAULT FALSE,
            kit_sync_at TIMESTAMP WITH TIME ZONE,
            subscription_metadata JSONB,
            user_id VARCHAR REFERENCES users(id)
        )
        """))
        
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS marketing_banners (
            id VARCHAR PRIMARY KEY,
            title VARCHAR NOT NULL,
            content TEXT NOT NULL,
            cta_text VARCHAR,
            cta_link VARCHAR,
            banner_type VARCHAR DEFAULT 'banner',
            position VARCHAR DEFAULT 'top',
            background_color VARCHAR DEFAULT '#f8f9fa',
            text_color VARCHAR DEFAULT '#212529',
            is_active BOOLEAN DEFAULT TRUE,
            start_date TIMESTAMP WITH TIME ZONE,
            end_date TIMESTAMP WITH TIME ZONE,
            show_to_logged_in BOOLEAN DEFAULT TRUE,
            show_to_anonymous BOOLEAN DEFAULT TRUE,
            show_once_per_session BOOLEAN DEFAULT FALSE,
            show_on_pages JSONB,
            priority INTEGER DEFAULT 0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE,
            created_by VARCHAR REFERENCES users(id),
            impressions INTEGER DEFAULT 0,
            clicks INTEGER DEFAULT 0,
            dismissals INTEGER DEFAULT 0,
            conversions INTEGER DEFAULT 0
        )
        """))
        
        # Create prelaunch tables
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS course_prelaunch_campaigns (
            id VARCHAR PRIMARY KEY,
            title VARCHAR NOT NULL,
            slug VARCHAR UNIQUE NOT NULL,
            description TEXT,
            start_date TIMESTAMP WITH TIME ZONE,
            end_date TIMESTAMP WITH TIME ZONE,
            is_active BOOLEAN DEFAULT TRUE,
            lead_magnet_title VARCHAR,
            lead_magnet_description TEXT,
            lead_magnet_file_url VARCHAR,
            header_image_url VARCHAR,
            content TEXT,
            cta_text VARCHAR,
            cta_url VARCHAR,
            early_bird_price INTEGER,
            regular_price INTEGER,
            max_enrollments INTEGER,
            view_count INTEGER DEFAULT 0,
            signup_count INTEGER DEFAULT 0,
            conversion_rate INTEGER DEFAULT 0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE,
            created_by VARCHAR REFERENCES users(id)
        )
        """))
        
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS prelaunch_subscribers (
            id VARCHAR PRIMARY KEY,
            email VARCHAR NOT NULL,
            name VARCHAR,
            campaign_id VARCHAR REFERENCES course_prelaunch_campaigns(id) NOT NULL,
            subscribed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            is_active BOOLEAN DEFAULT TRUE,
            unsubscribed_at TIMESTAMP WITH TIME ZONE,
            lead_magnet_sent BOOLEAN DEFAULT FALSE,
            lead_magnet_sent_at TIMESTAMP WITH TIME ZONE,
            user_id VARCHAR REFERENCES users(id),
            source VARCHAR,
            ip_address VARCHAR,
            user_agent VARCHAR,
            referrer VARCHAR,
            custom_fields JSONB
        )
        """))
        
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS prelaunch_email_sequences (
            id VARCHAR PRIMARY KEY,
            campaign_id VARCHAR REFERENCES course_prelaunch_campaigns(id) NOT NULL,
            title VARCHAR NOT NULL,
            description TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE
        )
        """))
        
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS prelaunch_emails (
            id VARCHAR PRIMARY KEY,
            sequence_id VARCHAR REFERENCES prelaunch_email_sequences(id) NOT NULL,
            subject VARCHAR NOT NULL,
            body TEXT NOT NULL,
            delay_days INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE,
            sent_count INTEGER DEFAULT 0,
            open_count INTEGER DEFAULT 0,
            click_count INTEGER DEFAULT 0
        )
        """))
        
        # Create association tables
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS prelaunch_course_association (
            prelaunch_id VARCHAR REFERENCES course_prelaunch_campaigns(id),
            course_id VARCHAR,
            PRIMARY KEY (prelaunch_id, course_id)
        )
        """))
        
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS prelaunch_booklet_association (
            prelaunch_id VARCHAR REFERENCES course_prelaunch_campaigns(id),
            booklet_id VARCHAR,
            PRIMARY KEY (prelaunch_id, booklet_id)
        )
        """))
        
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS prelaunch_series_association (
            prelaunch_id VARCHAR REFERENCES course_prelaunch_campaigns(id),
            series_id VARCHAR,
            PRIMARY KEY (prelaunch_id, series_id)
        )
        """))
        
        print("Tables created successfully!")
    
except Exception as e:
    print(f"Error creating tables: {e}")
    import traceback
    traceback.print_exc()
