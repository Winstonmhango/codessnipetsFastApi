# CodeSnippets API

A comprehensive FastAPI backend for the CodeSnippets blog and learning platform. This API provides endpoints for managing blog posts, categories, series, booklets, learning paths, and user authentication.

## Features

- **RESTful API**: Well-structured API endpoints following REST principles
- **Authentication**: JWT-based authentication with token refresh
- **User Management**: User registration, profile management, and role-based access control
- **Content Management**: CRUD operations for blog posts, categories, series, booklets, and learning paths
- **Database Integration**: PostgreSQL database with SQLAlchemy ORM
- **Migrations**: Database migrations using Alembic
- **Documentation**: Auto-generated API documentation with Swagger UI and ReDoc
- **Validation**: Request and response validation using Pydantic
- **CORS Support**: Cross-Origin Resource Sharing support for frontend integration

## Project Structure

```
fastapi-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── core/                   # Core modules
│   │   ├── __init__.py
│   │   ├── config.py           # Configuration settings
│   │   ├── security.py         # Authentication and security utilities
│   │   └── database.py         # Database connection and session management
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── post.py
│   │   ├── category.py
│   │   ├── series.py
│   │   ├── booklet.py
│   │   └── learning_path.py
│   ├── schemas/                # Pydantic schemas for request/response validation
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── post.py
│   │   ├── category.py
│   │   ├── series.py
│   │   ├── booklet.py
│   │   └── learning_path.py
│   ├── crud/                   # CRUD operations
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── user.py
│   │   ├── post.py
│   │   ├── category.py
│   │   ├── series.py
│   │   ├── booklet.py
│   │   └── learning_path.py
│   ├── api/                    # API endpoints
│   │   ├── __init__.py
│   │   ├── deps.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── api.py
│   │   │   ├── endpoints/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py
│   │   │   │   ├── users.py
│   │   │   │   ├── posts.py
│   │   │   │   ├── categories.py
│   │   │   │   ├── series.py
│   │   │   │   ├── booklets.py
│   │   │   │   └── learning_paths.py
│   ├── static/                 # Static files for documentation
│   │   └── index.html          # HTML documentation page
│   └── utils/                  # Utility functions
│       ├── __init__.py
│       └── init_db.py          # Database initialization script
├── alembic/                    # Database migrations
│   ├── versions/
│   ├── env.py
│   └── alembic.ini
├── docs/                       # Documentation
│   ├── README.md               # Documentation overview
│   └── API_DOCUMENTATION.md    # Comprehensive API documentation
├── tests/                      # Test directory
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_api/
│   │   ├── __init__.py
│   │   ├── test_auth.py
│   │   ├── test_users.py
│   │   └── ...
│   └── test_crud/
│       ├── __init__.py
│       ├── test_user.py
│       └── ...
├── .env                        # Environment variables
├── .gitignore
├── requirements.txt
├── run.py                      # Script to run the application
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/codesnippets-api.git
   cd codesnippets-api
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root and configure your environment variables:
   ```
   # Database settings
   DATABASE_URL=postgresql://postgres:postgres@localhost/codesnippets

   # Security settings
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30

   # Application settings
   PROJECT_NAME=CodeSnippets API
   API_V1_STR=/api/v1
   BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
   ```

5. Create the database:
   ```bash
   createdb codesnippets  # Using PostgreSQL command line tools
   ```

6. Run database migrations:
   ```bash
   alembic upgrade head
   ```

### Running the Application

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000.

API documentation will be available at:
- HTML Documentation: http://localhost:8000/
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Markdown Documentation: See the `docs/API_DOCUMENTATION.md` file

## API Endpoints

### Authentication

- `POST /api/v1/auth/login` - Login and get access token
- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/test-token` - Test access token

### Users

- `GET /api/v1/users/` - Get all users (admin only)
- `GET /api/v1/users/me` - Get current user
- `PUT /api/v1/users/me` - Update current user
- `GET /api/v1/users/{user_id}` - Get user by ID
- `PUT /api/v1/users/{user_id}` - Update user (admin only)

### Categories

- `GET /api/v1/categories/` - Get all categories with post count
- `POST /api/v1/categories/` - Create a new category (admin only)
- `GET /api/v1/categories/{slug}` - Get category by slug
- `PUT /api/v1/categories/{category_id}` - Update category (admin only)
- `DELETE /api/v1/categories/{category_id}` - Delete category (admin only)

### Posts

- `GET /api/v1/posts/` - Get all posts
- `POST /api/v1/posts/` - Create a new post
- `GET /api/v1/posts/{slug}` - Get post by slug
- `PUT /api/v1/posts/{post_id}` - Update post
- `DELETE /api/v1/posts/{post_id}` - Delete post
- `GET /api/v1/posts/category/{category_slug}` - Get posts by category
- `GET /api/v1/posts/author/{author_id}` - Get posts by author
- `GET /api/v1/posts/related/{slug}/{category_slug}` - Get related posts

### Series

- `GET /api/v1/series/` - Get all series
- `POST /api/v1/series/` - Create a new series (admin only)
- `GET /api/v1/series/{slug}` - Get series by slug with details
- `PUT /api/v1/series/{series_id}` - Update series (admin only)
- `DELETE /api/v1/series/{series_id}` - Delete series (admin only)
- `GET /api/v1/series/related/{series_id}` - Get related series
- `GET /api/v1/series/{series_id}/articles` - Get articles for a series
- `POST /api/v1/series/{series_id}/articles` - Create a new article for a series (admin only)
- `PUT /api/v1/series/articles/{article_id}` - Update a series article (admin only)
- `DELETE /api/v1/series/articles/{article_id}` - Delete a series article (admin only)

### Booklets

- `GET /api/v1/booklets/` - Get all booklets
- `POST /api/v1/booklets/` - Create a new booklet (admin only)
- `GET /api/v1/booklets/{slug}` - Get booklet by slug with details
- `PUT /api/v1/booklets/{booklet_id}` - Update booklet (admin only)
- `DELETE /api/v1/booklets/{booklet_id}` - Delete booklet (admin only)
- `GET /api/v1/booklets/{booklet_id}/chapters` - Get chapters for a booklet
- `POST /api/v1/booklets/{booklet_id}/chapters` - Create a new chapter for a booklet (admin only)
- `PUT /api/v1/booklets/chapters/{chapter_id}` - Update a booklet chapter (admin only)
- `DELETE /api/v1/booklets/chapters/{chapter_id}` - Delete a booklet chapter (admin only)
- `GET /api/v1/booklets/{booklet_id}/updates` - Get updates for a booklet
- `POST /api/v1/booklets/{booklet_id}/updates` - Create a new update for a booklet (admin only)
- `PUT /api/v1/booklets/updates/{update_id}` - Update a booklet update (admin only)
- `DELETE /api/v1/booklets/updates/{update_id}` - Delete a booklet update (admin only)

### Learning Paths

- `GET /api/v1/learning-paths/` - Get all learning paths
- `POST /api/v1/learning-paths/` - Create a new learning path (admin only)
- `GET /api/v1/learning-paths/featured` - Get featured learning paths
- `GET /api/v1/learning-paths/tag/{tag}` - Get learning paths by tag
- `GET /api/v1/learning-paths/{slug}` - Get learning path by slug with details
- `PUT /api/v1/learning-paths/{learning_path_id}` - Update learning path (admin only)
- `DELETE /api/v1/learning-paths/{learning_path_id}` - Delete learning path (admin only)
- `GET /api/v1/learning-paths/related/{learning_path_id}` - Get related learning paths
- `POST /api/v1/learning-paths/{learning_path_id}/modules` - Create a new module for a learning path (admin only)
- `PUT /api/v1/learning-paths/modules/{module_id}` - Update a module (admin only)
- `DELETE /api/v1/learning-paths/modules/{module_id}` - Delete a module (admin only)
- `POST /api/v1/learning-paths/modules/{module_id}/items` - Create a new content item for a module (admin only)
- `PUT /api/v1/learning-paths/items/{item_id}` - Update a content item (admin only)
- `DELETE /api/v1/learning-paths/items/{item_id}` - Delete a content item (admin only)
- `POST /api/v1/learning-paths/{learning_path_id}/resources` - Create a new resource for a learning path (admin only)
- `PUT /api/v1/learning-paths/resources/{resource_id}` - Update a resource (admin only)
- `DELETE /api/v1/learning-paths/resources/{resource_id}` - Delete a resource (admin only)

## Testing

Run tests using pytest:

```bash
pytest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
