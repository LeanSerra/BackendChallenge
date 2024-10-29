# Backend Challenge

A web scraping and data storage service using FastAPI, SQLModel, and PostgreSQL to extract product data from various supermarket websites and store it in a database.

### Prerequisites

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

### Steps

1. **Clone the Repository**

   Clone the repository to your local machine:

   ```bash
   git clone https://github.com/LeanSerra/BackendChallenge.git
   cd BackendChallenge

2. **Create a .env file**

    Create a .env file in the root directory and provide a PostgreSQL connection string
    ```
    DATABASE_URL=postgresql://postgres:password@postgres:5432/
    ```

3. **Make entrypoint.sh executable**

    ```bash
    chmod +x entrypoint.sh
    ```

4. **Start Docker containers**

    ```bash
    docker compose up
    ```

5. **(Optional) Preload the db with common keywords**

    ```bash
    chmod +x populate_db.sh
    ./populate_db.sh
    ```

6. **(Optional) Run tests**

    ```bash
    pytest
    ```

### Usage
- After deployment, the API can be accessed locally at ``http://localhost:8000``.
- Swagger documentation is available at ``http://localhost:8000/docs``
