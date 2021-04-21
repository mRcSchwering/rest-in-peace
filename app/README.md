# App

Use `docker` to start a throw-away postgres server for development.

```
sudo docker run \
    --rm \
    -e "POSTGRES_HOST_AUTH_METHOD=trust" \
    -e "POSTGRES_DB=main" \
    -e "POSTGRES_USER=postgres" \
    -p "5432:5432" \
    postgres:12-alpine
```

Use `alembic` to migrate the (still empty) database to the newest version.
This will fill the database with tables, indexes, and so on.
Then, add some test data and start the ASGI app using `uvicorn`.

```
alembic upgrade head  # migrate db schema
python -m tests.conftest  # reset testdata
uvicorn --reload app.main:app  # start dev server
```

[main.py](./main.py) is the entrypoint, the GraphQL schema and resolvers are under [api/](./api), the CRUD functions and database models under [db/](./db).
[config.py](./config.py) is the main configuration file.
Every variable can be overridden during runtime by providing environment variables.
Notably, the `SQLALCHEMY_DATABASE_URI` and `AUTH_SECRET_KEY` would have to be adapted for deployment.
[auth.py](./auth.py) contains the authentication logic. I am using JWT Baerer tokens as authentication.
