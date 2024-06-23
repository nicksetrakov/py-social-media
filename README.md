# social-meida

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