# Docker

App itself is started with [entrypoint.sh](./entrypoint.sh) where it checks whether database and code are in sync.
There is a `migrate` argument which triggers an alembic upgrade to the newest version.
This is used for testing, or to upgrade a fesh database to the current schema.
I edited alembics environment to accept `SQLALCHEMY_DATABASE_URI`.

## Test Stack

The test stack is defined in [docker-compose-test.yml](./docker-compose-test.yml).
Run it from CICD pipeline or locally:

```
sudo docker-compose -f docker/docker-compose-test.yml build
sudo docker-compose \
    -f docker/docker-compose-test.yml \
    up \
    --exit-code-from test
```
