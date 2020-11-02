# Docker

App itself is started with [entrypoint.sh](./entrypoint.sh) where it checks whether database and code are in sync.
There is a `migrate` argument which triggers an alembic upgrade to the newest version.
This is used for testing to upgrade a fesh database to current schema.
I edited alembics environment to accept `SQLALCHEMY_DATABASE_URI`.

## Test Stack

The test stack is defined in [docker-compose-test.yml](./docker-compose-test.yml).
Currently both _app_ and _test_ use the same image.
It's executed by [.gitlab-ci.yml](../.gitlab-ci.yml).
Test it locally:

```
sudo docker-compose -f docker/docker-compose-test.yml build
sudo docker-compose \
    -f docker/docker-compose-test.yml \
    up \
    --exit-code-from test
```
