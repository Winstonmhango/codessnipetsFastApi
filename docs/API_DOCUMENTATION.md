# CodeSnippets API Documentation

This document provides comprehensive documentation for the CodeSnippets API, which serves as the backend for the CodeSnippets Next.js frontend application.

## Table of Contents

- [Overview](#overview)
- [Getting Started](#getting-started)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Running the API](#running-the-api)
- [Authentication](#authentication)
  - [Register](#register)
  - [Login](#login)
  - [Using Authentication Tokens](#using-authentication-tokens)
- [API Endpoints](#api-endpoints)
  - [Users](#users)
  - [Categories](#categories)
  - [Posts](#posts)
  - [Series](#series)
  - [Booklets](#booklets)
  - [Learning Paths](#learning-paths)
- [Data Models](#data-models)
- [Error Handling](#error-handling)
- [Integration with Next.js Frontend](#integration-with-nextjs-frontend)
- [Development and Testing](#development-and-testing)

## Overview

The CodeSnippets API is built with FastAPI, providing a robust, high-performance backend for the CodeSnippets platform. It follows RESTful principles and uses JWT for authentication. The API provides endpoints for managing users, blog posts, categories, series, booklets, and learning paths.

Key features:
- RESTful API design
- JWT-based authentication
- SQLAlchemy ORM for database interactions
- Pydantic schemas for request/response validation
- Comprehensive CRUD operations for all resources
- Modular architecture for scalability

## Getting Started

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

### Configuration

1. Create a `.env` file in the project root with the following variables:
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

2. Create the database:
   ```bash
   createdb codesnippets  # Using PostgreSQL command line tools
   ```

3. Run database migrations:
   ```bash
   alembic upgrade head
   ```

### Running the API

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000.

API documentation will be available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. To access protected endpoints, you need to include the JWT token in the Authorization header of your requests.

### Register

To register a new user:

```
POST /api/v1/auth/register
```

Request body:
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "password",
  "first_name": "First",
  "last_name": "Last"
}
```

Response:
```json
{
  "id": "user_id",
  "email": "user@example.com",
  "username": "username",
  "first_name": "First",
  "last_name": "Last",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2023-01-01T00:00:00"
}
```

### Login

To login and get an access token:

```
POST /api/v1/auth/login
```

Request body (form data):
```
username: user@example.com
password: password
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Using Authentication Tokens

Include the token in the Authorization header of your requests:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Example with fetch in JavaScript:
```javascript
const response = await fetch('http://localhost:8000/api/v1/users/me', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const data = await response.json();
```

## API Endpoints

### Users

#### Get Current User

```
GET /api/v1/users/me
```

Response:
```json
{
  "id": "user_id",
  "email": "user@example.com",
  "username": "username",
  "first_name": "First",
  "last_name": "Last",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2023-01-01T00:00:00"
}
```

#### Update Current User

```
PUT /api/v1/users/me
```

Request body:
```json
{
  "first_name": "Updated",
  "last_name": "Name",
  "email": "updated@example.com",
  "password": "new_password"
}
```

Response: Updated user object

#### Get All Users (Admin Only)

```
GET /api/v1/users/
```

Response: Array of user objects

#### Get User by ID (Admin or Self)

```
GET /api/v1/users/{user_id}
```

Response: User object

#### Update User (Admin Only)

```
PUT /api/v1/users/{user_id}
```

Request body: User update object
Response: Updated user object

### Categories

#### Get All Categories

```
GET /api/v1/categories/
```

Response:
```json
[
  {
    "id": "category_id",
    "name": "Technology",
    "slug": "technology",
    "description": "Technology articles",
    "post_count": 10
  },
  ...
]
```

#### Create Category (Admin Only)

```
POST /api/v1/categories/
```

Request body:
```json
{
  "name": "New Category",
  "slug": "new-category",
  "description": "Description of the new category"
}
```

Response: Created category object

#### Get Category by Slug

```
GET /api/v1/categories/{slug}
```

Response: Category object

#### Update Category (Admin Only)

```
PUT /api/v1/categories/{category_id}
```

Request body: Category update object
Response: Updated category object

#### Delete Category (Admin Only)

```
DELETE /api/v1/categories/{category_id}
```

Response: Deleted category object

### Posts

#### Get All Posts

```
GET /api/v1/posts/
```

Response: Array of post objects

#### Create Post

```
POST /api/v1/posts/
```

Request body:
```json
{
  "title": "New Post",
  "slug": "new-post",
  "excerpt": "Short excerpt",
  "content": "Full content",
  "cover_image": "/images/cover.jpg",
  "category": "category_id",
  "reading_time": 5,
  "introduction": "Introduction text",
  "summary": ["Summary point 1", "Summary point 2"],
  "table_of_contents": [
    {
      "id": "section-1",
      "title": "Section 1",
      "level": 1
    }
  ],
  "sections": [
    {
      "id": "section-1",
      "title": "Section 1",
      "level": 1,
      "content": "Section content"
    }
  ],
  "blocks": [
    {
      "id": "block-1",
      "type": "paragraph",
      "content": "Block content"
    }
  ]
}
```

Response: Created post object

#### Get Post by Slug

```
GET /api/v1/posts/{slug}
```

Response: Post object

#### Update Post

```
PUT /api/v1/posts/{post_id}
```

Request body: Post update object
Response: Updated post object

#### Delete Post

```
DELETE /api/v1/posts/{post_id}
```

Response: Deleted post object

#### Get Posts by Category

```
GET /api/v1/posts/category/{category_slug}
```

Response: Array of post objects

#### Get Posts by Author

```
GET /api/v1/posts/author/{author_id}
```

Response: Array of post objects

#### Get Related Posts

```
GET /api/v1/posts/related/{slug}/{category_slug}
```

Response: Array of related post objects

### Series

#### Get All Series

```
GET /api/v1/series/
```

Response: Array of series objects

#### Create Series (Admin Only)

```
POST /api/v1/series/
```

Request body:
```json
{
  "title": "New Series",
  "slug": "new-series",
  "description": "Series description",
  "long_description": "Longer description",
  "cover_image": "/images/series-cover.jpg",
  "author_id": "author_id",
  "level": "Intermediate",
  "estimated_time": "5-7 hours",
  "tags": ["javascript", "typescript"],
  "learning_outcomes": ["Outcome 1", "Outcome 2"],
  "prerequisites": ["Prerequisite 1", "Prerequisite 2"]
}
```

Response: Created series object

#### Get Series by Slug

```
GET /api/v1/series/{slug}
```

Response: Series object with author and articles

#### Update Series (Admin Only)

```
PUT /api/v1/series/{series_id}
```

Request body: Series update object
Response: Updated series object

#### Delete Series (Admin Only)

```
DELETE /api/v1/series/{series_id}
```

Response: Deleted series object

#### Get Related Series

```
GET /api/v1/series/related/{series_id}
```

Response: Array of related series objects

#### Get Series Articles

```
GET /api/v1/series/{series_id}/articles
```

Response: Array of series article objects

#### Create Series Article (Admin Only)

```
POST /api/v1/series/{series_id}/articles
```

Request body:
```json
{
  "title": "New Article",
  "slug": "new-article",
  "reading_time": 15,
  "is_completed": false,
  "is_premium": false,
  "is_unlocked": true,
  "is_new": true,
  "series_id": "series_id"
}
```

Response: Created series article object

### Booklets

#### Get All Booklets

```
GET /api/v1/booklets/
```

Response: Array of booklet objects

#### Create Booklet (Admin Only)

```
POST /api/v1/booklets/
```

Request body:
```json
{
  "title": "New Booklet",
  "slug": "new-booklet",
  "description": "Booklet description",
  "long_description": "Longer description",
  "cover_image": "/images/booklet-cover.jpg",
  "author_id": "author_id",
  "status": "In Progress",
  "estimated_time": "8-10 hours",
  "last_updated": "January 1, 2023",
  "tags": ["react", "nextjs"],
  "learning_outcomes": ["Outcome 1", "Outcome 2"],
  "prerequisites": ["Prerequisite 1", "Prerequisite 2"]
}
```

Response: Created booklet object

#### Get Booklet by Slug

```
GET /api/v1/booklets/{slug}
```

Response: Booklet object with author, chapters, and updates

#### Update Booklet (Admin Only)

```
PUT /api/v1/booklets/{booklet_id}
```

Request body: Booklet update object
Response: Updated booklet object

#### Delete Booklet (Admin Only)

```
DELETE /api/v1/booklets/{booklet_id}
```

Response: Deleted booklet object

#### Get Booklet Chapters

```
GET /api/v1/booklets/{booklet_id}/chapters
```

Response: Array of booklet chapter objects

#### Create Booklet Chapter (Admin Only)

```
POST /api/v1/booklets/{booklet_id}/chapters
```

Request body:
```json
{
  "title": "New Chapter",
  "slug": "new-chapter",
  "reading_time": 20,
  "is_published": true,
  "publish_date": "January 15, 2023",
  "is_completed": false,
  "is_premium": false,
  "is_unlocked": true,
  "is_new": true,
  "booklet_id": "booklet_id"
}
```

Response: Created booklet chapter object

#### Get Booklet Updates

```
GET /api/v1/booklets/{booklet_id}/updates
```

Response: Array of booklet update objects

#### Create Booklet Update (Admin Only)

```
POST /api/v1/booklets/{booklet_id}/updates
```

Request body:
```json
{
  "title": "New Update",
  "date": "January 20, 2023",
  "description": "Update description",
  "chapter_link": "/booklets/slug/chapters/chapter-slug",
  "booklet_id": "booklet_id"
}
```

Response: Created booklet update object

### Learning Paths

#### Get All Learning Paths

```
GET /api/v1/learning-paths/
```

Response: Array of learning path objects

#### Create Learning Path (Admin Only)

```
POST /api/v1/learning-paths/
```

Request body:
```json
{
  "title": "New Learning Path",
  "slug": "new-learning-path",
  "description": "Learning path description",
  "long_description": "Longer description",
  "cover_image": "/images/path-cover.jpg",
  "author": "Author Name",
  "level": "Beginner",
  "duration": "8 weeks",
  "tags": ["javascript", "react", "frontend"],
  "article_count": 12,
  "quiz_count": 6,
  "learning_outcomes": ["Outcome 1", "Outcome 2"],
  "prerequisites": ["Prerequisite 1", "Prerequisite 2"]
}
```

Response: Created learning path object

#### Get Featured Learning Paths

```
GET /api/v1/learning-paths/featured
```

Response: Array of featured learning path objects

#### Get Learning Paths by Tag

```
GET /api/v1/learning-paths/tag/{tag}
```

Response: Array of learning path objects with the specified tag

#### Get Learning Path by Slug

```
GET /api/v1/learning-paths/{slug}
```

Response: Learning path object with modules and resources

#### Update Learning Path (Admin Only)

```
PUT /api/v1/learning-paths/{learning_path_id}
```

Request body: Learning path update object
Response: Updated learning path object

#### Delete Learning Path (Admin Only)

```
DELETE /api/v1/learning-paths/{learning_path_id}
```

Response: Deleted learning path object

#### Get Related Learning Paths

```
GET /api/v1/learning-paths/related/{learning_path_id}
```

Response: Array of related learning path objects

#### Create Learning Path Module (Admin Only)

```
POST /api/v1/learning-paths/{learning_path_id}/modules
```

Request body:
```json
{
  "title": "New Module",
  "description": "Module description",
  "estimated_time": "2 weeks",
  "is_completed": false,
  "is_premium": false,
  "is_unlocked": true,
  "start_url": "/blog/module-start",
  "learning_path_id": "learning_path_id"
}
```

Response: Created learning path module object

## Data Models

### User

```json
{
  "id": "string",
  "email": "string",
  "username": "string",
  "first_name": "string",
  "last_name": "string",
  "is_active": true,
  "is_superuser": false,
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Category

```json
{
  "id": "string",
  "name": "string",
  "slug": "string",
  "description": "string",
  "post_count": 0
}
```

### Post

```json
{
  "id": "string",
  "title": "string",
  "slug": "string",
  "excerpt": "string",
  "content": "string",
  "cover_image": "string",
  "date": "datetime",
  "author": "string",
  "category": "string",
  "reading_time": 0,
  "introduction": "string",
  "summary": ["string"],
  "table_of_contents": [
    {
      "id": "string",
      "title": "string",
      "level": 0
    }
  ],
  "sections": [
    {
      "id": "string",
      "title": "string",
      "level": 0,
      "content": "string",
      "subsections": []
    }
  ],
  "blocks": [
    {
      "id": "string",
      "type": "string",
      "content": "string",
      "data": {}
    }
  ],
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Author

```json
{
  "id": "string",
  "name": "string",
  "avatar": "string",
  "bio": "string",
  "twitter": "string",
  "github": "string",
  "linkedin": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Series

```json
{
  "id": "string",
  "title": "string",
  "slug": "string",
  "description": "string",
  "long_description": "string",
  "cover_image": "string",
  "author_id": "string",
  "level": "string",
  "estimated_time": "string",
  "tags": ["string"],
  "learning_outcomes": ["string"],
  "prerequisites": ["string"],
  "created_at": "datetime",
  "updated_at": "datetime",
  "author": {
    // Author object
  },
  "articles": [
    // SeriesArticle objects
  ]
}
```

### SeriesArticle

```json
{
  "id": "string",
  "title": "string",
  "slug": "string",
  "reading_time": 0,
  "is_completed": false,
  "is_premium": false,
  "is_unlocked": false,
  "is_new": false,
  "series_id": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Booklet

```json
{
  "id": "string",
  "title": "string",
  "slug": "string",
  "description": "string",
  "long_description": "string",
  "cover_image": "string",
  "author_id": "string",
  "status": "string",
  "estimated_time": "string",
  "last_updated": "string",
  "tags": ["string"],
  "learning_outcomes": ["string"],
  "prerequisites": ["string"],
  "created_at": "datetime",
  "updated_at": "datetime",
  "author": {
    // Author object
  },
  "chapters": [
    // BookletChapter objects
  ],
  "updates": [
    // BookletUpdate objects
  ]
}
```

### BookletChapter

```json
{
  "id": "string",
  "title": "string",
  "slug": "string",
  "reading_time": 0,
  "is_published": false,
  "publish_date": "string",
  "is_completed": false,
  "is_premium": false,
  "is_unlocked": false,
  "is_new": false,
  "booklet_id": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### BookletUpdate

```json
{
  "id": "string",
  "title": "string",
  "date": "string",
  "description": "string",
  "chapter_link": "string",
  "booklet_id": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### LearningPath

```json
{
  "id": "string",
  "title": "string",
  "slug": "string",
  "description": "string",
  "long_description": "string",
  "cover_image": "string",
  "author": "string",
  "level": "string",
  "duration": "string",
  "tags": ["string"],
  "article_count": 0,
  "quiz_count": 0,
  "learning_outcomes": ["string"],
  "prerequisites": ["string"],
  "created_at": "datetime",
  "updated_at": "datetime",
  "modules": [
    // LearningPathModule objects with content_items
  ],
  "resources": [
    // LearningPathResource objects
  ]
}
```

### LearningPathModule

```json
{
  "id": "string",
  "title": "string",
  "description": "string",
  "estimated_time": "string",
  "is_completed": false,
  "is_premium": false,
  "is_unlocked": false,
  "start_url": "string",
  "learning_path_id": "string",
  "created_at": "datetime",
  "updated_at": "datetime",
  "content_items": [
    // LearningPathContentItem objects
  ]
}
```

### LearningPathContentItem

```json
{
  "id": "string",
  "title": "string",
  "type": "string", // "article", "series", or "booklet"
  "is_completed": false,
  "module_id": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### LearningPathResource

```json
{
  "id": "string",
  "title": "string",
  "description": "string",
  "type": "string", // "documentation", "github", "video", "article", or "other"
  "url": "string",
  "learning_path_id": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

## Error Handling

The API returns appropriate HTTP status codes and error messages for different error scenarios:

- `400 Bad Request`: Invalid input data
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server-side error

Error response format:
```json
{
  "detail": "Error message"
}
```

For validation errors:
```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "Error message",
      "type": "error_type"
    }
  ]
}
```

## Integration with Next.js Frontend

### Setting Up API Client

Create an API client in your Next.js project to interact with the FastAPI backend:

```typescript
// lib/api-client.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export async function fetchAPI(endpoint: string, options: RequestInit = {}) {
  const token = localStorage.getItem('token');
  
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'An error occurred');
  }
  
  return response.json();
}

// Authentication
export async function login(email: string, password: string) {
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);
  
  const response = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData,
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Login failed');
  }
  
  const data = await response.json();
  localStorage.setItem('token', data.access_token);
  return data;
}

export async function register(userData: any) {
  return fetchAPI('/auth/register', {
    method: 'POST',
    body: JSON.stringify(userData),
  });
}

export async function getCurrentUser() {
  return fetchAPI('/users/me');
}

// Posts
export async function getPosts() {
  return fetchAPI('/posts');
}

export async function getPostBySlug(slug: string) {
  return fetchAPI(`/posts/${slug}`);
}

// Categories
export async function getCategories() {
  return fetchAPI('/categories');
}

export async function getCategoryBySlug(slug: string) {
  return fetchAPI(`/categories/${slug}`);
}

// Series
export async function getSeries() {
  return fetchAPI('/series');
}

export async function getSeriesBySlug(slug: string) {
  return fetchAPI(`/series/${slug}`);
}

// Booklets
export async function getBooklets() {
  return fetchAPI('/booklets');
}

export async function getBookletBySlug(slug: string) {
  return fetchAPI(`/booklets/${slug}`);
}

// Learning Paths
export async function getLearningPaths() {
  return fetchAPI('/learning-paths');
}

export async function getLearningPathBySlug(slug: string) {
  return fetchAPI(`/learning-paths/${slug}`);
}
```

### Using the API Client in Components

Example of using the API client in a Next.js component:

```tsx
// components/posts/post-list.tsx
'use client';

import { useEffect, useState } from 'react';
import { getPosts } from '@/lib/api-client';
import { BlogCard } from '@/components/blog-card';

export function PostList() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadPosts() {
      try {
        const data = await getPosts();
        setPosts(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    loadPosts();
  }, []);

  if (loading) return <div>Loading posts...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
      {posts.map((post) => (
        <BlogCard key={post.id} post={post} />
      ))}
    </div>
  );
}
```

### Authentication in Next.js

Example of a login form component:

```tsx
// components/auth/login-form.tsx
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { login } from '@/lib/api-client';

export function LoginForm() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await login(formData.email, formData.password);
      router.push('/dashboard');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {error && <div className="text-red-500 mb-4">{error}</div>}
      <div className="mb-4">
        <label htmlFor="email">Email</label>
        <input
          type="email"
          id="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          required
        />
      </div>
      <div className="mb-4">
        <label htmlFor="password">Password</label>
        <input
          type="password"
          id="password"
          name="password"
          value={formData.password}
          onChange={handleChange}
          required
        />
      </div>
      <button type="submit" disabled={loading}>
        {loading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
}
```

## Development and Testing

### Running Tests

Run tests using pytest:

```bash
pytest
```

### Database Migrations

Create a new migration:

```bash
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:

```bash
alembic upgrade head
```

### Initializing Sample Data

Initialize the database with sample data:

```bash
python -m app.utils.init_db
```

### Environment Variables

For development, you can use the `.env` file. For production, set environment variables according to your deployment platform.

## Conclusion

This documentation provides a comprehensive guide to the CodeSnippets API. For more detailed information, refer to the API documentation at `/docs` or `/redoc` endpoints when the API is running.

For any issues or questions, please open an issue on the GitHub repository or contact the development team.
