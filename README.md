# Social Media Service API
API for social media platform.

API allow users to create profiles, follow other users, create and retrieve posts, messages and events, manage likes and comments, and perform basic social media actions.

## Technologies
- Django Rest Framework
- Celery + Redis for scheduled post creation
- Postgres
- Docker

## Docker installation:

1. **Clone the repository:**

   ```sh
   git clone https://github.com/nicksetrakov/py-social-media
   cd py-social-media
   ```
   
2. Create an `.env` file in the root of the project directory. You can use the `.env.sample` file as a template:

   ```sh
   cp .env.example .env
   ```

3. Create app images and start it (you can comment containers such as telegram bot in docker-compose.yml if you don't need it):
   ```sh
   docker-compose build
   docker-compose up
   ```

## Getting access🔓

Creating user:
/api/user/register/

Getting access token:
/api/user/token/

Logout: /api/user/logout

## Features ⭐
JWT authentication (with logout function)
- Admin panel via /admin/
- Documentation via /api/doc/swagger/
- Extended profile system for users
- Likes, comments, messages and following system
- CRUD operations for posts, comments, events and messages
- Upload media to post and user profile
- Retrieving posts by title, content and author
- Scheduled post creation
- Auto superuser creation on first launch