# Tests

For local test suite start server with database server, then run pytest.

```
sudo docker run \
    --rm \
    -e "POSTGRES_HOST_AUTH_METHOD=trust" \
    -e "POSTGRES_DB=main" \
    -e "POSTGRES_USER=postgres" \
    -p "5432:5432" \
    postgres:12-alpine
...
alembic upgrade head  # migrate db schema
...
uvicorn --host 0.0.0.0 --reload app.app:app  # start devel server
...
pytest tests/
```
