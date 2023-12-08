## Run the application
You must have docker compose installed. Then enter the following command:

    docker compose up --build
When you see

    dailymotiontest-server-1  | INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)

you can access the application at http://localhost:8000/sign_up

You can see the OpenApi at http://localhost:8000/docs

## Run the tests
**Warning**: these are non-functional drafts

    docker compose run server pytest .

## Architecture schema

```
|-- Dailymotion test
|   |-- app
|   |   |-- static
|   |   |   |-- css
|   |   |   |   |-- materialize.css
|   |   |   |   `-- materialize.min.js
|   |   |   |-- js
|   |   |   |   |-- materialize.js
|   |   |   |   `-- materialize.min.js
|   |   |-- templates
|   |   |   |   |-- code_verification.html
|   |   |   |   `-- sign_up.html
|   |   |-- db.py (connection to the database)
|   |   |-- main.py
|   |   |-- schemas.py (user schema with pydantic)
|   |   `-- tests.py (pytest)
|   |-- .env
|   |-- compose.yaml 
|   |-- Dockerfile
|   |-- init.sql (creation of tables in database)
|   |-- readme.md
|   `-- requirements.txt
```
## Database schema

### User Table

| Column| Type |
| -- | -- |
|id| UUID |
| email | char |
| password| char |
| is_valid| boolean |
| created_at| timestamp |
| updated_at| timestamp |

*updated_at* automatically updated with a trigger function.

*id* is primary key

### 2fa_code Table

| Column| Type |
| -- | -- |
|id| UUID |
| code| smallint|
| user_id| UUID|
| created_at| timestamp |

Relation to User table with *user_id*

*id* is primary key
