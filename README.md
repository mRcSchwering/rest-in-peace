# rest-in-peace

A REST joke

```
sudo docker run \
    --rm \
    -e "POSTGRES_HOST_AUTH_METHOD=trust" \
    -e "POSTGRES_DB=main" \
    -e "POSTGRES_USER=postgres" \
    -p "5432:5432" \
    postgres:12-alpine
```

Start app (the first time `migrate` is needed to migrate the empty database):

```
alembic upgrade head  # migrate db schema
python -m tests.conftest  # reset testdata
python alembic/test_alembic.py  # test whether code and db are in sync
uvicorn --host 0.0.0.0 --reload app.app:app  # start devel server
```
