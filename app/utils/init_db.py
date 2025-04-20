import logging
import uuid
from sqlalchemy.orm import Session

from app import crud, schemas
from app.core.config import settings
from app.core.security import get_password_hash
from app.models import User, Category, Author

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db(db: Session) -> None:
    """
    Initialize the database with sample data
    """
    # Create superuser if it doesn't exist
    user = crud.user.get_by_email(db, email="admin@example.com")
    if not user:
        user_in = schemas.UserCreate(
            email="admin@example.com",
            username="admin",
            password="admin",
            first_name="Admin",
            last_name="User",
            is_superuser=True,
        )
        user = crud.user.create(db, obj_in=user_in)
        logger.info("Superuser created")
    else:
        logger.info("Superuser already exists")

    # Create categories if they don't exist
    categories = [
        {"name": "Technology", "slug": "technology", "description": "Latest trends and innovations in software development, AI, and digital transformation."},
        {"name": "Design", "slug": "design", "description": "Insights on UX/UI design, accessibility, and creating beautiful digital experiences."},
        {"name": "Business", "slug": "business", "description": "Strategies for growth, entrepreneurship, and building sustainable companies."},
        {"name": "Marketing", "slug": "marketing", "description": "Effective approaches to digital marketing, content strategy, and customer acquisition."},
    ]
    
    for category_data in categories:
        category = crud.category.get_by_slug(db, slug=category_data["slug"])
        if not category:
            category_in = schemas.CategoryCreate(**category_data)
            crud.category.create(db, obj_in=category_in)
            logger.info(f"Category '{category_data['name']}' created")
        else:
            logger.info(f"Category '{category_data['name']}' already exists")

    # Create authors if they don't exist
    authors = [
        {
            "name": "Sarah Johnson",
            "avatar": "/avatars/sarah-johnson.jpg",
            "bio": "Senior JavaScript Developer with 8+ years of experience. Passionate about teaching and sharing knowledge.",
            "twitter": "sarahjohnson",
            "github": "sarahjohnson",
            "linkedin": "sarahjohnson",
        },
        {
            "name": "Michael Chen",
            "avatar": "/avatars/michael-chen.jpg",
            "bio": "Full Stack Developer and open source contributor. Loves building tools that make developers' lives easier.",
            "twitter": "michaelchen",
            "github": "michaelchen",
            "linkedin": "michaelchen",
        },
    ]
    
    for author_data in authors:
        # Check if author exists by name (simplified approach)
        author = db.query(Author).filter(Author.name == author_data["name"]).first()
        if not author:
            author_in = schemas.AuthorCreate(**author_data)
            crud.author.create(db, obj_in=author_in)
            logger.info(f"Author '{author_data['name']}' created")
        else:
            logger.info(f"Author '{author_data['name']}' already exists")

    logger.info("Database initialization completed")


if __name__ == "__main__":
    from app.core.database import SessionLocal
    
    db = SessionLocal()
    init_db(db)
    db.close()
